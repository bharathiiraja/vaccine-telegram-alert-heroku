import collections
import os
from datetime import date, datetime
import time
import requests
#import logging

#logging.basicConfig(format='%(asctime)s :: %(levelname)s :: %(funcName)s :: %(lineno)d : %(message)s',level=logging.INFO, filename='logs/cowin.log', filemode='w')

currentDate = date.today().strftime("%d-%m-%Y")

currentList = []
currDict = {}
prevDict = {}

def slot_availability(districtId, chatId):
    dateTime = datetime.now()
    print('Searching for Slot Availability....' + str(districtId) + ' ---> Time: ' + str(
        dateTime.strftime("%d/%m/%Y %H:%M:%S")))
    COWIN_REQUEST_URL = os.environ.get('COWIN_BASE_URL') + '/appointment/sessions/public/calendarByDistrict?district_id=' + str(
        districtId) + '&date=' + currentDate
    headers = {'User-Agent': os.environ.get('USER_AGENT')}
    resultJson = ''

    try:
        result = requests.get(COWIN_REQUEST_URL, headers=headers)
        resultJson = result.json()
    except requests.exceptions.RequestException as e:
        print("Exception accessing COWIN API..Retrying..")

    if len(resultJson) > 0:
        slotAvailableList18 = []
        slotAvailableList45 = []
        for center in resultJson["centers"]:
            for s in center["sessions"]:
                if s["min_age_limit"] == 18 and s["available_capacity"] > 0 and s['available_capacity_dose1'] > 0:
                    slotCenter_18 = str(s['min_age_limit']) + "%2B Vaccine Available:" "\nDate: " + s['date'] + \
                                    "\nAddress: " + center['name'] + ", " + center['block_name'] + ", " + center[
                                        'district_name'] + \
                                    ", " + str(center['pincode']) + "\nVaccine: " + s['vaccine'] + \
                                    "\nAvailable Dose-1 Count: " + str(s['available_capacity_dose1'])
                    currentList.append(s['session_id'])
                    currDict[districtId] = currentList
                    slotAvailableList18.append(slotCenter_18)

        if len(slotAvailableList18) > 0:
            # To avoid repeating the same msgs in to group for each interval
            if compare_identical_list(currDict.get(districtId), prevDict.get(districtId)):
                for msg in slotAvailableList18:
                    try:
                        prevDict[districtId] = currDict.get(districtId)[:]
                        send_telegram_msg(msg, chatId)
                    except requests.exceptions.RequestException as e:
                        print("Connection refused by the telegram server..Let me sleep for 5 seconds")
                        time.sleep(5)
                        # clearing specific district value to resend the message in next iteration if any telegram connection error in previous iteration
                        del prevDict[districtId]
                        continue
            currDict.clear()
            currentList.clear()


def compare_identical_list(x, y):
    return collections.Counter(x) != collections.Counter(y)  # If two list is not match return true


def send_telegram_msg(message, chatId):
    base_url = os.environ.get('TELEGRAM_BASE_URL') + os.environ.get('TELEGRAM_TOKEN') + '/sendMessage?chat_id={0}&text={1}'.format(chatId,
                                                                                                             message)
    response = requests.get(base_url)
    print("Response from Telegram:", response)
    if response.status_code == 200:
        print("Sent Messages to Telegram !")
    else:
        print("Invalid Telegram Chat Id: " + str(chatId))
        #logging.error("Invalid Telegram Chat Id: " + str(chatId) + "~Response Code:" + str(response))


def run_all_districts():
    slot_availability(571, os.environ.get('CHAT_ID_CHENNAI'))  # Chennai
    time.sleep(5)  # sleep for telegram rate limiting
    slot_availability(572, os.environ.get('CHAT_ID_THIRUVALLUR'))  # Thiruvallur
    time.sleep(5)
    slot_availability(565, os.environ.get('CHAT_ID_CHENGALPET'))  # Chengalpet
    time.sleep(5)
    slot_availability(557, os.environ.get('CHAT_ID_KANCHIPURAM'))  # Kanchipuram
    time.sleep(5)
    slot_availability(265, os.environ.get('CHAT_ID_BANGALORE_URBAN'))  # Karnataka / Bangalore Urban
    time.sleep(5)
    slot_availability(294, os.environ.get('CHAT_ID_BBMP'))  # Karnataka / Bangalore BBMP
    time.sleep(5)
    slot_availability(776, os.environ.get('CHAT_ID_SURAT_CORP'))  # Gujarat / Surat Corp
    time.sleep(5)
    slot_availability(562, os.environ.get('CHAT_ID_KRISHNAGIRI'))  # Krishnagiri
    time.sleep(5)
    slot_availability(539, os.environ.get('CHAT_ID_COIMBATORE'))  # Coimbatore
    time.sleep(5)
    slot_availability(568, os.environ.get('CHAT_ID_TIRUPPUR'))  # Tiruppur
    time.sleep(5)
    slot_availability(268, os.environ.get('CHAT_ID_CHITRADURGA'))  # Karnataka / Chitradurga
    time.sleep(5)
    slot_availability(547, os.environ.get('CHAT_ID_CUDDALORE'))  # Cuddalore


if __name__ == '__main__':
    while True:
        run_all_districts()
        print('Sleeping for 15 secs !')
        time.sleep(15)
