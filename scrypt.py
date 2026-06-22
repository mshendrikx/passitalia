import os
import time
import random

from seleniumbase import SB
from whatsapp_api import whatsapp_send_message, whatsapp_get_numberid

WHATSAPP_BASE_URL = os.environ.get("WHATSAPP_BASE_URL")
WHATSAPP_API_KEY = os.environ.get("WHATSAPP_API_KEY")
WHATSAPP_SESSION = os.environ.get("WHATSAPP_SESSION")
WHATSAPP_NUMBER = os.environ.get("WHATSAPP_NUMBER")
REFRESH_RATE_MIN = int(os.environ.get("REFRESH_RATE_MIN", 60))
REFRESH_RATE_MAX = int(os.environ.get("REFRESH_RATE_MAX", 120))

whatsapp_id = whatsapp_get_numberid(
    base_url=WHATSAPP_BASE_URL,
    api_key=WHATSAPP_API_KEY,
    session=WHATSAPP_SESSION,
    contact=WHATSAPP_NUMBER,
    )

contacts = [whatsapp_id]
content = ("Agendamento disponível! Acesse https://prenotami.esteri.it/ para marcar seu horário.")

with SB(
    # browser="chrome",
    headless=True,
    uc=True,
#    servername=os.environ.get("SELENIUM_HUB_HOST", None),
#    port=os.environ.get("SELENIUM_HUB_PORT", None),
) as sb:
    
    try:
        sb.open("https://prenotami.esteri.it/")
        sb.click('/html/body/header/nav[1]/div/div/a[5]')
        sb.click('//*[@id="pingid-button"]')
        sb.type('input[id="floatingLabelInput33"]', os.environ.get("EMAIL"))
        sb.type('input[id="floatingLabelInput38"]', os.environ.get("PASSWORD"))
        sb.click('//*[@id="wrapper"]/div[3]/button')
        sb.click('/html/body/header/nav[1]/div/div/a[3]')
    except Exception as e:
        print('Error during login:', e)

    while 1 == 1:

        sb.click('//*[@id="advanced"]')

        try:
            sb.click('//*[@id="dataTableServices"]/tbody/tr[1]/td[4]/a')
            message = sb.wait_for_element('/html/body/div[2]/div[2]/div/div/div/div/div/div')
            if 'All appointments for this service are currently booked' in message.text:
                print("No appointments available")
                sb.click('/html/body/div[2]/div[2]/div/div/div/div/div/div/div/div[4]/button')
                
            else:
                print("Appointments available")
                whatsapp_send_message(
                    base_url=WHATSAPP_BASE_URL,
                    api_key=WHATSAPP_API_KEY,
                    session=WHATSAPP_SESSION,
                    contacts=contacts,
                    content=content,
                    content_type="string",
                )

            sb.click('//*[@id="dataTableServices"]/tbody/tr[2]/td[4]/a')
            message = sb.wait_for_element('/html/body/div[2]/div[2]/div/div/div/div/div/div')
            if 'All appointments for this service are currently booked' in message.text:
                print("No appointments available")
                sb.click('/html/body/div[2]/div[2]/div/div/div/div/div/div/div/div[4]/button')
            else:
                print("Appointments available")
                whatsapp_send_message(
                    base_url=WHATSAPP_BASE_URL,
                    api_key=WHATSAPP_API_KEY,
                    session=WHATSAPP_SESSION,
                    contacts=contacts,
                    content=content,
                    content_type="string",
                )

        except Exception as e:
            print(e)

        interval = random.randint(REFRESH_RATE_MIN, REFRESH_RATE_MAX)
        time.sleep(interval)