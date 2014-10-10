# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db import models

from uuidfield import UUIDField


class Category(models.Model):

    name = models.CharField(max_length=128)


ARTICLE_STATUSES = (
    (0, 'draft'),
    (1, 'new'),
    (2, 'online'),
    (3, 'api')
)


class Article(models.Model):

    uuid = UUIDField(auto=True, primary_key=True, hyphenate=True)

    author = models.ForeignKey(User)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    category = models.ForeignKey(Category, blank=True, null=True)

    subject = models.CharField(max_length=256)
    content = models.TextField(blank=True, default='')

    status = models.CharField(max_length=1,
                              choices=ARTICLE_STATUSES,
                              default=0)
