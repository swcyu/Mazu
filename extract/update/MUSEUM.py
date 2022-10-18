from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from time import sleep
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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

target_url ='https://www.museum.go.kr/site/main/exhiSpecialTheme/list/current'
driver.get(target_url)
sleep(3)

col_list = ['exhibition_id','exhibition_name', 'poster_link', 'exhibition_description', 'exhibition_period', 'exhibition_place']
row_list = []

time = datetime.now()
now = time.strftime('%Y%m%d')

#페이지별 전시회 갯수 탐색
exhibition_list = driver.find_elements(By.CSS_SELECTOR,'.show-list.report.special > li')
for idx, driver_li in enumerate(exhibition_list):
    drivers = driver.find_elements(By.CSS_SELECTOR,'.show-list.report.special > li')
    value_list = []
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    exhibition_box = soup.select('.show-list.report.special > li')[idx]
    exhibition_id = now + '02' + str(idx).zfill(4)
    poster_link = 'https://www.museum.go.kr/' + exhibition_box.select_one('div[class=exhioversea-img-over]').find_next_sibling()['src']
    exhibition_name = exhibition_box.select_one('div[class=info] strong').text
    exhibition_period = exhibition_box.select('div[class=info] p')[0].text
    exhibition_place = exhibition_box.select('div[class=info] p')[1].text
    drivers[idx].find_element(By.TAG_NAME,'a').send_keys(Keys.ENTER)
    sleep(3)

    # 데이터 추출(description)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    exhibition_description = soup.select_one('div[class=view-info-cont]').text
    #description_html = soup.select_one('div[class=view-info-cont]')
    #exhibition_description = ' '.join(re.compile('[가-힣]+').findall(str(description_html)))

    value_list.append(exhibition_id)
    value_list.append(exhibition_name)
    value_list.append(poster_link)
    value_list.append(exhibition_description)
    value_list.append(exhibition_period)
    value_list.append(exhibition_place)
    #value_list.append(description_html)
    row_list.append(value_list)

    # 뒤로가기
    driver.back()
    sleep(3)

middle_museum_df = pd.DataFrame(row_list, columns=col_list)

middle_museum_df.to_csv(f'~/yogi6/raw_data/crawling/{now}/MUSEUM.csv', encoding="utf-8-sig", index=False)
