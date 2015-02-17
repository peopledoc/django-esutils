from django.http import HttpResponse
from django.views.generic import ListView

from rest_framework import serializers
from rest_framework.generics import ListAPIView

from demo_esutils.models import Category
from demo_esutils.models import Article
from demo_esutils.models import User
from demo_esutils.mappings import ArticleMappingType as M
from django_esutils.mappings import SearchMappingType

from django_esutils.filters import ElasticutilsFilterSet
from django_esutils.filters import ElasticutilsFilterBackend


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id',
                  'subject',
                  'content']

    def to_native(self, obj):
        if isinstance(obj, SearchMappingType):
            obj = obj.get_object()
        return super(ArticleSerializer, self).to_native(obj)

    def getlist(self, dictionary, key):
        return getlist(dictionary, key)


class BaseArticleListView(object):

    model = Article
    filter_class = ElasticutilsFilterSet
    filter_backends = (
        ElasticutilsFilterBackend,
    )
    mapping_type = M
    search_fields = ['author.username',
                     'author.email',
                     'category_id',
                     'category.name',
                     'created_at',
                     'subject',
                     'content',
                     'status',
                     'contributors',
                     'library']

    def get_queryset(self):
        # detail views
        return self.mapping_type.query()


class ArticleListView(BaseArticleListView, ListView):
    def get_queryset(self):
        # detail views
        queryset = self.mapping_type.query()

        return self.filter_queryset(queryset)

    def filter_queryset(self, queryset):
        for backend in self.filter_backends:
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset


class ArticleRestListView(BaseArticleListView, ListAPIView):
    serializer_class = ArticleSerializer


class ArticleRestListView2(BaseArticleListView, ListAPIView):
    serializer_class = ArticleSerializer
    all_filter = 'trololo'
