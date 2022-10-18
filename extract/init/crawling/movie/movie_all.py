from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from time import sleep
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd

driver = webdriver.Chrome(executable_path='C:\workspaces\workspace_crawling\drivers\chromedriver.exe')
target_url ='https://www.kobis.or.kr/kobis/business/stat/offc/findFormerBoxOfficeList.do'
driver.get(target_url)
sleep(3)

btns_more = driver.find_elements(By.CLASS_NAME, 'btn_more')

#print(btns_more)

#사실 btn이 아니라 a태그인데, onclick이벤트로 작동을 하기 때문에 send_keys사용
for btn in btns_more[:-1]:
    btn.send_keys(Keys.ENTER)
    sleep(2)


col_list = ['movie_name', 'img_link', 'synopsis', 'director']
row_list = []
for i in range(500):
    value_list = []
    target_movie = driver.find_element(By.CSS_SELECTOR, f'#tab-5 #tr_tot{i} .boxMNm')
    movie_name = target_movie.text

    target_movie.send_keys(Keys.ENTER)
    sleep(2)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    img_link = 'https://www.kobis.or.kr' + soup.select('.ovf.info.info1 > a')[0].attrs['href']
    synopsis = soup.select('p[class=desc_info]')[0].text.strip()
    director = soup.select('div[id$=director] dd a')[0].text
    value_list.append(movie_name)
    value_list.append(img_link)
    value_list.append(synopsis)
    value_list.append(director)
    row_list.append(value_list)
    sleep(1)
    driver.find_element(By.CSS_SELECTOR, '.ui-dialog.ui-corner-all.ui-widget.ui-widget-content.ui-front.ui-draggable.ui-resizable').find_element(By.CLASS_NAME,'close').send_keys(Keys.ENTER)
    sleep(2)

movie_df = pd.DataFrame(row_list, columns=col_list)
#print(test_df)

movie_df.to_csv('movie.csv', encoding="utf-8-sig")