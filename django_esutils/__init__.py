# -*- coding: utf-8 -*-
import pkg_resources
__version__ = pkg_resources.get_distribution(__package__).version

from elasticutils import F  # NOQA
from elasticutils import Q  # NOQA
from elasticutils.contrib.django import S  # NOQA
from elasticutils.contrib.django import tasks  # NOQA
