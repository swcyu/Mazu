from django.shortcuts import render, redirect
from .models import Book, Exhibition, ExhibitionPlace, User_like, User_review, Summary, Movie
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from yogi6.models import User
from datetime import date, datetime
import logging
import ast
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.views.generic import ListView
from pure_pagination.mixins import PaginationMixin
from django.core.paginator import Paginator
import random
from elasticsearch import Elasticsearch
from haversine import haversine, Unit
import requests
import json


##test##
import pandas as pd
import numpy as np
import re
from konlpy.tag import Okt
from sklearn.feature_extraction.text import CountVectorizer
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from io import StringIO

time = datetime.now()
now = time.strftime('%Y-%m-%d')

def home(request):
    if request.user.is_anonymous:
        return render(request, 'home.html', {'data': {'recent' : recent_exhibition(), 'hot' : hot_exhibition(), 'deadline' : deadline_exhibition()}})
        # return render(request, 'home.html', {'data': {'recent' : recent_exhibition(), 'deadline' : deadline_exhibition()}})
    else:
        return render(request, 'home.html', {'data': {'recommend': recommend_exhibition(request) ,'near' : near_exhibition(request), 'recent' : recent_exhibition(), 'hot' : hot_exhibition(), 'similar' : similar_exhibition(request)}})
        # return render(request, 'home.html', {'data': {'recommend': recommend_exhibition(request) ,'near' : near_exhibition(request), 'recent' : recent_exhibition()}})


# pip install django-pure-pagination
# class CategoryListView(PaginationMixin, ListView):
class CategoryListView(ListView):
    template_name = 'category.html'
    paginate_by = 8
    model = Exhibition

    def get_queryset(self):
        id = self.kwargs.get('id')
        if id == 10:
            return Exhibition.objects.filter(cluster__contains='기타').order_by('exhibition_id')
        else:
            return Exhibition.objects.filter(cluster__contains=f'{id}').order_by('exhibition_id')

    def get_context_data(self, **kwargs):
        category_dic = {'0': '대중', '1': '문화재', '2': '미디어아트', '3': '추상', '4': '가족', '5': '글로벌',
                        '6': '수상작', '7': '현대', '8': '과학', '9': '예술', '10': '기타'}
        context = super(CategoryListView, self).get_context_data()
        id = self.kwargs.get('id')

        if id == 10:
            p = Paginator(Exhibition.objects.filter(cluster__contains='기타').order_by('exhibition_id'), self.paginate_by)
            context['exhibition_list'] = p.page(context['page_obj'].number)
            context['category_name'] = category_dic.get(f'{id}')


        else:
            p = Paginator(Exhibition.objects.filter(cluster__contains=f'{id}').order_by('exhibition_id'), self.paginate_by)
            context['exhibition_list'] = p.page(context['page_obj'].number)
            context['category_name'] = category_dic.get(f'{id}')

        return context


# context['exhibition_list'] = Exhibition.objects.filter(cluster__contains=f'{id}').order_by('exhibition_id')


