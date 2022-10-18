## 데이터 로딩 및 전처리
print('데이터 로딩중!')
import pandas as pd

# 데이터 불러오기
# category: 0: 전시, 1:도서, 2: 영화
df = pd.read_csv('~/yogi6/model_data/data_final.csv', dtype={'place_id':str}) # 데이터 불러오기
df = df[df['description_prep'].notnull()] # 전시설명 결측치 제거
df['place_id'] = df['place_id'].astype(str)
df['place_id'] = df['place_id'].apply(lambda x: x.zfill(5)) # 우편번호 5자
df.reset_index(drop=True, inplace=True) # 인덱스 번호 초기화


## tfidf 벡터화 수행
print('tfidf 벡터화!')
from sklearn.feature_extraction.text import TfidfVectorizer

tfidf = TfidfVectorizer()
tfidf_matrix = tfidf.fit_transform(df['description_prep'])
print(tfidf_matrix.shape)

## 코사인 유사도 행렬 생성
print('코사인 유사도 행렬 생성!')
try:
  from sklearn.metrics.pairwise import cosine_similarity
  cosine_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

  ## 전시별 추천 결과 추출하는 함수 정의
  def recommend(title):
      # name -> id dictionary 생성
      name2id = {}
      for i, c in enumerate(df['name_cat']):
          name2id[i] = c

      # id -> name dictionary 생성
      id2name = {}
      for i, c in name2id.items():
          id2name[c] = i

      # 검색할 전시명 id 추출
      idx = id2name[title]

      # 전시 인덱스 번호 구하기
      exhi_start_idx = id2name[df[df['category'] == 0].iloc[0]['name_cat']]
      exhi_end_idx = id2name[df[df['category'] == 0].iloc[-1]['name_cat']]

      # 도서 인덱스 번호 구하기
      book_start_idx = id2name[df[df['category'] == 1].iloc[0]['name_cat']]
      book_end_idx = id2name[df[df['category'] == 1].iloc[-1]['name_cat']]

      # 영화 인덱스 번호 구하기
      movie_start_idx = id2name[df[df['category'] == 2].iloc[0]['name_cat']]
      movie_end_idx = id2name[df[df['category'] == 2].iloc[-1]['name_cat']]

      ## 카테고리별 유사도 상위 5개 추출
      # 전시 추천
      exhi_sim_scores = [(i, c) for i, c in enumerate(cosine_matrix[idx]) if i != idx if exhi_start_idx <= i <= exhi_end_idx]
      exhi_sim_scores = sorted(exhi_sim_scores, key = lambda x: x[1], reverse=True)
      exhi_sim_scores = [(name2id[i], score) for i, score in exhi_sim_scores[0:5]]

      # 도서 추천
      book_sim_scores = [(i, c) for i, c in enumerate(cosine_matrix[idx]) if i != idx if book_start_idx <= i <= book_end_idx]
      book_sim_scores = sorted(book_sim_scores, key = lambda x: x[1], reverse=True)
      book_sim_scores = [(name2id[i], score) for i, score in book_sim_scores[0:5]]

      # 영화 추천
      movie_sim_scores = [(i, c) for i, c in enumerate(cosine_matrix[idx]) if i != idx if movie_start_idx <= i <= movie_end_idx]
      movie_sim_scores = sorted(movie_sim_scores, key = lambda x: x[1], reverse=True)
      movie_sim_scores = [(name2id[i], score) for i, score in movie_sim_scores[0:5]]

      return exhi_sim_scores, book_sim_scores, movie_sim_scores

  ## 전시별 추천결과 저장하는 함수
  def save_recommend():
      rcmd = df[df['category']==0]
      rcmd['temp'] = rcmd['name_cat'].apply(lambda x: recommend(x))
      rcmd['recommend_exhi'] = rcmd['temp'].apply(lambda x: x[0])
      rcmd['recommend_book'] = rcmd['temp'].apply(lambda x: x[1])
      rcmd['recommend_movie'] = rcmd['temp'].apply(lambda x: x[2])
      rcmd.drop(['category', 'description_prep', 'temp'], axis=1, inplace=True)

      return rcmd
  ## 추천 결과 저장한 최종 데이터프레임 생성
  print("추천 결과 저장중!")
  rcmd = save_recommend()

  ## 최종 데이터프레임 저장
  rcmd.to_csv('~/yogi6/model_data/tfidf.csv', encoding='utf-8-sig')
  print("추천 결과 저장 완료!")
  print(rcmd)

except Exception as err:
    print(err)