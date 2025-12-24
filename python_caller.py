import sys
import csv
import threading
import os.path
from datetime import datetime
from zoneinfo import ZoneInfo
import web_scrapper_selenium
# accidents_2022_2023_meteo.csv

def run(lowerBound: int, upperBound: int, csvFileName: str):
    with open(csvFileName, 'r') as csvFile:
        reader = csv.DictReader(csvFile, delimiter=';')
        rows = list(reader)

        # threads = []
        # results = []

        for i in range(lowerBound, min(upperBound + 1, len(rows))):
            row = rows[i]
            print(row)
            lat = row["lat"]
            lon = row["long"]
            hour = row['hrmn']
            date = f'{row['an']}-{row['mois']}-{row['jour']}'
            fullDate = f'{date} {hour}'
            fullDateFormated = datetime.strptime(fullDate, '%Y-%m-%d %H:%M').replace(tzinfo=ZoneInfo("Europe/Paris")).isoformat()
            id = row['Num_Acc']

            web_scrapper_selenium.run(lat, lon, fullDateFormated, id, f'{lowerBound}_{upperBound}')
            print(f'Done loop {i}')


if __name__ == '__main__':
    lowerBound = int(sys.argv[1])
    upperBound = int(sys.argv[2])
    fileName = sys.argv[3]
    run(lowerBound, upperBound, fileName)
    # csvFile = openCSVFile(fileName)
