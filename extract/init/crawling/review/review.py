from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from time import sleep
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import re
import math

##임의의 csv파일에서 전시명 불러와서 리스트로 저장하기##
target_csv = pd.read_csv('crawling_sema_past.csv')

search_list = []
for idx in target_csv.index:
    search_list.append(target_csv['exhibition_name'][idx])
#print(search_list)
#['서울 최초의 도시공원, 탑골공원', '나의 하루 이야기- 헝가리에서 온 편지', '매직샷展', '제12회 서울미디어시티비엔날레 사전프로그램 《정거장》', '국립한글박물관 상설전시 <훈민정음, 천년의 문자 계획>', '포에틱 AI', 'The Color Spot : 꿈속의 자연']

##인터파크에서 검색하기##
driver = webdriver.Chrome(executable_path='C:\workspaces\workspace_crawling\drivers\chromedriver.exe')

#test = 'dreamer.3:45am'
row_list = []
col_list = ['exhibition_name', 'star', 'review_title', 'review_detail']
for exh_name in search_list:
    target_url = 'https://tickets.interpark.com'
    driver.get(target_url)
    sleep(3)

    # 검색어 입력 및 검색버튼 클릭
    driver.find_element(By.ID,'Nav_SearchWord').send_keys(exh_name)
    driver.find_element(By.CSS_SELECTOR,'a[class=btn_search]').send_keys(Keys.ENTER)
    sleep(3)
    #target_url = f'https://tickets.interpark.com/search?keyword={exh_name}'
    #driver.get(target_url)
    #sleep(3)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # '빈 결과 태그'가 생성되지 않는경우 => 탐색 시작
    if (soup.select_one('div[class=categoryContents] > div[class=emptyResultContent]')) == None:
        print(f'{exh_name} : 검색성공', end='\t')
        tickets = soup.select('#allContent > div[class=ticketContent] ul[class=itemList] > li')
        #검색결과 5개로 한정
        if len(tickets) >= 5:
            tickets = tickets[:5]
        # 검색된 티켓들 순차탐색
        for ticket in tickets:
            driver.get(ticket.select_one('div[class=itemName] > a')['href'])

            # alert창 발생시, 닫고 다음 반복문 실행
            try:
                WebDriverWait(driver, 3).until(EC.alert_is_present())
                alert = driver.switch_to.alert
                alert.dismiss()
                sleep(3)
                continue
            except:
                pass

            sleep(3)

            # 팝업 발생시, 닫기 실행
            try:
                driver.find_element(By.CSS_SELECTOR, '.popupCloseBtn.is-bottomBtn').send_keys(Keys.ENTER)
                sleep(1)
            except:
                pass

            ##데이터추출##
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            li_list = soup.select('#productMainBody ul[class=navList] > li')

            for idx, li in enumerate(li_list):
                target_li = driver.find_elements(By.CSS_SELECTOR, '#productMainBody ul[class=navList] > li')[idx]
                # 전시 티켓인지 판별 + 이용후기 수가 5개 이상인 경우
                if re.findall('이용후기', li.find('a').text) and int(
                        re.sub(r'[^0-9]', '', li.select_one('span[class=countNum]').text)) >= 5:
                    # 이용후기 태그 클릭
                    target_li.find_element(By.CSS_SELECTOR,'a[class=navLink]').send_keys(Keys.ENTER)
                    sleep(3)

                    # 다른 페이지와 헷갈리지않도록 변수명 별도 설정
                    soup_review = BeautifulSoup(driver.page_source, 'html.parser')

                    # 이용후기 pagination을 위한 마지막 페이지 구하기
                    # 1.총 이용후기 갯수
                    total_review_count = int(re.sub(r'[^0-9]', '', soup_review.select_one('strong[class=bbsTotal]').text))
                    print(total_review_count)
                    # 2.총 페이지묶음 반복 횟수(기본:1회)
                    total_pages_count = math.ceil(total_review_count/150)

                    # 페이지 묶음별 탐색
                    for pages_num in range(total_pages_count):
                        soup_review = BeautifulSoup(driver.page_source, 'html.parser')
                        # 화면별 개별 페이지 탐색
                        for idx in range(len(soup_review.select('div[class=pagination] > ol[class=pageNumWrap] > li'))):
                            if idx != 0:
                                driver.find_elements(By.CSS_SELECTOR, 'div[class=pagination] > ol[class=pageNumWrap] > li')[idx]\
                                    .find_element(By.CSS_SELECTOR, 'a[class=pageNumBtn]').send_keys(Keys.ENTER)
                                sleep(3)
                            else:
                                pass

                            soup_review = BeautifulSoup(driver.page_source, 'html.parser')
                            review_boxes = soup_review.select('.bbsList.reviewList > li')
                            # 리뷰별 탐색
                            for review_box in review_boxes:
                                value_list = []
                                exhibition_name = exh_name
                                star = review_box.select_one('div[class=prdStarIcon]')['data-star']
                                review_title = review_box.select_one('div[class=bbsTitle]').text.strip()
                                review_detail = review_box.select_one('p[class=bbsText]').text.strip()
                                value_list.append(exhibition_name)
                                value_list.append(star)
                                value_list.append(review_title)
                                value_list.append(review_detail)
                                row_list.append(value_list)
                            #리뷰내용

                        # 다음 페이지묶음으로 이동
                        if (total_pages_count == 1) or (pages_num == total_pages_count-1):
                            pass
                        else:
                            driver.find_element(By.CSS_SELECTOR,'.pageNextBtn.pageArrow').send_keys(Keys.ENTER)
                            sleep(3)

                # 이용후기 li가 존재하고, 이용후기 수가 5개 미만인 경우
                elif re.findall('이용후기', li.find('a').text) and int(
                        re.sub(r'[^0-9]', '', li.select_one('span[class=countNum]').text)) < 5:
                    print(f"이용후기 갯수가 {re.sub(r'[^0-9]', '', li.select_one('span[class=countNum]').text)}개 라서 패스")
                else:
                    pass

            print('')
    else:
        print('검색실패')
        pass

test_df = pd.DataFrame(row_list, columns=col_list)
test_df.to_csv('crawling_sema_past_review.csv', encoding="utf-8-sig")
