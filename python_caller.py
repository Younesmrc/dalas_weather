import sys
import csv
import threading
import os.path
from datetime import datetime
from zoneinfo import ZoneInfo
import web_scrapper_selenium
from queue import Queue

result_queue = Queue(maxsize=100)  # prevents memory explosion
# accidents_2022_2023_meteo.csv

def run(lowerBound: int, upperBound: int, csvFileName: str):
    with open(csvFileName, 'r') as csvFile:
        reader = csv.DictReader(csvFile, delimiter=';')
        rows = list(reader)

        threads = []

        resultFileName = f'{lowerBound}-{min(upperBound, len(rows))}.csv'

        writer_thread = threading.Thread(target=writeToCSV, daemon=True, args=(resultFileName, ))
        writer_thread.start()


        for i in range(lowerBound, min(upperBound + 1, len(rows))):
            t = threading.Thread(target=worker,args=(rows[i],))
            threads.append(t)
            t.start()

            while threading.active_count() > 5:
                pass

            
        for t in threads:
            t.join()

        result_queue.put(None)
        writer_thread.join()
        

def worker(row):
    lat = row["lat"]
    lon = row["long"]
    hour = row['hrmn']
    date = f'{row['an']}-{row['mois']}-{row['jour']}'
    fullDate = f'{date} {hour}'
    fullDateFormated = datetime.strptime(fullDate, '%Y-%m-%d %H:%M').replace(tzinfo=ZoneInfo("Europe/Paris")).isoformat()
    id = row['Num_Acc']

    result = web_scrapper_selenium.run(lat, lon, fullDateFormated, id, f'{lowerBound}_{upperBound}')
    if(result):
        result_queue.put({'result': result, 'date': fullDateFormated, "id": id})

def writeToCSV(fileName):
    written = 0
    has_header = os.path.isfile(f'{fileName}')
    with open (f'{fileName}.csv', 'a+', newline='') as csvfile:
        fieldNames = ['Num_Acc','date','temperature', 'dew_point', 'humidity', 'perspitation', 'wind', 'wind_speed', 'wind_gust', 'pressure', 'visibility', 'condition']
        writer = csv.DictWriter(csvfile, fieldnames=fieldNames)
        if(not has_header):
            writer.writeheader()
        while True:
            item = result_queue.get()
            if item is None:
                break
            writer.writerow({'Num_Acc': item['id'],'date': item['date'], 'temperature': item['result']['temperature'], 'dew_point': item['result']['dew_point'], 'perspitation': item['result']['perspitation'], 'wind': item['result']['wind'], 'wind_gust': item['result']['wind_gust'], 'wind_speed': item['result']['wind_speed'], 'pressure': item['result']['pressure'], 'visibility': item['result']['visibility'],'condition': item['result']['condition']})
            result_queue.task_done()
            written +=1
            print(f'Queue number {written}')
        return None

if __name__ == '__main__':
    lowerBound = int(sys.argv[1])
    upperBound = int(sys.argv[2])
    fileName = sys.argv[3]
    run(lowerBound, upperBound, fileName)
    # csvFile = openCSVFile(fileName)
