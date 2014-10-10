# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from demo_esutils.mappings import ArticleMappingType


AVAILABLE_MAPPING_TYPES = [
    ArticleMappingType,
]


class Command(BaseCommand):
    args = "update_mapping"
    help = """Creates and/or updates index and mappings."""
    option_list = BaseCommand.option_list

    def handle(self, *args, **options):
        for m_type in AVAILABLE_MAPPING_TYPES:
            m_type.update_mapping()
