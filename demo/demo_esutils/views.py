from django.http import HttpResponse
from django.views.generic import ListView

from demo_esutils.models import Category
from demo_esutils.models import Article
from demo_esutils.models import User
from demo_esutils.mappings import ArticleMappingType as M
from django_esutils.filters import ElasticutilsFilterSet
from django_esutils.filters import ElasticutilsFilterBackend


class ArticleListView(ListView):
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
                     'contributors']


    def get_queryset(self):
        # detail views
        return self.mapping_type.query()

    