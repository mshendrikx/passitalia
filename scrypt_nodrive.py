import os
import time
import logging
import asyncio

from datetime import datetime
import nodriver as uc
from whatsapp_api import whatsapp_send_message, whatsapp_get_numberid

WHATSAPP_BASE_URL = os.environ.get("WHATSAPP_BASE_URL")
WHATSAPP_API_KEY = os.environ.get("WHATSAPP_API_KEY")
WHATSAPP_SESSION = os.environ.get("WHATSAPP_SESSION")
WHATSAPP_NUMBER = os.environ.get("WHATSAPP_NUMBER")
ATTEMPTS = int(os.environ.get("ATTEMPTS", 5))
START_MINUTE = int(os.environ.get("START_MINUTE", 59))
BROWSER_EXECUTABLE_PATH = os.environ.get("BROWSER_EXECUTABLE_PATH") or os.environ.get("CHROME_BIN")
TEST_EXEC = os.environ.get("TEST", "false").lower() in ("1", "true", "yes")
LOG_FILE_PATH = "./logs/passitalia.log"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", filename=LOG_FILE_PATH, filemode="a")
logger = logging.getLogger(__name__)

def active_login():
    
    if TEST_EXEC:
        return True
    
    if START_MINUTE == 0:
        start_login = 58
    elif START_MINUTE == 1:
        start_login = 59
    else:
        start_login = START_MINUTE - 2

    now = datetime.now()

    if now.minute == start_login:
        return True
    else:   
        return False
    
def active_attempts():

    if TEST_EXEC:
        return True

    if START_MINUTE == 0:
        start_login = 59
    else:
        start_login = START_MINUTE - 1

    now = datetime.now()
    if now.minute == start_login and now.second > 57:
        return True
    else:   
        return False

async def click_selector(tab, selector, timeout=10):
    element = await tab.select(selector, timeout=timeout)
    if element is None:
        raise TimeoutError(f"Element not found: {selector}")
    await element.click()
    return element


async def type_selector(tab, selector, value, timeout=10):
    element = await tab.select(selector, timeout=timeout)
    if element is None:
        raise TimeoutError(f"Element not found: {selector}")
    await element.clear_input()
    await element.send_keys(value or "")
    return element


async def raise_if_bot_challenge(tab):
    content = await tab.get_content()
    content_lower = content.lower()
    if "radware bot manager captcha" in content_lower or "captcha" in content_lower:
        raise RuntimeError("Bot challenge detected before login")


async def login_prenotami(tab):
    login = False
    while login == False:
        try:
            await tab.get("https://prenotami.esteri.it/")
            await tab.sleep(3)
            #await raise_if_bot_challenge(tab)
            await click_selector(tab, "#pingid-button")
            await type_selector(tab, 'input[id="floatingLabelInput33"]', os.environ.get("EMAIL"))
            await type_selector(tab, 'input[id="floatingLabelInput38"]', os.environ.get("PASSWORD"))
            await click_selector(tab, "#wrapper > div:nth-of-type(3) > button")
            await click_selector(tab, "body > header > nav:first-of-type > div > div > a:nth-of-type(2)")
            logger.info("Successfully logged in")
            print("Successfully logged in")
            login = True
        except Exception as e:
            logger.error("Error during login: %s", e)
            print("Error during login: %s" % e)
            if "Bot challenge detected" in str(e):
                await asyncio.sleep(30)


async def check_booking(tab, service_id, contacts, content):
    try:
        await tab.get(f"https://prenotami.esteri.it/Services/Booking/{service_id}")
        element = await tab.select("#typeofbookingddl", timeout=10)
        if element is None:
            raise TimeoutError("typeofbookingddl not found")

        whatsapp_send_message(
            base_url=WHATSAPP_BASE_URL,
            api_key=WHATSAPP_API_KEY,
            session=WHATSAPP_SESSION,
            contacts=contacts,
            content=content,
            content_type="string",
        )

        logger.info("Appointments %s available", service_id)
        print("Appointments %s available" % service_id)
        return True
    except Exception as e:
        logger.error("Error occurred: %s", e)
        print("Error occurred: %s" % e)
        logger.info("No Appointments %s available", service_id)
        print("No Appointments %s available" % service_id)
        return False


async def run_browser_window(contacts, content):
    
    browser_options = {"headless": False}
    if BROWSER_EXECUTABLE_PATH:
        browser_options["browser_executable_path"] = BROWSER_EXECUTABLE_PATH

    browser = await uc.start(**browser_options)
    
    try:
        tab = await browser.get("about:blank")

        print("Nodriver initialized successfully")
        logger.info("Nodriver initialized successfully")

        await login_prenotami(tab)

        while not active_attempts():
            await tab.sleep(1)

        found_2391 = False
        found_4784 = False
        attempts = 0

        while attempts < ATTEMPTS:
            attempts += 1

            found_2391 = await check_booking(tab, "2391", contacts, content)
            found_4784 = await check_booking(tab, "4784", contacts, content)

            if found_2391 or found_4784:
                break
            
            time.sleep(3)  # Wait a bit before the next attempt
            
    finally:
        browser.stop()


print("Starting Nodriver script")
logger.info("Starting Nodriver script")

whatsapp_id = None
while whatsapp_id is None:
    try:
        whatsapp_id = whatsapp_get_numberid(
            base_url=WHATSAPP_BASE_URL,
            api_key=WHATSAPP_API_KEY,
            session=WHATSAPP_SESSION,
            contact=WHATSAPP_NUMBER,
        )
        if whatsapp_id is None:
            logger.error("Error retrieving whatsapp number id")
            time.sleep(60)
    except Exception as e:
        logger.error("Error retrieving whatsapp number id: %s", e)
        time.sleep(60)
contacts = [whatsapp_id]
content = "Agendamento disponível! Acesse https://prenotami.esteri.it/ para marcar seu horário."
logger.info("Successfully retrieved whatsapp number id")
print("Successfully retrieved whatsapp number id")

while 1 == 1:

    if active_login():
        uc.loop().run_until_complete(run_browser_window(contacts, content))
                    
        logger.info("Waiting next window")
        print("Waiting next window")
        time.sleep(60)
        
    
