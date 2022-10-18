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

time = datetime.now()
now = time.strftime('%Y%m%d')



## 2011-01-01 부터 총 3665건, 611쪽
##url = 'https://www.mcst.go.kr/kor/s_culture/culture/cultureList.jsp?pCurrentPage=1&pSearchType=01&pSearchWord=&pType=%EC%A0%84%EC%8B%9C&pArea=&pPeriod=&fromDt=20110101&toDt=2022.08.30.'
# 2022-09-10부터 2022-09-25 까지총 26건, 5쪽
url = 'https://www.mcst.go.kr/kor/s_culture/culture/cultureList.jsp?pCurrentPage=1&pSearchType=01&pSearchWord=&pType=%EC%A0%84%EC%8B%9C&pArea=&pPeriod=&fromDt=20220910&toDt=2022.09.25.'
driver.get(url)
sleep(5)

driver.find_element(By.CLASS_NAME, 'go').send_keys(Keys.ENTER)
sleep(3)

col_list = ['exhibition_id', 'exhibition_name', 'poster_link', 'exhibition_description', 'exhibition_period', 'exhibition_place']
row_list = []
try:
    ## 총 3665개
    # 총 26개
    for i in range(0, 100):
        value_list = []
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        exhibition_id = now + '06' + str(i).zfill(4)
        exhibition_name = soup.select('p.board_tit')[0].text
        poster_link = 'https://www.mcst.go.kr/' + soup.select('div > img')[0]['src']
        exhibition_description = soup.select('div.view_con')[0].text
        exhibition_period = soup.select('div.board_detail > dl > dd')[1].text.strip()
        exhibition_place = soup.select('div.board_detail > dl > dd')[3].text.strip()

        value_list.append(exhibition_id)
        value_list.append(exhibition_name)
        value_list.append(poster_link)
        value_list.append(exhibition_description)
        value_list.append(exhibition_period)
        value_list.append(exhibition_place)
        row_list.append(value_list)
        print(value_list)
        print(i)
        driver.find_elements(By.CSS_SELECTOR, '.viewbtnWrap > a')[2].send_keys(Keys.ENTER)
        sleep(3)
except:
    MCST_df = pd.DataFrame(row_list, columns=col_list)
    MCST_df.to_csv(f'~/yogi6/raw_data/crawling/{now}/MCST.csv', encoding="utf-8-sig", index=False)