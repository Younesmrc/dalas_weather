import sys
import requests
from bs4 import BeautifulSoup

def debugWriteFile(text: str):
    with open('debug.log', 'w') as f:
        f.write(text)

def getScrappedData(url: str):
    print(url)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.text, 'html.parser')
    print('aria-labelledby="History observation"')
    debugWriteFile(soup.prettify(   ))
    # print(soup.prettify())
    # finder = soup.find('aria-labelledby="History observation"')
    finder = soup.find_all('table"')
    print(finder)
    return
if __name__ == '__main__':
    url = sys.argv[1]
    getScrappedData(url)