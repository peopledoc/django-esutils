# -*- coding: utf-8 -*-
"""URL configuration."""

from django.conf.urls import url
from demo_esutils.views import ArticleListView
from demo_esutils.views import ArticleRestListView
from demo_esutils.views import ArticleRestListView2

urlpatterns = [
    url(r'^articles/$', ArticleListView.as_view(), name='article_list'),
    url(r'^articles/rest/$', ArticleRestListView.as_view(), name='rest_article_list'),  # noqa
    url(r'^articles/rest2/$', ArticleRestListView2.as_view(), name='s_rest_list'),  # noqa
]
