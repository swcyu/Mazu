# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    display_name = models.CharField(max_length=45, blank=True, null=True)
    select_keyword = models.CharField(max_length=45, blank=True, null=True)
    sex = models.CharField(max_length=45, blank=True, null=True)
    age = models.CharField(max_length=45, blank=True, null=True)
    since_from = models.DateField(blank=True, null=True)
    last_login = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'yogi6_user'


class User_like(models.Model):
    like_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150)
    exhibition_id = models.CharField(max_length=45)

    class Meta:
        managed = False
        db_table = 'yogi6_user_like'

class User_review(models.Model):
    review_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150)
    exhibition_id = models.CharField(max_length=45)
    title = models.CharField(max_length=150)
    detail = models.TextField()
    star = models.FloatField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'yogi6_user_review'

class Book(models.Model):
    book_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=500, blank=True, null=True)
    writer = models.CharField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'book'


class Movie(models.Model):
    movie_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=500, blank=True, null=True)
    poster_link = models.CharField(max_length=500, blank=True, null=True)
    director = models.CharField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'movie'


class Exhibition(models.Model):
    exhibition_id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=500, blank=True, null=True)
    poster_link = models.CharField(max_length=500, blank=True, null=True)
    detail_place = models.CharField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    start_period = models.DateField(blank=True, null=True)
    end_period = models.DateField(blank=True, null=True)
    place_id = models.CharField(max_length=50, blank=True, null=True)
    recommend_exhi = models.CharField(max_length=500, blank=True, null=True)
    recommend_book = models.CharField(max_length=500, blank=True, null=True)
    recommend_movie= models.CharField(max_length=500, blank=True, null=True)
    recommend_doc= models.CharField(max_length=500, blank=True, null=True)
    cluster = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'exhibition'


class ExhibitionPlace(models.Model):
    place_id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=500, blank=True, null=True)
    address = models.CharField(max_length=500, blank=True, null=True)
    x = models.FloatField(blank=True, null=True)
    y = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'exhibition_place'

class Summary(models.Model):
    summary_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=500)
    rating = models.IntegerField()
    summary = models.TextField(blank=True, null=True)
    star = models.FloatField()
    review_num = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'summary'