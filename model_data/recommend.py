### TF-IDF 기반 전시/도서/영화 추천시스템
## 1. 데이터 로딩 및 전처리
import pandas as pd
import numpy as np

# 데이터 불러오기
print('데이터 로딩중!')
# category: 0: 전시, 1:도서, 2: 영화
df = pd.read_csv('~/yogi6/model_data/data_final.csv', dtype={'place_id':str}) # 데이터 불러오기
df.loc[df['name'].isnull(), 'name'] = 'NULL' # 전시명 널값으로 인식된 'NULL' 텍스트로 다시 입력하기
df = df[df['description_prep'].notnull()] # 전시설명 결측치 제거
df.drop('Unnamed: 0',axis=1, inplace=True) # 필요없는 컬럼 제거
df['place_id'] = df['place_id'].astype(str)
df['place_id'] = df['place_id'].apply(lambda x: x.zfill(5)) # 우편번호 5자
df.reset_index(drop=True, inplace=True) # 인덱스 번호 초기화

## 2. tf-idf 수행
print('tfidf 벡터화!')
from sklearn.feature_extraction.text import TfidfVectorizer
tfidf = TfidfVectorizer()
tfidf_matrix = tfidf.fit_transform(df['description_prep'])

## 3. 코사인 유사도 행렬 생성
print('코사인 유사도 행렬 생성!')
print('0')
from sklearn.metrics.pairwise import cosine_similarity
print('0.5')
cosine_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
print('1')
## 4. tf-idf 전시/도서/영화 추천시스템 함수 정의
def recommendation(title):
    # name -> id dictionary 생성
    name2id = {}
    for i, c in enumerate(df['name']):
        name2id[i] = c

    # id -> name dictionary 생성
    id2name = {}
    for i, c in name2id.items():
        id2name[c] = i

    # 검색할 전시명 id 추출
    idx = id2name[title]

    # 전시 인덱스 번호 구하기
    exhi_start_idx = id2name[df[df['category'] == 0].iloc[0]['name']]
    exhi_end_idx = id2name[df[df['category'] == 0].iloc[-1]['name']]

    # 도서 인덱스 번호 구하기
    book_start_idx = id2name[df[df['category'] == 1].iloc[0]['name']]
    book_end_idx = id2name[df[df['category'] == 1].iloc[-1]['name']]

    # 영화 인덱스 번호 구하기
    movie_start_idx = id2name[df[df['category'] == 2].iloc[0]['name']]
    movie_end_idx = id2name[df[df['category'] == 2].iloc[-1]['name']]

    ## 카테고리별 유사도 상위 5개 추출
    # 전시 추천
    exhi_sim_scores = [(i, c) for i, c in enumerate(cosine_matrix[idx]) if i != idx if exhi_start_idx <= i <= exhi_end_idx]
    exhi_sim_scores = sorted(exhi_sim_scores, key = lambda x: x[1], reverse=True)
    exhi_list = [name2id[i] for i, score in exhi_sim_scores[0:5]]

    # 도서 추천
    book_sim_scores = [(i, c) for i, c in enumerate(cosine_matrix[idx]) if i != idx if book_start_idx <= i <= book_end_idx]
    book_sim_scores = sorted(book_sim_scores, key = lambda x: x[1], reverse=True)
    book_list = [name2id[i] for i, score in book_sim_scores[0:5]]

    # 영화 추천
    movie_sim_scores = [(i, c) for i, c in enumerate(cosine_matrix[idx]) if i != idx if movie_start_idx <= i <= movie_end_idx]
    movie_sim_scores = sorted(movie_sim_scores, key = lambda x: x[1], reverse=True)
    movie_list = [name2id[i].lstrip() for i, score in movie_sim_scores[0:5]]

    return exhi_list, book_list, movie_list
print('2')
## 5. 전시별 추천결과 새 컬럼으로 저장하는 함수
def save_recommend():
    rcmd = df[df['category']==0]
    rcmd['temp'] = rcmd['name'].apply(lambda x: recommendation(x))
    rcmd['recommend_exhi'] = rcmd['temp'].apply(lambda x: x[0])
    rcmd['recommend_book'] = rcmd['temp'].apply(lambda x: x[1])
    rcmd['recommend_movie'] = rcmd['temp'].apply(lambda x: x[2])
    rcmd.drop(['temp'], axis=1, inplace=True)

    return rcmd
