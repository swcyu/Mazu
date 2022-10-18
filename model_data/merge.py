import pandas as pd
import numpy as np
from datetime import datetime

time = datetime.now()
now = time.strftime('%Y%m%d')

## 1. 전시 데이터 전처리
# 전시 데이터 불러오기
df_exhi = pd.read_csv(f'~/yogi6/model_data/exhibition_final.csv')
df_exhi['category'] = 0

# 전시명 널값으로 인식된 'NULL' 텍스트로 다시 입력하기
df_exhi.loc[df_exhi['name'].isnull(), 'name'] = 'NULL'

# 카테고리별로 동일한 이름 중복으로 잡히지 않도록 카테고리명 추가
df_exhi['name_cat'] = '[전시]' + df_exhi['name']

# 분석용 전시설명 전처리(설명 한글만 남기기+불용어 제거)
df_exhi['description_prep'] = df_exhi['description'].str.replace(pat=r'[^ ㄱ-ㅣ가-힣]+',repl=r' ',regex=True)
df_exhi['description_prep'] = df_exhi['description_prep'].str.replace('맑은', '')
df_exhi['description_prep'] = df_exhi['description_prep'].str.replace('고딕', '')
df_exhi['description_prep'] = df_exhi['description_prep'].str.replace('굴림', '')
df_exhi['description_prep'] = df_exhi['description_prep'].str.replace('돋움', '')
df_exhi['description_prep'] = df_exhi['description_prep'].str.replace('바탕글', '')
df_exhi['description_prep'] = df_exhi['description_prep'].str.replace('전시소개', '')
df_exhi['description_prep'] = df_exhi['description_prep'].str.replace('전시 소개', '')
df_exhi['description_prep'] = df_exhi['description_prep'].str.replace('전시기간', '')
df_exhi['description_prep'] = df_exhi['description_prep'].str.replace('전시장소', '')
df_exhi['description_prep'] = df_exhi['description_prep'].str.replace('부대행사', '')

# 불필요한 컬럼 삭제
#df_exhi.drop('Unnamed: 0', axis=1, inplace=True)



## 2. 도서 데이터 전처리
df_book = pd.read_csv('~/yogi6/model_data/book.csv')
df_book = df_book[['title', 'description']]

# 필요한 컬럼명 변경
df_book.rename(columns={'title': 'name'}, inplace=True)

# 책 이름 중복 제거
df_book['name_dup'] = df_book['name'].str.replace(pat=r'[^\w]',repl=r' ',regex=True)
df_book['name_dup'] = df_book['name_dup'].str.replace(' ', '')
df_book.drop_duplicates(subset=['name_dup'], keep='first', inplace=True)

# 설명 한글만 남기기
df_book['description_prep'] = df_book['description'].str.replace(pat=r'[^ ㄱ-ㅣ가-힣]+',repl=r' ',regex=True)
df_book.drop_duplicates(subset=['description_prep'], keep='first', inplace=True)

# 설명 널값 제거하기
df_book = df_book[df_book['description_prep'].notnull()]
df_book.reset_index(drop=True, inplace=True)

# 도서 설명이 공백포함 30자 미만인 행들은 제거
df_book = df_book[df_book['description_prep'].str.len() > 30]

# 없는 컬럼 채우기
df_book['poster_link'] = None
df_book['detail_place'] = None
df_book['start_period'] = '2016-01-01'
df_book['end_period'] = '2999-12-31'
df_book['place_id'] = None
df_book['category'] = 1
df_book['name_cat'] = '[도서]' + df_book['name']

# 필요한 컬럼만 저장
df_book = df_book[['name',
                   'poster_link',
                   'description',
                   'detail_place',
                   'start_period',
                   'end_period',
                   'place_id',
                   'category',
                   'name_cat',
                   'description_prep']]



## 3. 영화 데이터 전처리
df_movie = pd.read_csv('~/yogi6/model_data/movie.csv')

# 영화 이름 중복 제거
df_movie['name_dup'] = df_movie['name'].str.replace(pat=r'[^\w]', repl=r' ', regex=True)
df_movie['name_dup'] = df_movie['name_dup'].str.replace(' ', '')
df_movie.drop_duplicates(subset=['name_dup'], keep='first', inplace=True)

# 영화 감독 + 설명 합친 description_prep 만들기
df_movie['description_prep'] = df_movie['director'] + ' ' + df_movie['description']

# 설명 한글만 남기기
df_movie['description_prep'] = df_movie['description'].str.replace(pat=r'[^ ㄱ-ㅣ가-힣]+', repl=r' ', regex=True)

# 설명 널값 제거하기
df_movie = df_movie[df_movie['description_prep'].notnull()]
df_movie.reset_index(drop=True, inplace=True)

# 없는 컬럼 채우기
df_movie['poster_link'] = None
df_movie['detail_place'] = None
df_movie['start_period'] = '2016-01-01'
df_movie['end_period'] = '2999-12-31'
df_movie['place_id'] = None
df_movie['category'] = 2
df_movie['name_cat'] = '[영화]' + df_movie['name'].str.lstrip()

# 영화 설명이 공백포함 10자 미만인 행들은 제거
df_movie = df_movie[df_movie['description_prep'].str.len() > 10]

# 필요한 컬럼만 저장
df_movie = df_movie[['name',
                     'poster_link',
                     'description',
                     'detail_place',
                     'start_period',
                     'end_period',
                     'place_id',
                     'category',
                     'name_cat',
                     'description_prep']]



## 4. 전시(0) + 도서(1) + 영화(2) 데이터 합치기
df = pd.concat([df_exhi, df_book, df_movie], ignore_index=True)
df.to_csv('~/yogi6/model_data/data_final.csv', encoding='utf-8-sig')

print('데이터 전처리 및 통합 완료!')
#print(df)
