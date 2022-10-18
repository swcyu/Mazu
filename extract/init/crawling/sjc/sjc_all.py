from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from time import sleep
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
import pandas as pd
import re

# 구동 : 기간에 값 넣고 조회 > 페이지를 돌면서 각 전시의 '상세'로 들어 가는 url들을 link에 리스트로 넣음 > link 안에 있는 url들을 한번씩 들어가며 필요한 내용 크롤링 후 생선된 데이터를 csv 출력
# 참고 : 중복되는 행이 있지만 전처리 하지 않은 코드 입니다.

# 크롬 드라이버 선언
service = Service('chromedriver.exe')
driver = webdriver.Chrome(service=service)

# 사이트 접속
target_url = 'https://www.sejongpac.or.kr/portal/performance/exhibit/performList.do?menuNo=200005'
driver.get(target_url)
sleep(3)

# 기간 "전체" 버튼 클릭
btn_all = driver.find_element(By.CSS_SELECTOR, '.item>label:last-child')
btn_all.click()
sleep(3)

# 기존 기간 값 없애기
driver.find_element(By.CLASS_NAME, "datepickerRange").clear()
sleep(2)

# 원하는 기간 값 넣기
driver.find_element(By.CLASS_NAME, "datepickerRange").send_keys('2016-04-01 - 2022-08-30')
sleep(2)

# 달력 닫기
date_close = driver.find_element(By.XPATH, '/html/body/div/div[4]/button[2]')
driver.execute_script("arguments[0].click();", date_close)
sleep(2)

# 조회 누르기
driver.find_element(By.XPATH, '/html/body/section/div[3]/div/div[2]/article/div/form/div[3]/ul/li[3]/div/button').send_keys(Keys.ENTER)
sleep(2)

# 파싱
soup = BeautifulSoup(driver.page_source, 'html.parser')

# 총 게시글 수 확인
last_page_link = int(soup.select('div[class=etc_w] > span > strong')[0].text)
# print(last_page_link)
# 423

# 총 넘겨야 하는 페이지 수 확인
last_page_num = last_page_link // 100
# print(last_page_num)
# 4

# 빈 링크 리스트 생성
links = []

# 페이지 넘기기
for total_skip_num in range(last_page_num + 1):
    # 리스트로 가져오기 위한 페이지 수 확인
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    pages = soup.select('.paginationSet > ul > li')
    # 페이지 넘길 때마다 파싱 후 '상세' 링크 크롤링
    for page in range(len(pages) - 4):
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        for li in soup.select('#performList > .bbs-today_thumb.clearfix > li'):
            links.append('https://www.sejongpac.or.kr' + li.select_one('div[class=vertical] > a:last-child').attrs['href'])
        # 다음 페이지로 이동
        page_li = driver.find_elements(By.CSS_SELECTOR, '.paginationSet > ul > li')
        # print(page_li)
        # 14
        next_page = page_li[page + 3].find_element(By.TAG_NAME, 'a')
        next_page.send_keys(Keys.ENTER)
        sleep(3)

# 실제 사용할 컬럼 지정, 빈 행 리스트 생성
col_list = ['exhibition_name', 'poster_link', 'exhibition_description', 'exhibition_period', 'exhibition_place']
row_list = []

# 링크에 들어있는 '상세' 링크 하나씩 들어 가서 필요한 부분 크롤링
for link in links:
    value_list = []
    driver.get(link)
    sleep(3)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    exhibition_name = soup.select('div[class=tit] > h2[class=t]')[0].text
    try:
        target_link = soup.select('div[class=poster] > img')[0]['src']
        poster_link = 'https://www.sejongpac.or.kr' + target_link
    except:
        poster_link = None
    exhibition_target_period = soup.select('ul[class=detail] > li')[0].text.replace('기간', '')
    exhibition_period = re.sub("[\s]", "", exhibition_target_period)
    exhibition_target_place = soup.select('ul[class=detail] > li')[1].text.replace('장소', '')
    exhibition_place = re.sub("[\s]", "", exhibition_target_place)
    try:
        description_html = soup.select('.tab_detail.on > div[class=editor]')[0]
        exhibition_description = ' '.join(re.compile('[가-힣]+').findall(str(description_html)))
    except:
        exhibition_description = None
    # 크롤링 한 변수들 row에 넣기
    value_list.append(exhibition_name)
    value_list.append(poster_link)
    value_list.append(exhibition_description)
    value_list.append(exhibition_period)
    value_list.append(exhibition_place)
    row_list.append(value_list)
    print(exhibition_name, poster_link, exhibition_description, exhibition_period, exhibition_place)

# CSV로 출력
SJC_df = pd.DataFrame(row_list, columns=col_list)

SJC_df.to_csv('sjc.csv', encoding="utf-8-sig")