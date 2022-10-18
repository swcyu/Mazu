from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from time import sleep
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
import pandas as pd
import re

service = Service('chromedriver.exe')
driver = webdriver.Chrome(service=service)

url = 'https://ddp.or.kr/?menuno=240'
driver.get(url)
sleep(1)

exhibition_all_select = driver.find_element(By.XPATH, '/html/body/div[8]/form/div/div/div/div/div[1]/ul/li[1]/a')
exhibition_all_select.click()
sleep(1)

#마지막페이지 찾기
soup = BeautifulSoup(driver.page_source, 'html.parser')
last_page_link = str(soup.select('p[class=next_last] > a')[0])
#print(last_page_link)
#<a class="" href="#" onclick="return submitForm(this,'list',34);">마지막</a>
#print(type(last_page_link))
#<class 'str'>

last_page_num = last_page_link[-13:-11]
#print(last_page_num)
#34


col_list = ['exhibition_name', 'poster_link', 'exhibition_description', 'exhibition_period', 'exhibition_place']
row_list = []

for page in range(int(last_page_num)):
    exhibition_list = driver.find_elements(By.CSS_SELECTOR, 'ul[class=overList] > li')
    for i in range(len(exhibition_list)):
        value_list=[]
        driver.find_elements(By.CSS_SELECTOR, 'ul[class=overList] > li > a')[i].send_keys(Keys.ENTER)
        sleep(3)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        #데이터 추출
        exhibition_name = soup.select('strong[class=detail_cont_top_ttl]')[0].text
        exhibition_description = soup.select('div[class=detail_cont_inner] > div > div[class=detail_cont_each_txt]')[0].text.strip()
        target_image_link = soup.select('div[class=detail_cont_tbg]> img')[0]['src']
        poster_link = 'https://ddp.or.kr' + target_image_link
        #target_image_link = soup.select('div[class=detail_cont_tbg]> img')
        #poster_link = soup.select()
        for dl in soup.select('.detail_cont_top_txt._kor > dl'):
            if dl.dt.text == '일정':
                exhibition_period = dl.dd.text
            elif dl.dt.text == '장소':
                exhibition_place = dl.dd.text
            else:
                pass
        value_list.append(exhibition_name)
        value_list.append(poster_link)
        value_list.append(exhibition_description)
        value_list.append(exhibition_period)
        value_list.append(exhibition_place)
        row_list.append(value_list)
        print(exhibition_name, exhibition_description, exhibition_period, exhibition_place, poster_link)
        #뒤로가기
        driver.back()
        sleep(3)
    if page != int(last_page_num)-1:
        driver.find_element(By.XPATH, '/html/body/div[8]/form/div/div/div/div/div[2]/div[2]/p[3]/a').send_keys(Keys.ENTER)
        sleep(3)
    else:
        pass

DDP_df2 = pd.DataFrame(row_list, columns=col_list)

DDP_df2.to_csv('ddp.csv', encoding="utf-8-sig")
    #
    #exhibition_period = soup.select('strong[class=detail_cont_top_ttl')[0].text

'''
#8개의 전시들 선택
    exhibition_list = driver.find_elements(By.CSS_SELECTOR,'ul[class=article-list] > li')

    for i in range(len(exhibition_list)):
        value_list = []
        ##이미지 링크 뽑아내기##
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        target_image_link = soup.select('ul[class=article-list] > li div[class=thumb]')[i]['style']
        #background-image:url(/comm/getImage?srvcId=POST&parentSn=41126&fileTy=POSTTHUMB&fileNo=1&thumbTy=M)
        poster_link = 'https://korean.visitseoul.net' + target_image_link[target_image_link.find('url')+4:-1]
        #https://korean.visitseoul.net/comm/getImage?srvcId=POST&parentSn=41126&fileTy=POSTTHUMB&fileNo=1&thumbTy=M

        #전시목록에서 클릭해서 들어가기
        driver.find_elements(By.CSS_SELECTOR,'ul[class=article-list] > li')[i].find_element(By.TAG_NAME,'a').send_keys(Keys.ENTER)
        sleep(3)
'''




#describition = soup.select('div[class=detail_cont_each_txt]')[0]
#print(describition.text)


# 전시 설명 잘 나왔다.
#describition = soup.select('div[class=cwa-text]')[1]
#print(describition.text)

#describition = soup.select('div[class=cwa-text]')
#print(describition)
'''
#전체 공연 선택
exhibition_all_select = driver.find_element(By.XPATH, '/html/body/div[8]/form/div/div/div/div/div[1]/ul/li[1]/a')
exhibition_all_select.click()
sleep(1)

for i in range(len())
'''


