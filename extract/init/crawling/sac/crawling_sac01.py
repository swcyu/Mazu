import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep
from bs4 import BeautifulSoup

df = pd.read_csv('sac_list.csv')

service = Service('../drivers/chromedriver.exe')
driver = webdriver.Chrome(service=service)

# 현재 전시 (다음 글이 없을 때까지 크롤링)
url = 'https://www.sac.or.kr/site/main/home'
driver.get(url)
sleep(3)

col_list = ['exhibition_name', 'poster_link', 'exhibition_description', 'exhibition_period', 'exhibition_place']
row_list = []

driver.find_element(By.CLASS_NAME, 'search-btn').send_keys(Keys.ENTER)
sleep(3)
driver.find_element(By.ID, 'search-input').send_keys(df['공연/전시명'][0])
sleep(3)
driver.find_element(By.CSS_SELECTOR, 'div.search-box > a').send_keys(Keys.ENTER)
sleep(3)
# search-box > input 태그 의 value 값에 검색할 정보를 넣는다.
for i in range(1, len(df['공연/전시명'])):

    query = df['공연/전시명'][i]

    try:
        if(driver.find_element(By.XPATH, '//*[@id="contents"]/div[2]/div/ul/li[2]/a/span').text == '(0)'):
            driver.find_element(By.CLASS_NAME, 'search-btn').send_keys(Keys.ENTER)
            sleep(3)

            # search-box > input 태그(name="query") 의 value 값에 검색할 정보를 넣는다.
            search = driver.find_element(By.ID, 'query')
            search.click()
            sleep(2)
            search.send_keys(query)
            sleep(2)
            search.send_keys("\n")
            sleep(3)
        else:
            driver.find_element(By.LINK_TEXT, '바로가기').send_keys(Keys.ENTER)

            value_list = []
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            exhibition_name = df['공연/전시명'][i]
            exhibition_period = df['기간'][i]
            exhibition_place = df['장소'][i]
            poster_link = 'https://www.sac.or.kr/' + soup.select('.area.show-view-top.clearfix > dd > p > a > img')[0]['src']

            driver.find_element(By.ID, 'introTab').send_keys(Keys.ENTER)
            sleep(1)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            exhibition_description = soup.select_one('div[class=cwa-tab-list]').select_one('.ctl-sub.on').select('.cwa-text > div')[0].text


            value_list.append(exhibition_name)
            value_list.append(poster_link)
            value_list.append(exhibition_description)
            value_list.append(exhibition_period)
            value_list.append(exhibition_place)
            row_list.append(value_list)

            driver.find_element(By.CLASS_NAME, 'search-btn').send_keys(Keys.ENTER)
            sleep(3)
            # search-box > input 태그(name="query") 의 value 값에 검색할 정보를 넣는다.
            driver.find_element(By.ID, 'search-input').send_keys(query)
            sleep(2)
            search.send_keys("\n")
            sleep(3)
    except:
        pass

    print(i)

SAC_df = pd.DataFrame(row_list, columns=col_list)

SAC_df.to_csv('sac_all.csv', encoding="utf-8-sig")