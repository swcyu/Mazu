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

#과거전시url, 마지막 페이지를 알기위해 우선 접속
target_url ='https://korean.visitseoul.net/exhibition?curPage=1&srchType=&srchOptnCode=&srchCtgry=&sortOrder=&srchSchdul=&srchBgnDe=&srchEndDe=&srchWord='
driver.get(target_url)
sleep(3)

soup = BeautifulSoup(driver.page_source, 'html.parser')
last_page_link = soup.select('div[class=paging-lst] > a:last-child')[0]['href']
last_page_num = int(last_page_link[last_page_link.find('curPage')+8:last_page_link.find('srchType')-1])


time = datetime.now()
now = time.strftime('%Y%m%d')

col_list = ['exhibition_id','exhibition_name', 'poster_link', 'exhibition_description', 'exhibition_period', 'exhibition_place']
row_list = []
for page_num in range(1, last_page_num+1):
    target_url = f'https://korean.visitseoul.net/exhibition?curPage={page_num}&srchType=&srchOptnCode=&srchCtgry=&sortOrder=&srchSchdul=&srchBgnDe=&srchEndDe=&srchWord='
    driver.get(target_url)
    sleep(3)
    #8개의 전시들 선택
    exhibition_list = driver.find_elements(By.CSS_SELECTOR,'ul[class=article-list] > li')
    #print(exhibition_list)

    for i in range(len(exhibition_list)):
        exhibition_id = now + '00' + str(i).zfill(4)
        value_list = []
        #이미지 링크 뽑아내기
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        target_image_link = soup.select('ul[class=article-list] > li div[class=thumb]')[i]['style']
        poster_link = 'https://korean.visitseoul.net' + target_image_link[target_image_link.find('url')+4:-1]

        #전시목록에서 클릭해서 들어가기
        driver.find_elements(By.CSS_SELECTOR,'ul[class=article-list] > li')[i].find_element(By.TAG_NAME,'a').send_keys(Keys.ENTER)
        sleep(3)

        ##데이터 추출##
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        exhibition_name = soup.select('.h3.textcenter')[0].text.strip()

        #설명 태그가 너무 중구난방이라 싹 긁어와서 정규식으로 한글만 뽑아내기, 나중에 html태그 사용하기 위해 별도로 추가
        exhibition_description = soup.select('div[class=text-area]')[0].text
        #description_html = soup.select('div[class=text-area]')[0]
        #exhibition_description = ' '.join(re.compile('[가-힣]+').findall(str(soup.select('div[class=text-area]')[0])))

        for dl in soup.select('.detail-map-infor'):
            if dl.find('dt').text == '행사 기간':
                exhibition_period = dl.find('dd').text.strip()
            elif dl.find('dt').text == '주소':
                exhibition_place = dl.find('dd').text.strip()
            else:
                pass
        value_list.append(exhibition_id)
        value_list.append(exhibition_name)
        value_list.append(poster_link)
        value_list.append(exhibition_description)
        value_list.append(exhibition_period)
        value_list.append(exhibition_place)
        #value_list.append(description_html)
        row_list.append(value_list)

        sleep(1)
        #뒤로가기
        driver.back()
        sleep(3)



now = time.strftime('%Y-%m-%d')

VSN_df = pd.DataFrame(row_list, columns=col_list)

VSN_df.to_csv('~/jesun/VSN.csv', encoding="utf-8-sig")