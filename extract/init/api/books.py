import requests
import pandas as pd
from bs4 import BeautifulSoup

def getData(url):
    response = requests.get(url)
    contents = response.text

    xml_obj = BeautifulSoup(contents, 'lxml-xml')
    rows = xml_obj.findAll('item')

    # 각 행의 컬럼, 이름, 값을 가지는 리스트 만들기
    row_list = []  # 행값
    name_list = []  # 열이름값
    value_list = []  # 데이터값

    # xml 안의 데이터 수집
    for i in range(0, len(rows)):
        columns = rows[i].find_all()
        # 첫째 행 데이터 수집
        for j in range(0, len(columns)):
            if i == 0:
                # 컬럼 이름 값 저장
                name_list.append(columns[j].name)
            # 컬럼의 각 데이터 값 저장
            value_list.append(columns[j].text)

        # 각 행의 value값 전체 저장
        row_list.append(value_list)
        # 데이터 리스트 값 초기화
        value_list = []

    print(len(row_list))
    print(name_list)
    print(len(name_list))

    # xml값 DataFrame으로 만들기
    df = pd.DataFrame(row_list, columns=name_list)
    return df

def getDataAladin(url):
    url = url
    response = requests.get(url)
    contents = response.text

    xml_obj = BeautifulSoup(contents, 'lxml-xml')
    rows = xml_obj.findAll('item')

    columns = ['title', 'link', 'author', 'pubDate', 'description', 'isbn', 'priceSales', 'priceStandard', 'mallType',
               'cover', 'categoryId', 'categoryName', 'publisher', 'customerReviewRank', 'bestRank']  # 열이름값
    row_list = []

    # xml 안의 데이터 수집
    for row in rows:
        value_list = []  # 한 행의 데이터
        for column in columns:
            value_list.append(row.find(column).text)
        row_list.append(value_list)

    return row_list


# 세종도서_교양
url2 = 'http://api.kcisa.kr/openapi/service/rest/meta14/getKPEF011802?serviceKey=03cf4332-5464-43b8-9b71-a0d5ca06580e&numOfRows=3000&pageNo=1'
# 사서추천도서2 - 국립중앙도서관
url3 = 'http://api.kcisa.kr/openapi/service/rest/meta13/getNLKF0201?serviceKey=03cc5f31-22cd-441c-bded-229ee6275717&numOfRows=2000&pageNo=1'
# 추천도서_이달의 읽을만한 책
url4 = 'http://api.kcisa.kr/openapi/service/rest/meta13/getKPEF0101?serviceKey=7fd7349c-a813-4ce5-a0b9-4164c11455bf&numOfRows=1100&pageNo=1'
# 추천도서 - 문화체육관광부
url5 = 'http://api.kcisa.kr/openapi/service/rest/meta4/getKCPG0506?serviceKey=ed19c920-88ec-4da9-b32c-8c951695bdcb&numOfRows=1000&pageNo=1'
# 알라딘 API
serviceKey = 'ttbgw03311704001'
# 50978~50985, 50988, 50989, 50990, 50991, 51076, 51060, 51063
categoryID = ['50978','50979','50980','50981','50982','50983','50984','50985','50988','50989','50990','50991','51076','51060','51063']
row_list = []
columns = ['title', 'link', 'author', 'pubDate', 'description', 'isbn', 'priceSales', 'priceStandard', 'mallType',
               'cover', 'categoryId', 'categoryName', 'publisher', 'customerReviewRank', 'bestRank']  # 열이름값
for id in categoryID:
    for i in range(1, 3):
        url = f'http://www.aladin.co.kr/ttb/api/ItemList.aspx?ttbkey={serviceKey}&QueryType=BestSeller&MaxResults=50&start={i}&SearchTarget=Book&CategoryId={id}&output=xml&Version=20131101'
        data = getDataAladin(url)
        if len(data) != 0:
            for value in data:
                row_list.append(value)
df = pd.DataFrame(row_list, columns=columns)
df.to_csv('~/yogi6/raw_data/api/book/book.csv', encoding='utf-8-sig', index=False)


# test_df = getData(url5)
# print(test_df)
# test_df.to_csv('test_all.csv', encoding="utf-8-sig")

df2 = getData(url2)
df2.to_csv('~/yogi6/raw_data/api/book/book_0.csv', encoding='utf-8-sig', index=False)

df3 = getData(url3)
df3.to_csv('~/yogi6/raw_data/api/book/book_1.csv', encoding='utf-8-sig', index=False)

df4 = getData(url4)
df4.to_csv('~/yogi6/raw_data/api/book/book_2.csv', encoding='utf-8-sig', index=False)

df5 = getData(url5)
df5.to_csv('~/yogi6/raw_data/api/book/book_3.csv', encoding='utf-8-sig', index=False)



