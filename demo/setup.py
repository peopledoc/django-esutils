# -*- coding: utf-8 -*-
"""Python packaging."""
import os
from setuptools import setup


here = os.path.abspath(os.path.dirname(__file__))

NAME = u'demo_esutils'
DESCRIPTION = u'Demo for django-esutils.'
README = open(os.path.join(here, 'README')).read()
VERSION = open(os.path.join(os.path.dirname(here), 'VERSION')).read().strip()
PACKAGES = ['demo_esutils']
REQUIREMENTS = ['django-esutils']
ENTRY_POINTS = {
    'console_scripts': ['demo_esutils = demo_esutils.manage:main'],
}
AUTHOR = u'Novapost'
EMAIL = u'rd@novapost.net'
URL = u'https://github.com/novapost/django-esutils'
CLASSIFIERS = ['Development Status :: 3 - Alpha',
               "Programming Language :: Python :: 2.7"]
KEYWORDS = []


if __name__ == '__main__':  # Don't run setup() when we import this module.
    setup(name=NAME,
          version=VERSION,
          description=DESCRIPTION,
          long_description=README,
          classifiers=CLASSIFIERS,
          keywords=' '.join(KEYWORDS),
          author=AUTHOR,
          author_email=EMAIL,
          url=URL,
          packages=PACKAGES,
          include_package_data=True,
          zip_safe=False,
          install_requires=REQUIREMENTS,
          entry_points=ENTRY_POINTS)