print('3')
## 6. 추천결과 저장한 최종 데이터프레임 생성
print("tfidf 추천 결과 저장중!")
rcmd = save_recommend()

## 7. tf-idf 결과 저장
#rcmd.to_csv('tfidf_recommend.csv', encoding='utf-8-sig')
print("tfidf 추천 결과 저장 완료!")


### Doc2Vec 기반 전시 추천시스템
## 1. 데이터 로딩 및 전처리
rcmd = rcmd[rcmd['category']==0] # tf-idf 결과 데이터에서 전시 데이터만 남기기
rcmd.reset_index(drop=True, inplace=True) # 인덱스 번호 초기화


## 2. Doc2Vec 형태소 분석 및 모델 저장 함수
from konlpy.tag import Mecab
from gensim.models.doc2vec import TaggedDocument
from tqdm import tqdm
from gensim.models import doc2vec

# 전시설명 형태소 분석 함수
def make_corpus(df=rcmd):
    print('형태소 분석중!')

    mecab = Mecab() # 형태소 분석기 mecab 사용
    tagged_corpus_list = []
    for index, row in tqdm(df.iterrows(), total=len(df)): # 각 행마다 제목과 형태소 분석된 설명을 담은 리스트 생성
        text = row['description_prep']
        tag = row['name_cat']
        tagged_corpus_list.append(TaggedDocument(tags=[tag], words=mecab.morphs(text)))

    return tagged_corpus_list


## 모델 생성/학습/저장 함수
def using_model(tagged_corpus_list):
    print('doc2vec 모델 생성중!')

    # model 생성
    model = doc2vec.Doc2Vec(vector_size=300, alpha=0.025, min_alpha=0.025, workers=8, window=8)

    # Vocabulary 빌드
    model.build_vocab(tagged_corpus_list)

    # model 학습
    print('doc2vec 모델 학습중!')
    model.train(tagged_corpus_list, total_examples=model.corpus_count, epochs=50)

    # model 저장
    model.save('recommend_exhi.doc2vec')
    print('doc2vec 모델 저장완료!')

## 모든 과정 순차적으로 실행하는 함수
def toSaveModel():
    return using_model(make_corpus())

toSaveModel()
## 3. 저장한 doc2vec 모델 불러오기
from gensim.models import doc2vec
model = doc2vec.Doc2Vec.load('recommend_exhi.doc2vec')

## 4. doc2vec 추천 전시 함수 정의
def recommendation_doc(title):
    # name -> id dictionary 생성
    name2id = {}
    for i, c in enumerate(rcmd['name_cat']):
        name2id[i] = c

    # id -> name dictionary 생성
    id2name = {}
    for i, c in name2id.items():
        id2name[c] = i

    # 검색할 전시명 id 추출
    idx = id2name[title]

    # 카테고리별 유사도 출력
    exhi_sim_scores = model.docvecs.most_similar(title, topn=5)

    # 추천 전시명만 리스트에 담기
    exhi_list = []
    for i in range(5):
        name = str(exhi_sim_scores[i][0])
        name = name[4:]
        exhi_list.append(name)

    return exhi_list


# 5. 추천 결과 컬럼 추가
print("doc2vec 추천 결과 저장중!")
rcmd['recommend_doc'] = rcmd['name_cat'].apply(lambda x: recommendation_doc(x))

# 6. doc2vec 추천 결과 저장
#rcmd.to_csv('doc2vec_exhi.csv', encoding='utf-8-sig')
print("doc2vec 추천 결과 저장 완료!")

# 7. 필요 없는 컬럼 제거 후 tfidf + doc2vec 통합 결과 저장
rcmd.drop(['category', 'name_cat', 'description_prep'], axis=1, inplace=True)
rcmd.to_csv('~/yogi6/model_data/recommend.csv', encoding='utf-8-sig', index=False)
print("tfidf, doc2vec 통합 파일 저장 완료!")
