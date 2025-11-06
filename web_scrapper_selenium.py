import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

def getScrappedData(url: str):
    driver = webdriver.Chrome()
    driver.get(url)
    driver.implicitly_wait(1)

    with open('result.html', "w") as f:
        f.write(driver.page_source)
    return None
if __name__ == '__main__':
    url = sys.argv[1]
    getScrappedData(url)