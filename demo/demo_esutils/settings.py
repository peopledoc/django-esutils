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
    'freezegun',
]

# Databases.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'demo_esutils.db',
    }
}

# URL configuration.
ROOT_URLCONF = 'demo_esutils.urls'

# Fake secret key.
SECRET_KEY = 'Fake secret.'

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

NOSE_ARGS = [
    '--verbosity=2',
    '--nocapture',
    '--no-path-adjustment',
    '--all-modules',
    '--cover-inclusive',
    '--cover-tests',
]

PASSWORD_HASHERS = (
    'django_ticketoffice.utils.PlainPasswordHasher',
)

AUTH_USER_MODEL = 'demo_esutils.User'

# Specific test settings - do not delay
CELERY_ALWAYS_EAGER = True

ES_URLS = [
    'http://127.0.0.1:9200',
]
# @see for additionals available kwargs:
# - http://elasticsearch-py.readthedocs.org/en/master/connection.html#elasticsearch.Transport   # noqa
# - http://elasticsearch-py.readthedocs.org/en/master/connection.html#elasticsearch.Connection  # noqa
ELASTICSEARCH_KWARGS = {}

ES_DISABLED = False

ES_INDEX_DEFAULT = 'demo_esutils'

ES_INDEXES = {
    'default': [
        ES_INDEX_DEFAULT,
    ]
}

ES_INDEX_SETTINGS = {
    'index': {
        'number_of_replicas': 1,
        'number_of_shards': 1,
        'analysis': {
            'analyzer': {
                'ngram_analyzer': {
                    'type': 'custom',
                    'filter': [
                        'esutils_ngram'
                    ],
                    'tokenizer': 'lowercase'
                },
                'edgengram_analyzer': {
                    'type': 'custom',
                    'filter': [
                        'esutils_edgengram'
                    ],
                    'tokenizer': 'lowercase'
                }
            },
            'filter': {
                'esutils_edgengram': {
                    'type': 'edgeNGram',
                    'min_gram': 2,
                    'max_gram': 15
                },
                'esutils_ngram': {
                    'min_gram': 3,
                    'type': 'nGram',
                    'max_gram': 15
                }
            },
            'tokenizer': {
                'esutils_ngram_tokenizer': {
                    'min_gram': 3,
                    'type': 'nGram',
                    'max_gram': 15
                },
                'esutils_edgengram_tokenizer': {
                    'max_gram': 15,
                    'min_gram': 2,
                    'type': 'edgeNGram',
                    'side': 'front'
                }
            }
        }
    }
}

ES_DOC_TYPES = [
    'article',
]

ES_SOURCE_ENABLED = True

TIME_ZONE = 'Europe/Paris'

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware'
)

try:
    from local_settings import *
except ImportError:
    pass
