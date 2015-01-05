# -*- coding: utf-8 -*-
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now

from django_esutils.models import ESManager


class User(AbstractUser):
    language = models.CharField(max_length=10, default='fr')


class Category(models.Model):

    name = models.CharField(max_length=128)


ARTICLE_STATUSES = (
    (0, 'draft'),
    (1, 'new'),
    (2, 'online'),
    (3, 'api')
)


class Article(models.Model):

    author = models.ForeignKey(User, related_name='author')

    contributors = models.ManyToManyField(User, related_name='contributors')

    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)

    category = models.ForeignKey(Category, blank=True, null=True)

    subject = models.CharField(max_length=256)
    content = models.TextField(blank=True, default='')

    status = models.IntegerField(choices=ARTICLE_STATUSES,
                                 default=0)

    objects = ESManager()
