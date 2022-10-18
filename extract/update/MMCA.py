from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime

#driver = webdriver.Chrome(executable_path='C:\workspaces\workspace_crawling\drivers\chromedriver.exe')

options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
# 크롬 드라이버 경로 설정, 및 옵션 설정(옵션은 DevToolsActivePort를 찾을 수 없다는 에러 해결을 위해)
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("--single-process")
chrome_options.add_argument("--disable-dev-shm-usage")
path = '/home/ubuntu/chromedriver'
driver = webdriver.Chrome(path, options=chrome_options)


# 현재 전시 (다음 글이 없을 때까지 크롤링)
url = 'https://www.mmca.go.kr/exhibitions/progressList.do#'
driver.get(url)
sleep(3)

first = driver.find_element(By.CSS_SELECTOR, '#listDiv > ul > li > a').send_keys(Keys.ENTER)
sleep(3)

col_list = ['exhibition_id','exhibition_name', 'poster_link', 'exhibition_description', 'exhibition_period', 'exhibition_place']
row_list = []

time = datetime.now()
now = time.strftime('%Y%m%d')
i = 0

while(True):
    value_list = []
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    exhibition_id = now + '01' + str(i).zfill(4)
    exhibition_name = soup.select('figure > img')[0]['alt']
    poster_link = 'https://www.mmca.go.kr' + soup.select('figure > img')[0]['src']
    exhibition_description = soup.find('div', 'txtArea').text
    exhibition_period = soup.find('ul', 'barList').select('li')[0].text.strip()
    exhibition_place = soup.find('ul', 'barList').select('li')[1].text.strip()

    value_list.append(exhibition_id)
    value_list.append(exhibition_name)
    value_list.append(poster_link)
    value_list.append(exhibition_description)
    value_list.append(exhibition_period)
    value_list.append(exhibition_place)
    row_list.append(value_list)

    next = driver.find_elements(By.CSS_SELECTOR, '.detailPagi > div')[1]
    findTag = soup.find('div', 'detailPagi').select('div')[1].children
    if(list(findTag)[3].name == 'span'):
        break
    else:
        next.find_element(By.CSS_SELECTOR, 'a').send_keys(Keys.ENTER)
        sleep(3)
    i += 1

MMCA_df = pd.DataFrame(row_list, columns=col_list)

MMCA_df.to_csv(f'~/yogi6/raw_data/crawling/{now}/MMCA.csv', encoding="utf-8-sig", index=False)


