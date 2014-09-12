# -*- coding: utf-8 -*-

# Applications, dependencies.
INSTALLED_APPS = [
    'django.contrib.sessions',
    'django.contrib.messages',
    # libs
    'django_nose',
    # Project's.
    'django_esutils',
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
