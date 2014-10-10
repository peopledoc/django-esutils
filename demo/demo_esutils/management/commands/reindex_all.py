# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from demo_esutils.mappings import ArticleMappingType


AVAILABLE_MAPPING_TYPES = [
    ArticleMappingType,
]


class Command(BaseCommand):
    args = "reindex_all"
    help = """Reindexes all values in ES."""
    option_list = BaseCommand.option_list

    def handle(self, *args, **options):
        for m_type in AVAILABLE_MAPPING_TYPES:
            m_type.es_index_all()
