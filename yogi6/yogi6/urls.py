"""yogi6 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name='home'),
    path("detail/<int:id>/", views.detail, name='detail'),
    path("register/", views.register, name='register'),
    path("login/", views.login, name='login'),
    path("logout/", views.logout, name='logout'),
    path("mypage/", views.mypage, name='mypage'),
    path("insert/", views.insert_proc, name='insert'),
    path("mypage/likes", views.likes, name='likes'),
    path("mypage/reviews", views.reviews, name='reviews'),
    path('mypage/reviews/update/<int:id>', views.update_proc, name='update'),
    path('mypage/reviews/delete/<int:id>', views.delete_proc, name='delete'),
    path("mypage/statistics", views.statistics, name='statistics'),
    path("search/", views.search, name='search'),
    path("category/<int:id>/", views.CategoryListView.as_view(), name='category'),
]