def detail(request, id):
    if request.method == 'GET':
        target_exhibition = Exhibition.objects.filter(exhibition_id=id).first()
        target_review_star = list(map(lambda x: x.star, User_review.objects.filter(exhibition_id=id)))


        #log에 유저정보를 찍기전 로그인 유무 판단
        if request.user.is_anonymous:
          logger_click(request, target_exhibition, login=0)
        else:
          logger_click(request, target_exhibition, login=1)
          
        #도서 추천 TOP5 나누기
        recom_book = target_exhibition.recommend_book
        arr = ast.literal_eval(recom_book)

        #전시 추천 TOP5 나누기
        recom_exhi = target_exhibition.recommend_exhi
        arr3 = ast.literal_eval(recom_exhi)

        #영화 추천 TOP5 나누기
        recom_movie = target_exhibition.recommend_movie
        arr5 = ast.literal_eval(recom_movie)

        #평균 별점 보여주기
        if len(target_review_star) == 0:
            mean_star=0
        else:
            mean_star = round(sum(target_review_star) / len(target_review_star), 1)

        #print(target_summary)

        # 리뷰 긍정 부정 나누기
        # rating_pos = target_summary.rating
        # arr7 = ast.literal_eval(rating_pos)


        #전시 포스터 표현
        try:
            poster1 = Exhibition.objects.filter(name=arr3[0])[0].poster_link
        except:
            poster1 = ''
        try:
            poster2 = Exhibition.objects.filter(name=arr3[1])[0].poster_link
        except:
            poster2 = ''
        try:
            poster3 = Exhibition.objects.filter(name=arr3[2])[0].poster_link
        except:
            poster3 = ''
        try:
            poster4 = Exhibition.objects.filter(name=arr3[3])[0].poster_link
        except:
            poster4 = ''
        try:
            poster5 = Exhibition.objects.filter(name=arr3[4])[0].poster_link
        except:
            poster5 = ''

        #영화 포스터 표현
        try:
            poster11 = Movie.objects.filter(name=arr5[0])[0].poster_link
        except:
            poster11 = ''
        try:
            poster22 = Movie.objects.filter(name=arr5[1])[0].poster_link
        except:
            poster22 = ''
        try:
            poster33 = Movie.objects.filter(name=arr5[2])[0].poster_link
        except:
            poster33 = ''
        try:
            poster44 = Movie.objects.filter(name=arr5[3])[0].poster_link
        except:
            poster44 = ''
        try:
            poster55 = Movie.objects.filter(name=arr5[4])[0].poster_link
        except:
            poster55 = ''

          #exhibition_id = User.objects.get()

        dic = {}
        dic['exhibition_id'] = target_exhibition.exhibition_id
        dic['name'] = target_exhibition.name
        dic['poster_link'] = target_exhibition.poster_link
        dic['detail_place'] = target_exhibition.detail_place
        dic['description'] = target_exhibition.description
        dic['start_period'] = target_exhibition.start_period
        dic['end_period'] = target_exhibition.end_period
        dic['place_id'] = target_exhibition.place_id
        dic['star'] = mean_star

        dic['recom_books_1st'] = arr[0]
        dic['recom_books_2nd'] = arr[1]
        dic['recom_books_3rd'] = arr[2]
        dic['recom_books_4th'] = arr[3]
        dic['recom_books_5th'] = arr[4]

        dic['recom_exhi_1st'] = arr3[0]
        dic['recom_exhi_2nd'] = arr3[1]
        dic['recom_exhi_3rd'] = arr3[2]
        dic['recom_exhi_4th'] = arr3[3]
        dic['recom_exhi_5th'] = arr3[4]

        dic['recom_movie_1st'] = arr5[0]
        dic['recom_movie_2nd'] = arr5[1]
        dic['recom_movie_3rd'] = arr5[2]
        dic['recom_movie_4th'] = arr5[3]
        dic['recom_movie_5th'] = arr5[4]

        dic['poster_exhi_1st'] = poster1
        dic['poster_exhi_2nd'] = poster2
        dic['poster_exhi_3rd'] = poster3
        dic['poster_exhi_4th'] = poster4
        dic['poster_exhi_5th'] = poster5

        dic['poster_movie_1st'] = poster11
        dic['poster_movie_2nd'] = poster22
        dic['poster_movie_3rd'] = poster33
        dic['poster_movie_4th'] = poster44
        dic['poster_movie_5th'] = poster55


        try:
          review_all = {}
          review_data = User_review.objects.filter(exhibition_id=id)
          print(review_data)
          for e in review_data:
              # print(e)
              review = {}
              review_id = e.review_id
              review['displayname'] = User.objects.get(username=e.username).display_name
              review['review_title'] = e.title
              review['review_detail'] = e.detail
              review['review_star'] = e.star
              review['review_date'] = e.date_joined
              review_all[f'{review_id}'] = review
          # print(review_all)
        except:
          review_all = {}
        exhibition_map = {}
        exhibition_map['lat'] = ExhibitionPlace.objects.get(place_id=Exhibition.objects.get(exhibition_id=id).place_id).y
        exhibition_map['lng'] = ExhibitionPlace.objects.get(place_id=Exhibition.objects.get(exhibition_id=id).place_id).x
        print(exhibition_map)
        return render(request, 'detail.html', {'data': dic, 'review': review_all, 'map' : exhibition_map})
    else:
        req_dic = {}
        #like 비동기 통신
        username = request.user.username
        exhibition_name = request.POST.get('exhibition_name')
        exhibition_id = Exhibition.objects.get(name=exhibition_name).exhibition_id
        like_status = request.POST.get('like_status')
        if like_status == '1':
            like = User_like.objects.create(
                username=username,
                exhibition_id=exhibition_id,
            )
        else:
            like = User_like.objects.filter(
                username=username,
                exhibition_id=exhibition_id,
            ).delete()
            print('0: ', like)

        return redirect('/')


