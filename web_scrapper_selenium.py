import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import datetime
import requests
from bs4 import BeautifulSoup
import csv
import os.path

def getScrappedData(cityName, timeOfDay: datetime.datetime):
    url = f'https://www.wunderground.com/history/daily/fr/{cityName}/date/{timeOfDay.year}-{timeOfDay.month}-{timeOfDay.day}'
    hour = timeOfDay.hour

    driver = webdriver.Chrome()
    driver.get(url)
    driver.implicitly_wait(1)

    htmlSource = driver.page_source   
    html_soup: BeautifulSoup = BeautifulSoup(htmlSource, 'html.parser')
    summaryTable = html_soup.find(class_='summary-table')

    DailyObservationsTable = html_soup.find(class_='observation-table')
    print(DailyObservationsTable.prettify())
    temperatureLine = DailyObservationsTable.find_all('tr')[hour].find_all('td')[1].find(class_='wu-value-to')
    dewPointLine = DailyObservationsTable.find_all('tr')[hour].find_all('td')[2].find(class_='wu-value-to')
    humidityLine = DailyObservationsTable.find_all('tr')[hour].find_all('td')[3].find(class_='wu-value-to')
    windLine = DailyObservationsTable.find_all('tr')[hour].find_all('td')[4].find('span')
    windSpeedLine = DailyObservationsTable.find_all('tr')[hour].find_all('td')[5].find(class_='wu-value-to')
    windGustLine = DailyObservationsTable.find_all('tr')[hour].find_all('td')[6].find(class_='wu-value-to')
    pressure = DailyObservationsTable.find_all('tr')[hour].find_all('td')[7].find(class_='wu-value-to')
    perspirationLine = DailyObservationsTable.find_all('tr')[hour].find_all('td')[8].find(class_='wu-value-to')
    conditionLine = DailyObservationsTable.find_all('tr')[hour].find_all('td')[9].find('span')

    visibilityLine = summaryTable.find("table").find_all('tbody')[3].find_all('tr')[1].find_all('td')[0]

    return {
        'temperature': (float(temperatureLine.get_text()) - 32) * (5.0/9.0),
        'dew_point': (float(dewPointLine.get_text()) - 32) * (5.0/9.0),
        'humidity': (float(humidityLine.get_text())),
        'perspitation': float(perspirationLine.get_text()),
        'wind': windLine.get_text(),
        'wind_speed': float(windSpeedLine.getText()),
        'wind_gust': float(windGustLine.get_text()),
        'pressure': float(pressure.get_text()) * pow(10, -5),
        'visibility': visibilityLine.get_text(),
        'condition': conditionLine.get_text()
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
    print(responseJSON)
    print(responseJSON['nearest']['city'])
    return responseJSON['nearest']['city']

def writeToCSV(scrappedData, time):
    has_header = os.path.isfile('test.csv')
    with open ('test.csv', 'a+', newline='') as csvfile:
        fieldNames = ['date','temperature', 'dew_point', 'humidity', 'perspitation', 'wind', 'wind_speed', 'wind_gust', 'pressure', 'visibility', 'condition']
        writer = csv.DictWriter(csvfile, fieldnames=fieldNames)
        if(not has_header):
            writer.writeheader()
        writer.writerow({'date': time, 'temperature': scrappedData['temperature'], 'dew_point': scrappedData['dew_point'], 'perspitation': scrappedData['perspitation'], 'wind': scrappedData['wind'], 'wind_gust': scrappedData['wind_gust'], 'wind_speed': scrappedData['wind_speed'], 'pressure': scrappedData['pressure'], 'visibility': scrappedData['visibility'],'condition': scrappedData['condition']})
        return None

if __name__ == '__main__':
    latitude = sys.argv[1]
    longitude = sys.argv[2]
    timeOfDay = sys.argv[3]
    cityName = getCityNameFromCoordinates(latitude=latitude, longitude=longitude)
    scrappedData = getScrappedData(cityName, datetime.datetime.fromisoformat(timeOfDay))
    writeToCSV(scrappedData, datetime.datetime.fromisoformat(timeOfDay))
    