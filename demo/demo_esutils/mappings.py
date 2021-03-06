# -*- coding: utf-8 -*-
from django.db.models.signals import post_save
from django.db.models.signals import post_delete

from django_esutils.mappings import SearchMappingType
from django_esutils.models import post_update

from demo_esutils.models import Article


ARTICLE_MAPPING = {
    'id': {
        'type': 'integer'
    },
    # author
    'author.username': {
        'type': 'string',
    },
    'author.email': {
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
    'category.id': {
        'type': 'integer',
    },
    'category.name': {
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
        'type': 'integer',
    },
    'contributors': {
        'type': 'nested',
        'properties': {
            'username': {'type': 'string'},
            'id': {'type': 'string'}
        }
    },
    'library': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string'},
            'id': {'type': 'string'},
            'number_of_books': {'type': 'string'}
        }
    }
}


class ArticleMappingType(SearchMappingType):

    @classmethod
    def get_model(cls):
        return Article

    @classmethod
    def get_field_mapping(cls):
        return ARTICLE_MAPPING

    def get_object(self):
        return ArticleMappingType.get_object_by_id(self._id)


post_save.connect(ArticleMappingType.on_post_save, sender=Article)
post_delete.connect(ArticleMappingType.on_post_delete, sender=Article)
post_update.connect(ArticleMappingType.on_post_update, sender=Article)