def insert_proc(request):
    if request.method == 'GET':
        return render(request, 'detail.html')
    else:
        user_id = request.user
        exhibition_id = request.POST['exhibition_id']
        mystar = request.POST['rating']
        mytitle = request.POST['mytitle']
        mycontent = request.POST['mycontent']
        print(user_id)
        print(exhibition_id)
        print(mystar)
        print(mytitle)
        print(mycontent)
        result = User_review.objects.create(username=user_id, exhibition_id=exhibition_id, title=mytitle, detail=mycontent, star=mystar, date_joined=timezone.now())
        print(result)

        return redirect('detail', id=exhibition_id)

def reviews(request):
    user_review = User_review.objects.filter(username=request.user.username)
    review_all = {}
    for e in user_review:
        # print(e)
        review = {}
        id = e.review_id
        exhibition = Exhibition.objects.filter(exhibition_id=e.exhibition_id)[0]
        review['exhibition_id'] = e.exhibition_id
        review['exhibition_name'] = exhibition.name
        review['review_title'] = e.title
        review['review_detail'] = e.detail
        review['review_star'] = e.star
        review['review_date'] = e.date_joined
        review_all[f'{id}'] = review
    return render(request, 'reviews.html', {'review': review_all})

def update_proc(request, id):
    print(id)
    if request.method == 'GET':
        review = User_review.objects.get(review_id=id)
        exhibition_name = Exhibition.objects.get(exhibition_id=review.exhibition_id).name
        return render(request, 'review_update.html', {'review': review, 'exhibition_name' : exhibition_name})

    else:
        user_id = request.user
        exhibition_id = request.POST['exhibition_id']
        mystar = request.POST['rating']
        mytitle = request.POST['mytitle']
        mycontent = request.POST['mycontent']

        myreview = User_review.objects.filter(review_id=id)

        myreview.update(star=mystar)
        result_title = myreview.update(title=mytitle)
        result_content = myreview.update(detail=mycontent)
        # print(f'fifle update : {result_title} /content update : {result_content}')

        if result_content + result_title == 2:
            print("WELL DONE")

        return redirect('reviews')


def delete_proc(request, id):
    result_delete = User_review.objects.filter(review_id=id).delete()
    # print(result_delete)

    return redirect('reviews')



from math import ceil
def search(request):

    def start_end_update(hits):
        r_list = []
        for hit in hits:
            hit['start_period'] = hit['start_period'][:4] + '년 ' + hit['start_period'][5:7]+ '월 ' + hit['start_period'][8:] + '일'
            hit['end_period'] = hit['end_period'][:4] + '년 ' + hit['end_period'][5:7]+ '월 ' + hit['end_period'][8:] + '일'
            r_list.append(hit)
        return r_list

    if request.method == 'GET':
        keyword = request.GET.get('keyword', '')
        if keyword:
            # es = Elasticsearch(['http://35.79.131.28:8960'])
            es = Elasticsearch(['http://110.10.226.208:8960'])
            #if not keyword:
            #    return HttpResponse('검색어를 입력해서 검색을 해주세요')
            res = es.search(index='yogi6_search3',
                            query={"match": {"name.nori_mixed": keyword}}, size=1000)
            hits_list = start_end_update(list(map(lambda x: x['_source'], res['hits']['hits'])))

        else:
            hits_list = []


        paginator = Paginator(hits_list, 8)
        page = request.GET.get('page')
        page_obj = paginator.get_page(page)

        return render(request, 'search.html', {'hits_list': hits_list, 'keyword': keyword, 'page_obj': page_obj})


    else:
        return



