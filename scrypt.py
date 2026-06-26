import os
import time
import random
import logging

from datetime import datetime
from seleniumbase import SB
from whatsapp_api import whatsapp_send_message, whatsapp_get_numberid

WHATSAPP_BASE_URL = os.environ.get("WHATSAPP_BASE_URL")
WHATSAPP_API_KEY = os.environ.get("WHATSAPP_API_KEY")
WHATSAPP_SESSION = os.environ.get("WHATSAPP_SESSION")
WHATSAPP_NUMBER = os.environ.get("WHATSAPP_NUMBER")
SELENIUM_HUB_HOST = os.environ.get("SELENIUM_HUB_HOST", None)
SELENIUM_HUB_PORT = os.environ.get("SELENIUM_HUB_PORT", None)
ATTEMPTS = int(os.environ.get("ATTEMPTS", 5))
START_MINUTE = int(os.environ.get("START_MINUTE", 59))
LOG_FILE_PATH = "./logs/passitalia.log" 
NO_APPOINTMENTS_MESSAGE = "currently booked."

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", filename=LOG_FILE_PATH, filemode="a")
logger = logging.getLogger(__name__)

def active_login():
    
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

    if START_MINUTE == 0:
        start_login = 59
    else:
        start_login = START_MINUTE - 1

    now = datetime.now()
    if now.minute == start_login and now.second > 57:
        return True
    else:   
        return False

print("Starting SeleniumBase script")
logger.info("Starting SeleniumBase script")

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

        with SB(
            # browser="chrome",
            headless=True,
            uc=True,
            servername=SELENIUM_HUB_HOST,
            port=SELENIUM_HUB_PORT,
        ) as sb:
    
            print("SeleniumBase initialized successfully")
            logger.info("SeleniumBase initialized successfully")
    
            login = False
            while login == False:
                try:
                    sb.open("https://prenotami.esteri.it/")
                    sb.wait_for_element('//*[@id="pingid-button"]')
                    sb.click('//*[@id="pingid-button"]')
                    sb.wait_for_element('input[id="floatingLabelInput33"]')
                    sb.type('input[id="floatingLabelInput33"]', os.environ.get("EMAIL"))
                    sb.wait_for_element('input[id="floatingLabelInput38"]')
                    sb.type('input[id="floatingLabelInput38"]', os.environ.get("PASSWORD"))
                    sb.wait_for_element('//*[@id="wrapper"]/div[3]/button')
                    sb.click('//*[@id="wrapper"]/div[3]/button')
                    sb.wait_for_element("/html/body/header/nav[1]/div/div/a[2]")
                    sb.click("/html/body/header/nav[1]/div/div/a[2]")
                    logger.info("Successfully logged in")
                    print("Successfully logged in")
                    login = True
                except Exception as e:
                    logger.error("Error during login: %s", e)
                    print("Error during login: %s" % e)

            while not active_attempts():
                time.sleep(1)

            found_appointments = False
            attempts = 0            
            while attempts < ATTEMPTS:
                attempts += 1
                try:
                    sb.open("https://prenotami.esteri.it/Services/Booking/2391")
                    message = sb.wait_for_element(
                        "/html/body/div[2]/div[2]/div/div/div/div/div/div"
                    )
                    if NO_APPOINTMENTS_MESSAGE in message.text:
                        logger.info("No appointments 1 available")
                        print("No appointments 1 available")
    
                    else:
                        logger.info("Appointments 1 available")
                        print("Appointments 1 available")
                        whatsapp_send_message(
                            base_url=WHATSAPP_BASE_URL,
                            api_key=WHATSAPP_API_KEY,
                            session=WHATSAPP_SESSION,
                            contacts=contacts,
                            content=content,
                            content_type="string",
                        )
                        found_appointments = True
                        
                    time.sleep(2)
                    sb.open("https://prenotami.esteri.it/Services/Booking/4784")
                    message = sb.wait_for_element(
                        "/html/body/div[2]/div[2]/div/div/div/div/div/div"
                    )
                    if NO_APPOINTMENTS_MESSAGE in message.text:
                        logger.info("No appointments 2 available")
                        print("No appointments 2 available")
                    else:
                        logger.info("Appointments 2 available")
                        print("Appointments available")
                        whatsapp_send_message(
                            base_url=WHATSAPP_BASE_URL,
                            api_key=WHATSAPP_API_KEY,
                            session=WHATSAPP_SESSION,
                            contacts=contacts,
                            content=content,
                            content_type="string",
                        )
                        found_appointments = True
    
                except Exception as e:
                    logger.error("Error occurred: %s", e)
                    print("Error occurred: %s" % e)
                    
                if found_appointments:
                    break
                    
                time.sleep(2)

        logger.info("Waiting next window")
        print("Waiting next window")
        time.sleep(60)
        
    