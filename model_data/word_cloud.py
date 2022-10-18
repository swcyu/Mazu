time = datetime.now()
now = time.strftime('%Y%m%d')

def word_cloud(request):
  username = request.user.username
  exhibition_id_list = list(set(map(lambda x:x.exhibition_id, User_review.objects.filter(username=username, star__gt=3.5))))
  #print(exhibitions)
  #exhbi
  col_list = ['exhibition_id', 'description']
  row_list = []
  for exh_id in exhibition_id_list:
    exh_desc = Exhibition.objects.get(exhibition_id=exh_id).description
    value_list = [exh_id, exh_desc]
    row_list.append(value_list)
  
  user_pd = pd.DataFrame(row_list, columns=col_list)

  def apply_regular_expression(text):
    hangul = re.compile('[^ ㄱ-ㅣ 가-힣]') # 한글 추출 규칙: 띄어 쓰기(1개)를 포함한 한글
    result = hangul.sub('', text) # 위에 설정한 "hangul" 규칙을 "text"에 적용(.sub)시킴
    return result

  okt = Okt()
  okt_nouns = okt.nouns(apply_regular_expression(user_pd['description'][0]))

  # 불용어 사전
  stopwords = pd.read_csv("https://raw.githubusercontent.com/yoonkt200/FastCampusDataset/master/korean_stopwords.txt").values.tolist()

  # 전시 관련 불용어 사전 추가
  exhi_stopwords = ['전시', '전시회', '대해', '정도', '하나', '보고', '작가', '이번', '통해',
                  '우리', '지엄', '개최', '년대', '대표', '대한', '서울', '세계', '작품', '한국',
                  '모두', '사람', '주년', '주제', '위해', '이후', '이자', '참여', '작업', '진행',
                  '서로', '선정', '분야', '관계', '존재', '구성', '특별', '이야기', '경험', '모습',
                  '주목', '나볼', '누구', '개관', '이해', '최초', '아티스트', '활동', '자리', '다른',
                  '주요', '바탕', '시대', '지난', '의미', '지금', '로서', '공간', '시간', '기획', '가장',
                  '인간', '기록', '인간', '과정', '또한', '순간', '주요', '관련', '가장', '소개', '코로나',
                  '팬데믹', '자신', '중심', '세기', '공개', '관람', '버튼', '생각', '방문',
                  '감독', '정말', '조금', '추천', '다시', '진짜', '제대로', '때문', '자체', '별로', '서서',
                  '매우', '느낌', '인원', '내용', '다만', '아주', '일찍', '역시', '중간', '더욱',
                  '금지', '입장', '물이', '강추', '예약', '대기', '워낙', '시간대', '안내', '편이', '군데',
                  '가격', '전시관', '몇개', '계속', '도움', '마스크', '위주', '보기', '등등', '가야', '무조건',
                  '무언가', '부분', '미리', '최고', '참고', '다행', '거꾸로', '전혀', '작고', '나중', '거의',
                  '더욱더', '마련']
  for word in exhi_stopwords:
    stopwords.append(word)

    # BoW 백터 생성
  def text_cleaning(text):
      korean = re.compile('[^ ㄱ-ㅣ 가-힣]')
      result = korean.sub('', text)
      okt = Okt()
      nouns = okt.nouns(result)
      nouns = [x for x in nouns if len(x) > 1]
      nouns = [x for x in nouns if x not in stopwords] # 불용어 제거
      return nouns

  vector = CountVectorizer(tokenizer = lambda x: text_cleaning(x))
  bow_vector = vector.fit_transform(user_pd['description'].tolist())
  word_list = vector.get_feature_names()
  count_list = bow_vector.toarray().sum(axis=0)


  # 단어 - 빈도 매칭
  word_freq = dict(zip(word_list, count_list))

  # wordcloud
  word_cloud = WordCloud(font_path='malgun', width=400, height=400, max_font_size=100,
                      background_color='white').generate_from_frequencies(word_freq)
  
  return