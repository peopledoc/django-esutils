# -*- coding: utf-8 -*-
"""URL configuration."""

from django.conf.urls import url
from demo_esutils.views import ArticleListView

urlpatterns = [
    url(r'^articles/$', ArticleListView.as_view()),
]
