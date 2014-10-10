# -*- coding: utf-8 -*-

# Applications, dependencies.
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    # libs
    'django_nose',
    # Project's.
    'django_esutils',
    # for testing
    'demo_esutils',
]

# Databases.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'demo_esutils.db',
    }
}

# URL configuration.
ROOT_URLCONF = '{package}.urls'.format(package=__package__)

# Fake secret key.
SECRET_KEY = 'Fake secret.'

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

NOSE_ARGS = [
    '--verbosity=2',
    '--nocapture',
    '--rednose',
    '--no-path-adjustment',
    '--all-modules',
    '--cover-inclusive',
    '--cover-tests',
]

PASSWORD_HASHERS = (
    'django_ticketoffice.utils.PlainPasswordHasher',
)

# Specific test settings - do not delay
CELERY_ALWAYS_EAGER = True

ES_URLS = [
    'http://127.0.0.1:9200',
]
# @see for additionals available kwargs:
# - http://elasticsearch-py.readthedocs.org/en/master/connection.html#elasticsearch.Transport
# - http://elasticsearch-py.readthedocs.org/en/master/connection.html#elasticsearch.Connection
ELASTICSEARCH_KWARGS = {}

ES_DISABLED = False

ES_INDEX_DEFAULT = 'demo_esutils'

ES_INDEXES = {
    'default': [
        ES_INDEX_DEFAULT,
    ]
}

ES_INDEX_SETTINGS = {
}

ES_DOC_TYPES = [
    'article',
]

ES_SOURCE_ENABLED = True