def register(request):
    if request.method == "GET":
        return render(request, 'register.html')
    elif request.method == "POST":
        print(request.POST)
        #keys = list(request.POST.keys())
        context = {}
        try:
            req_username = request.POST.get("username", None)
            req_password1 = request.POST.get("password1", None)
            req_password2 = request.POST.get("password2", None)
            req_first_name = request.POST.get('first_name', None)
            req_last_name = request.POST.get('last_name', None)
            req_email = request.POST.get('email', None)
            req_display_name = request.POST.get('display_name', None)
            req_age = request.POST.get('age', None)
            req_sex = request.POST.get('sex', None)
            req_keyword1 = int(request.POST.get('select1', None))
            req_keyword2 = int(request.POST.get('select2', None))
            user_exist_id = User.objects.filter(email=req_username)
            if user_exist_id.exists():
                print('중복된 이메일 입니다.')
            elif req_password1 != req_password2:
                print('비밀번호가 틀립니다')
            else:
                user = User.objects.create(
                    username=req_username,
                    password=req_password1,
                    first_name=req_first_name,
                    last_name=req_last_name,
                    email=req_email,
                    display_name=req_display_name,
                    age=req_age,
                    sex=req_sex,
                    select_keyword=[req_keyword1, req_keyword2],
                )
                user.set_password(req_password1)
                user.save()
                logger_login(request,user, 0)
                auth_login(request, user)
                return redirect('home')

        except Exception as err:
            print(err)
            pass
        return render(request, 'register.html')


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            logger_login(request, user)
            auth_login(request, user)
            return redirect('home')
        else:
            #messages.error(request,'ID 혹은 비밀번호 오류입니다.')
            return redirect('login')
    else:
        return render(request, 'login.html')


def logout(request):
    auth_logout(request)
    return redirect('home')


def mypage(request):
    username = request.user.username
    user_data = User.objects.get(username=username)
    profile = {}
    profile['id'] = user_data.username
    profile['password'] = user_data.password
    profile['first_name'] = user_data.first_name
    profile['last_name'] = user_data.last_name
    profile['email'] = user_data.email
    profile['nickname'] = user_data.display_name
    profile['age'] = user_data.age
    profile['sex'] = user_data.sex

    category_dic = {'0': '대중', '1': '문화재', '2': '미디어아트', '3': '추상', '4': '가족', '5': '글로벌',
                    '6': '수상작', '7': '현대', '8': '과학', '9': '예술', '10': '기타'}

    keywords = user_data.select_keyword
    arr = ast.literal_eval(keywords)
    profile['keyword1'] = category_dic.get(f'{arr[0]}')
    profile['keyword2'] = category_dic.get(f'{arr[1]}')

    # return render(request, 'mypage2.html', {'profile':profile, 'graph':word_cloud(request)})
    return render(request, 'mypage2.html', {'profile':profile})


def statistics(request):
    context = {}
    context['graph'] = word_cloud(request)
    return render(request, 'statistics.html', context)


def likes(request):
    user_like = User_like.objects.filter(username=request.user.username)
    like_all = {}
    for e in user_like:
        # print(e)
        like = {}
        exhibition = Exhibition.objects.filter(exhibition_id=e.exhibition_id)[0]
        like['exhibition_id'] = exhibition.exhibition_id
        like['exhibition_name'] = exhibition.name
        like['poster_link'] = exhibition.poster_link
        like_all[f'{id}'] = like
    print(like_all)
    return render(request, 'likes.html', {'like': like_all})


def logger_login(request, user, register=1):
    logger_login = logging.getLogger("yogi6.login")
    
    userNum = user.id
    if register == 1:
        revisit_time = (date.today() - user.last_login).days
    else:
        revisit_time = 0

    clientip = get_client_ip(request)

    if clientip == '127.0.0.1':
        clientip = '121.134.206.100'
    else:
        pass
    
    request.session['ip'] = clientip
    #print(clientip)
    #user_loc = geocoder.ip(f'{clientip}')
    #print(user_loc)
    #print(user_loc.latlng)

    data={
        'userNum':userNum,
        'revisit_time':revisit_time,
        'clientip':clientip,
    }
    logger_login.info('login', extra=data)
    return

