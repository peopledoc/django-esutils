# -*- coding: utf-8 -*-
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now

from django_esutils.models import ESManager

from uuidfield import UUIDField


class User(AbstractUser):
    uuid = UUIDField(auto=True, hyphenate=True)


class Category(models.Model):

    name = models.CharField(max_length=128)


ARTICLE_STATUSES = (
    (0, 'draft'),
    (1, 'new'),
    (2, 'online'),
    (3, 'api')
)


class Article(models.Model):

    uuid = UUIDField(auto=True, hyphenate=True)

    author = models.ForeignKey(User)

    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)

    category = models.ForeignKey(Category, blank=True, null=True)

    subject = models.CharField(max_length=256)
    content = models.TextField(blank=True, default='')

    status = models.CharField(max_length=1,
                              choices=ARTICLE_STATUSES,
                              default=0)

    objects = ESManager()
