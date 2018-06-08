# -*- coding: utf-8 -*-
"""
Settings for tests
"""
from __future__ import unicode_literals

INSTALLED_APPS = [
    # core django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # third party
    'sorl.thumbnail',
    'private_storage',
    'phonenumber_field',
    'crispy_forms',
    # custom
    'small_small_hr.apps.SmallSmallHrConfig',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'small_small_hr',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': '127.0.0.1'
    }
}

TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_L10N = True
USE_TZ = True

SECRET_KEY = "i love oov"

PRIVATE_STORAGE_ROOT = '/path/to/private-media/'
PRIVATE_STORAGE_AUTH_FUNCTION = 'private_storage.permissions.allow_staff'

# try and load local_settings if present
try:
    # pylint: disable=wildcard-import
    # pylint: disable=unused-wildcard-import
    from .local_settings import *  # noqa
except ImportError:
    pass