def logger_click(request, target_exhibition, login=1):
    logger_click = logging.getLogger("yogi6.click")

    if login == 0:
      userNum = 0
      select_keyword = None
      sex = None
      age = None
    else:
      userNum = request.user.id
      select_keyword = request.user.select_keyword
      sex = request.user.sex
      age = request.user.age

    exhibition_id = target_exhibition.exhibition_id
    clientip = get_client_ip(request)
    now_date = time.strftime('%Y%m%d')

    data={
        'date': now_date,
        'userNum':userNum,
        'select_keyword':select_keyword,
        'sex':sex,
        'age':age,
        'clientip':clientip,
        'exhibition_id':exhibition_id,
    }
    logger_click.info('click', extra=data)
    return

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

##home page에서 slider 형성##
def recommend_exhibition(request):
  keywords = ast.literal_eval(request.user.select_keyword)
  now_exhibitions = sorted(list(Exhibition.objects.filter(start_period__lt=f'{now}', end_period__gt=f'{now}')), key=lambda x:x.end_period)
  exhibitions = [exh for exh in now_exhibitions if str(keywords[0]) in exh.cluster or str(keywords[1]) in exh.cluster]
  return exhibitions


def near_exhibition(request):

    def find_km(exh):
      return haversine((float(target_lat), float(target_lng)), (float(ExhibitionPlace.objects.get(place_id=exh.place_id).y), float(ExhibitionPlace.objects.get(place_id=exh.place_id).x)), unit='km')
    
    # clientip = request.session['ip']
    clientip = '127.0.0.1'
    if clientip == '127.0.0.1':
      clientip = '121.134.206.100'
    url = f"http://www.geoplugin.net/json.gp?ip={clientip}"
    response = requests.request("GET", url)
    json_obj = response.json()
    target_lat = json_obj['geoplugin_latitude']
    target_lng = json_obj['geoplugin_longitude']
    print(target_lat, target_lng)
    exhibitions = sorted(list(Exhibition.objects.filter(start_period__lt=f'{now}', end_period__gt=f'{now}')), key=lambda x:find_km(x))
    #print(exhibitions)
    return exhibitions

def recent_exhibition():
  exhibitions = sorted(list(Exhibition.objects.filter(start_period__lt=f'{now}', end_period__gt=f'{now}')), key=lambda x:x.start_period, reverse=True)
  return exhibitions

def hot_exhibition():
  now_month = time.strftime('%Y%m%d')[:-2]
#   es = Elasticsearch('http://35.79.131.28:8960')
  es = Elasticsearch('http://110.10.226.208:8960')
  res = es.search(index='yogi6',
                    query={"prefix": {"date": f'{now_month}'}}, size=1000)
  
  exhibitions = list(map(lambda x : x['_source']['exhibition_id'], res['hits']['hits']))
  dic={}
  for exh in exhibitions:
    if dic.get(exh, 0) == 0:
      dic[exh] = 1
    else:
      dic[exh] += 1

  exhibitions = list(map(lambda x:Exhibition.objects.get(exhibition_id=x[0]), sorted(dic.items(), key=lambda x:x[1], reverse=True)))
  return exhibitions

def similar_exhibition(request):
  try:
    username = request.user.username
    exhibition_list = list(map(lambda x: ast.literal_eval(Exhibition.objects.get(exhibition_id=x.exhibition_id).recommend_doc), User_review.objects.filter(username=username)))
    exhibitions = []
    for exhs in exhibition_list:
      for exh in exhs:
        exhibitions.append(Exhibition.objects.get(name=exh))
  except:
    exhibitions = 0
  #print(exhibitions)
  return exhibitions

def deadline_exhibition():
  exhibitions = sorted(list(Exhibition.objects.filter(start_period__lt=f'{now}', end_period__gt=f'{now}')), key=lambda x:x.end_period)
  return exhibitions


# def word_cloud(request):
#   username = request.user.username
#   exhibition_id_list = list(set(map(lambda x:x.exhibition_id, User_review.objects.filter(username=username, star__gt=3.5))))
#   #print(exhibitions)
#   #exhbi
#   col_list = ['exhibition_id', 'description']
#   row_list = []
#   for exh_id in exhibition_id_list:
#     exh_desc = Exhibition.objects.get(exhibition_id=exh_id).description
#     value_list = [exh_id, exh_desc]
#     row_list.append(value_list)
  
