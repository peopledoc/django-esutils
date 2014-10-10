# -*- coding: utf-8 -*-
from django.db.models.signals import post_save
from django.db.models.signals import post_delete

from django_esutils.mappings import SearchMappingType

from demo_esutils.models import Article


ARTICLE_MAPPING = {
    # author
    'author__username': {
        'type': 'string',
    },
    'author__email': {
        'type': 'string',
        'index': 'not_analyzed'
    },
    # created
    'created_at': {
        'type': 'date',
    },
    # updated
    'updated_at': {
        'type': 'date',
    },
    # category
    'category_id': {
        'type': 'integer',
    },
    'category__name': {
        'type': 'string',
    },
    # subject
    'subject': {
        'type': 'string',
    },
    # content
    'content': {
        'type': 'string',
    },
    # status
    'status': {
        'type': 'string',
    },
}


class ArticleMappingType(SearchMappingType):

    id_field = 'uuid'

    @classmethod
    def get_model(cls):
        return Article

    @classmethod
    def get_field_mapping(cls):
        return ARTICLE_MAPPING


post_save.connect(ArticleMappingType.es_index, sender=Article)
post_delete.connect(ArticleMappingType.es_unindex, sender=Article)
