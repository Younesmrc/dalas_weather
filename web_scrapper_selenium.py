import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import datetime
import requests
from bs4 import BeautifulSoup
import csv
import os.path

def getScrappedData(cityName, timeOfDay: datetime.datetime):
    # url = f'https://www.wunderground.com/history/daily/fr/{cityName}/date/{timeOfDay.year}2025-11-17'
    url = f'https://www.wunderground.com/history/daily/fr/{cityName}/date/{timeOfDay.year}-{timeOfDay.month}-{timeOfDay.day}'
    hour = timeOfDay.hour

    driver = webdriver.Chrome()
    driver.get(url)
    driver.implicitly_wait(1)

    htmlSource = driver.page_source   
    html_soup: BeautifulSoup = BeautifulSoup(htmlSource, 'html.parser')
    # print(html_soup.prettify()) 
    # print(html_soup.find_all(class_='summary-table'))
    summaryTable = html_soup.find(class_='summary-table')
    # print(summaryTable.find_all("table"))

    DailyObservationsTable = html_soup.find(class_='observation-table')
    # temperatureLine = DailyObservationsTable.find_all('tbody')[0].find_all('tr')[0].find_all('td')[0]
    temperatureLine = DailyObservationsTable.find_all('tr')[hour].find_all('td')[1].find(class_='wu-value-to')
    perspirationLine = DailyObservationsTable.find_all('tr')[hour].find_all('td')[8].find(class_='wu-value-to')
    windLine = DailyObservationsTable.find_all('tr')[hour].find_all('td')[5].find(class_='wu-value-to')
    pressure = DailyObservationsTable.find_all('tr')[hour].find_all('td')[7].find(class_='wu-value-to')
    visibilityLine = summaryTable.find("table").find_all('tbody')[3].find_all('tr')[1].find_all('td')[0]
    # visibilityLine = DailyObservationsTable.find_all('tr')[hour].find_all('td')[5]
    # perspirationLine = DailyObservationsTable.find("table").find_all('tbody')[1].find_all('tr')[0].find_all('td')[0]
    # windLine = DailyObservationsTable.find("table").find_all('tbody')[3].find_all('tr')[0].find_all('td')[0]

    print((float(temperatureLine.get_text()) - 32) * (5.0/9.0))
    print(perspirationLine.get_text())
    print(windLine.get_text())
    print(float(pressure.get_text()) * pow(10, -5))
    print(visibilityLine.get_text())
    return {
        'temperature': (float(temperatureLine.get_text()) - 32) * (5.0/9.0),
        'perspitation': float(perspirationLine.get_text()),
        'wind_line': float(windLine.get_text()),
        'pressure': float(pressure.get_text()) * pow(10, -5),
        'visibility': visibilityLine.get_text()
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
        fieldNames = ['date','temperature', 'perspitation', 'wind', 'pressure', 'visibility']
        writer = csv.DictWriter(csvfile, fieldnames=fieldNames)
        # is_header = not any(cell.isdigit() for cell in csv_table[0])
        # sniffer = csv.Sniffer()
        # has_header = sniffer.has_header(csvfile.read(2048))
        if(not has_header):
            writer.writeheader()
        writer.writerow({'date': time, 'temperature': scrappedData['temperature'], 'perspitation': scrappedData['perspitation'], 'wind': scrappedData['wind_line'], 'pressure': scrappedData['pressure'], 'visibility': scrappedData['visibility']})
        return None

if __name__ == '__main__':
    latitude = sys.argv[1]
    longitude = sys.argv[2]
    timeOfDay = sys.argv[3]
    cityName = getCityNameFromCoordinates(latitude=latitude, longitude=longitude)
    scrappedData = getScrappedData(cityName, datetime.datetime.fromisoformat(timeOfDay))
    writeToCSV(scrappedData, datetime.datetime.fromisoformat(timeOfDay))
    