#   user_pd = pd.DataFrame(row_list, columns=col_list)
#   print(user_pd)
#   def apply_regular_expression(text):
#     hangul = re.compile('[^ ㄱ-ㅣ 가-힣]') # 한글 추출 규칙: 띄어 쓰기(1개)를 포함한 한글
#     result = hangul.sub('', text) # 위에 설정한 "hangul" 규칙을 "text"에 적용(.sub)시킴
#     return result

#   okt = Okt()
#   okt_nouns = okt.nouns(apply_regular_expression(user_pd['description'][0]))

#   # 불용어 사전
#   stopwords = pd.read_csv("https://raw.githubusercontent.com/yoonkt200/FastCampusDataset/master/korean_stopwords.txt").values.tolist()

#   # 전시 관련 불용어 사전 추가
#   exhi_stopwords = ['전시', '전시회', '대해', '정도', '하나', '보고', '작가', '이번', '통해',
#                   '우리', '지엄', '개최', '년대', '대표', '대한', '서울', '세계', '작품', '한국',
#                   '모두', '사람', '주년', '주제', '위해', '이후', '이자', '참여', '작업', '진행',
#                   '서로', '선정', '분야', '관계', '존재', '구성', '특별', '이야기', '경험', '모습',
#                   '주목', '나볼', '누구', '개관', '이해', '최초', '아티스트', '활동', '자리', '다른',
#                   '주요', '바탕', '시대', '지난', '의미', '지금', '로서', '공간', '시간', '기획', '가장',
#                   '인간', '기록', '인간', '과정', '또한', '순간', '주요', '관련', '가장', '소개', '코로나',
#                   '팬데믹', '자신', '중심', '세기', '공개', '관람', '버튼', '생각', '방문',
#                   '감독', '정말', '조금', '추천', '다시', '진짜', '제대로', '때문', '자체', '별로', '서서',
#                   '매우', '느낌', '인원', '내용', '다만', '아주', '일찍', '역시', '중간', '더욱',
#                   '금지', '입장', '물이', '강추', '예약', '대기', '워낙', '시간대', '안내', '편이', '군데',
#                   '가격', '전시관', '몇개', '계속', '도움', '마스크', '위주', '보기', '등등', '가야', '무조건',
#                   '무언가', '부분', '미리', '최고', '참고', '다행', '거꾸로', '전혀', '작고', '나중', '거의',
#                   '더욱더', '마련']
#   for word in exhi_stopwords:
#     stopwords.append(word)

#     # BoW 백터 생성
#   def text_cleaning(text):
#       korean = re.compile('[^ ㄱ-ㅣ 가-힣]')
#       result = korean.sub('', text)
#       okt = Okt()
#       nouns = okt.nouns(result)
#       nouns = [x for x in nouns if len(x) > 1]
#       nouns = [x for x in nouns if x not in stopwords] # 불용어 제거
#       return nouns

#   vector = CountVectorizer(tokenizer = lambda x: text_cleaning(x))
#   bow_vector = vector.fit_transform(user_pd['description'].tolist())
#   word_list = vector.get_feature_names()
#   count_list = bow_vector.toarray().sum(axis=0)


#   # 단어 - 빈도 매칭
#   word_freq = dict(zip(word_list, count_list))

#   # wordcloud
#   word_cloud = WordCloud(font_path='/home/ubuntu/yogi6/yogi6/yogi6/static/fonts/malgun.ttf', width=400, height=400, max_font_size=100,
#                       background_color='white').generate_from_frequencies(word_freq)
                     
#   # plt.figure(figsize=(15,10), dpi=300)
#   # plt.imshow(word_cloud)
#   # plt.axis('off')

#   # now = time.strftime('%Y%m%d')
#   # path = f'/static/img/{now}-{username}.jpg'
#   # plt.savefig('/home/ubuntu/yogi6/yogi6/yogi6' + path)

#   #fig.patch.set_alpha(0.3)

#   #ax = plt.axes()
#   #ax.set_facecolor("#222222")

#   fig = plt.figure(figsize=(5,5))
#   plt.imshow(word_cloud)

#   #plt 설정 바꾸기
#   plt.axis('off')
#   #ax1 = fig.add_subplot(1,1,1)
#   #ax1.set_facecolor("#222222")

#   imgdata = StringIO()
#   fig.savefig(imgdata, dpi=300, facecolor='#222222', format='svg')
#   imgdata.seek(0)

#   data = imgdata.getvalue()
#   return data