import os
import time

from seleniumbase import SB
from dotenv import load_dotenv

load_dotenv()


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
                
            else:
                print("Appointments available")

            sb.click('//*[@id="dataTableServices"]/tbody/tr[2]/td[4]/a')
            message = sb.wait_for_element('/html/body/div[2]/div[2]/div/div/div/div/div/div')
            if 'All appointments for this service are currently booked' in message.text:
                print("No appointments available")
            else:
                print("Appointments available")

        except Exception as e:
            print(e)

        time.sleep(int(os.environ.get("REFRESH_RATE", 60)))

    breakpoint()