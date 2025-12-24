import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import datetime
import requests
from bs4 import BeautifulSoup
import csv
from selenium.webdriver.chrome.options import Options
import os.path
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# import undetected_chromedriver as uc
import re

API_KEY='bdc_3f00dbcc437e48e2be3dd32756eb5577'

def to_float(text: str) -> float:
    match = re.search(r"-?\d+(?:\.\d+)?", text)
    if not match:
        raise ValueError(f"No numeric value found in: {text}")
    return float(match.group())

def getScrappedData(cityName, timeOfDay: datetime.datetime):
    url = f"https://www.wunderground.com/history/daily/fr/{cityName}/date/{timeOfDay.year}-{timeOfDay.month}-{timeOfDay.day}"
    hour = timeOfDay.hour

    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options )
    wait = WebDriverWait(driver, 10)
    try:
        print(url)
        driver.get(url)

        # Wait until hourly rows exist in live DOM
        rows = wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, ".observation-table tbody tr")
            )
        )

        row = rows[hour]

        cells = row.find_elements(By.TAG_NAME, "td")

        # second_rows = wait.until(
        #     EC.presence_of_all_elements_located(
        #         (By.CSS_SELECTOR, ".summary-table tbody tr")
        #     )
        # )

        temperature = cells[1].get_attribute("textContent").strip()
        dew_point = cells[2].get_attribute("textContent").strip()
        humidity = cells[3].get_attribute("textContent").strip()
        wind = cells[4].get_attribute("textContent").strip()
        wind_speed = cells[5].get_attribute("textContent").strip()
        wind_gust = cells[6].get_attribute("textContent").strip()
        pressure = cells[7].get_attribute("textContent").strip()
        precipitation = cells[8].get_attribute("textContent").strip()
        condition = cells[9].get_attribute("textContent").strip()
        # visibility = re.findall(
        #     r"\d+", second_rows[9].get_attribute("textContent").strip()
        # )[0]

        second_rows = driver.find_elements(By.CSS_SELECTOR, ".summary-table tbody tr")

        if second_rows:
            # safely extract visibility
            visibility_text = second_rows[9].get_attribute("textContent").strip() if len(second_rows) > 9 else None
            numbers = re.findall(r"\d+", visibility_text) if visibility_text else []
            visibility = numbers[0] if numbers else None
        else:
            visibility = None

        driver.quit()

        return {
            "temperature": (to_float(temperature) - 32) * 5 / 9,
            "dew_point": (to_float(dew_point) - 32) * 5 / 9,
            "humidity": to_float(humidity),
            "wind": wind,
            "wind_speed": to_float(wind_speed),
            "wind_gust": to_float(wind_gust),
            "pressure": to_float(pressure) * 1e-5,
            "perspitation": to_float(precipitation),
            "condition": condition,
            "visibility": visibility,
        }
    except:
        driver.quit()
        return {
            "temperature": 'inconnu',
            "dew_point": 'inconnu',
            "humidity": 'inconnu',
            "wind": 'inconnu',
            "wind_speed": 'inconnu',
            "wind_gust": 'inconnu',
            "pressure": 'inconnu',
            "perspitation": 'inconnu',
            "condition": 'inconnu',
            "visibility": 'inconnu',
        }
def getCityNameFromCoordinates(latitude, longitude):
    url = f'http://api.3geonames.org/{latitude},{longitude}.json'
    response = requests.get(url)
    responseJSON = None
    try:
        responseJSON = response.json()
    except:
        print('exception')
        return
    return responseJSON['nearest']['city']

def getCityNameFromCoordinatesBDC(latitude, longitude):
    url = f'https://api-bdc.net/data/reverse-geocode?latitude={latitude}&longitude={longitude}&key={API_KEY}'
    response = requests.get(url)
    responseJSON = None
    try:
        responseJSON = response.json()
    except:
        print('exception')
        return
    print(responseJSON)
    print(responseJSON['city'])
    return responseJSON['city']

def writeToCSV(scrappedData, time, id, filename):
    has_header = os.path.isfile(f'{filename}.csv')
    with open (f'{filename}.csv', 'a+', newline='') as csvfile:
        fieldNames = ['Num_Acc','date','temperature', 'dew_point', 'humidity', 'perspitation', 'wind', 'wind_speed', 'wind_gust', 'pressure', 'visibility', 'condition']
        writer = csv.DictWriter(csvfile, fieldnames=fieldNames)
        if(not has_header):
            writer.writeheader()
        writer.writerow({'Num_Acc': id,'date': time, 'temperature': scrappedData['temperature'], 'dew_point': scrappedData['dew_point'], 'perspitation': scrappedData['perspitation'], 'wind': scrappedData['wind'], 'wind_gust': scrappedData['wind_gust'], 'wind_speed': scrappedData['wind_speed'], 'pressure': scrappedData['pressure'], 'visibility': scrappedData['visibility'],'condition': scrappedData['condition']})
        return None

def run(latitude: str, longitude: str, timeofDay:str, id:str, filename: str):
    cityName = getCityNameFromCoordinatesBDC(latitude=latitude, longitude=longitude)
    # scrappedData = getScrappedData(cityName, datetime.datetime.fromisoformat(timeofDay))
    # writeToCSV(scrappedData, datetime.datetime.fromisoformat(timeofDay), id, filename)
    return getScrappedData(cityName, datetime.datetime.fromisoformat(timeofDay))
    