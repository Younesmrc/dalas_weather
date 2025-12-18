import sys
import csv
import threading
import os.path
from datetime import datetime
import web_scrapper_selenium
# accidents_2022_2023_meteo.csv

def run(lowerBound: int, upperBound: int, csvFileName: str):
    with open(csvFileName, 'r', newline='') as csvFile:
        reader = csv.DictReader(csvFile)
        rows = list(reader)

        for i in range(lowerBound, min(upperBound + 1, len(rows))):
            row = rows[i]
            print(row)
            lat = row["lat"]
            lon = row["long"]
            # time = row["time"]
            # day =
            # month
            # year
            # hour
            fullDate = datetime.strptime(row['date'], '%Y-%m-%d')
            fullDateFormated = fullDate.isoformat()
            id = row['Num_Acc']

            web_scrapper_selenium.run(lat, lon, fullDateFormated, id, f'{lowerBound}_{upperBound}')
            print(f'Done loop {i}')


if __name__ == '__main__':
    lowerBound = int(sys.argv[1])
    upperBound = int(sys.argv[2])
    fileName = sys.argv[3]
    print(lowerBound)
    print(upperBound)
    print(fileName)
    run(lowerBound, upperBound, fileName)
    # csvFile = openCSVFile(fileName)
