# -*- coding: utf-8 -*-
import pkg_resources
__version__ = pkg_resources.get_distribution(__package__).version


from demo_esutils.celery_app import app  # NOQA
