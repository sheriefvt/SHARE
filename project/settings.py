"""
Django settings for share project.

Generated by 'django-admin startproject' using Django 1.9.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
import subprocess

from django.utils.log import DEFAULT_LOGGING

from celery.schedules import crontab

# Suppress select django deprecation messages
LOGGING = DEFAULT_LOGGING

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'c^0=k9r3i2@kh=*=(w2r_-sc#fd!+b23y%)gs+^0l%=bt_dst0')

SALT = os.environ.get('SALT', 'r_-78y%c^(w2_ds0d*=t!+c=s+^0l=bt%2isc#f2@kh=0k5r)g')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(os.environ.get('DEBUG', True))

if 'VERSION' not in os.environ and DEBUG:
    try:
        VERSION = subprocess.check_output(['git', 'describe']).decode().strip()
    except subprocess.CalledProcessError:
        VERSION = 'UNKNOWN'
else:
    VERSION = os.environ.get('VERSION') or 'UNKNOWN'

ALLOWED_HOSTS = [h for h in os.environ.get('ALLOWED_HOSTS', '').split(' ') if h]

AUTH_USER_MODEL = 'share.ShareUser'

JSON_API_FORMAT_KEYS = 'camelize'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'django_celery_beat',

    'django_filters',
    'django_extensions',
    'oauth2_provider',
    'rest_framework',
    'corsheaders',
    'revproxy',
    'graphene_django',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # not yet
    # 'allauth.socialaccount.providers.orcid',
    # 'allauth.socialaccount.providers.github',
    # 'allauth.socialaccount.providers.google',
    'osf_oauth2_adapter',

    'share',
    'api',

    'bots.elasticsearch',
]

HARVESTER_SCOPES = 'upload_normalized_manuscript upload_raw_data'
USER_SCOPES = 'approve_changesets'

OAUTH2_PROVIDER = {
    'SCOPES': {
        'read': 'Read scope',
        'write': 'Write scope',
        'groups': 'Access to your groups',
        'upload_normalized_manuscript': 'Upload Normalized Manuscript',
        'upload_raw_data': 'Upload Raw Data',
        'approve_changesets': 'Approve ChangeSets'
    }
}
SOCIALACCOUNT_ADAPTER = 'osf_oauth2_adapter.views.OSFOAuth2Adapter'
SOCIALACCOUNT_PROVIDERS = \
    {'osf':
        {
            'METHOD': 'oauth2',
            'SCOPE': ['osf.users.profile_read'],
            'AUTH_PARAMS': {'access_type': 'offline'},
            # 'FIELDS': [
            #     'id',
            #     'email',
            #     'name',
            #     'first_name',
            #     'last_name',
            #     'verified',
            #     'locale',
            #     'timezone',
            #     'link',
            #     'gender',
            #     'updated_time'],
            # 'EXCHANGE_TOKEN': True,
            # 'LOCALE_FUNC': 'path.to.callable',
            # 'VERIFIED_EMAIL': False,
            # 'VERSION': 'v2.4'
        }
     }


APPLICATION_USERNAME = 'system'

REST_FRAMEWORK = {
    'PAGE_SIZE': 10,
    'ORDERING_PARAM': 'sort',
    'EXCEPTION_HANDLER': 'rest_framework_json_api.exceptions.exception_handler',
    'DEFAULT_PAGINATION_CLASS': 'api.pagination.FuzzyPageNumberPagination',
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework_json_api.parsers.JSONParser',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'api.renderers.HideNullJSONAPIRenderer',
        # 'rest_framework_json_api.renderers.JSONRenderer',
        # 'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_METADATA_CLASS': 'rest_framework_json_api.metadata.JSONAPIMetadata',
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticatedOrReadOnly',),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.ext.rest_framework.OAuth2Authentication',
        'rest_framework.authentication.SessionAuthentication',
        # 'api.authentication.NonCSRFSessionAuthentication',
    ),
}

GRAPHENE = {
    'SCHEMA': 'share.graphql.schema.schema'
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

INTERNAL_IPS = ['127.0.0.1']

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'db.backends.postgresql',
        'NAME': os.environ.get('DATABASE_NAME', 'share'),
        'USER': os.environ.get('DATABASE_USER', 'postgres'),
        'HOST': os.environ.get('DATABASE_HOST', 'localhost'),
        'PORT': os.environ.get('DATABASE_PORT', '5432'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD', None),
        'CONN_MAX_AGE': int(os.environ.get('CONN_MAX_AGE', 60)),
        'TEST': {'SERIALIZE': False},
    },
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LOGIN_REDIRECT_URL = os.environ.get('LOGIN_REDIRECT_URL', 'http://localhost:8000/')

if DEBUG:
    AUTH_PASSWORD_VALIDATORS = []
# else:
if os.environ.get('USE_SENTRY'):
    INSTALLED_APPS += [
        'raven.contrib.django.raven_compat',
    ]
    RAVEN_CONFIG = {
        'dsn': os.environ.get('SENTRY_DSN', None),
        'release': os.environ.get('GIT_COMMIT', None),
    }


# TODO REMOVE BEFORE PRODUCTION
# ALLOW LOCAL USERS TO SEARCH
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
# TODO REMOVE BEFORE PRODUCTION

ANONYMOUS_USER_NAME = 'AnonymousUser'
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',  # this is default
    'allauth.account.auth_backends.AuthenticationBackend',
    # 'guardian.backends.ObjectPermissionBackend',
)

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATICFILES_DIRS = (
    os.path.join(os.path.dirname(__file__), 'static'),
)

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL', 'http://localhost:9200/')
ELASTICSEARCH_INDEX = os.environ.get('ELASTIC_SEARCH_INDEX', 'share')
ELASTICSEARCH_TIMEOUT = int(os.environ.get('ELASTICSEARCH_TIMEOUT', '45'))
ELASTICSEARCH_INDEX_VERSIONS = tuple(v for v in os.environ.get('ELASTICSEARCH_INDEX_VERSIONS', '').split(',') if v)

INDEXABLE_MODELS = {
    'agent': 'Agent',
    'creativework': 'CreativeWork',
    'subject': 'Subject',
    'tag': 'Tag',
}

# Seconds, not an actual celery settings
CELERY_RETRY_BACKOFF_BASE = int(os.environ.get('CELERY_RETRY_BACKOFF_BASE', 2 if DEBUG else 10))

# Celery Settings

CELERY_TIMEZONE = 'UTC'
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'amqp://'),

CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_BEAT_SCHEDULE = {
    # Once a minute
    'Update Search': {
        'task': 'bots.elasticsearch.tasks.update_elasticsearch',
        'schedule': 60,
    },
    # Every 2 minutes
    'Harvest Task': {
        'task': 'share.tasks.harvest',
        'schedule': 120,
    },
    # Executes daily at 11:30 P.M
    'Elasticsearch Janitor': {
        'task': 'bots.elasticsearch.tasks.elasticsearch_janitor',
        'schedule': crontab(hour=23, minute=30),
    },
}

if not DEBUG:
    CELERY_BEAT_SCHEDULE = {
        **CELERY_BEAT_SCHEDULE,
        'Schedule Harvests': {
            'task': 'share.tasks.schedule_harvests',
            'schedule': crontab(minute=0)  # hourly
        },
        'RawData Janitor': {
            'task': 'share.janitor.tasks.rawdata_janitor',
            'schedule': crontab(minute=0)  # hourly
        },
        'Source Stats': {
            'task': 'share.tasks.source_stats',
            'schedule': crontab(minute=0, hour='3,9,15,21'),  # every 6 hours
            'args': (),
        },
    }

CELERY_RESULT_EXPIRES = 60 * 60 * 24 * 3  # 4 days
CELERY_RESULT_BACKEND = 'share.celery:CeleryDatabaseBackend'

# Don't reject tasks that were present on a worker when it was killed
CELERY_TASK_REJECT_ON_WORKER_LOST = False

# Don't remove tasks from RabbitMQ until they are finished
CELERY_TASK_ACKS_LATE = True

CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 60 * 60 * 3  # 3 Hours

CELERY_TASK_DEFAULT_QUEUE = 'share_default'
CELERY_TASK_DEFAULT_EXCHANGE = 'share_default'
CELERY_TASK_DEFAULT_ROUTING_KEY = 'share_default'

CELERY_TASK_ROUTES = {
    'bots.elasticsearch.*': {'priority': 50, 'queue': 'elasticsearch'},
    'share.tasks.harvest': {'priority': 0, 'queue': 'harvest'},
    'share.tasks.transform': {'priority': 20, 'queue': 'transform'},
    'share.tasks.disambiguate': {'priority': 35, 'queue': 'disambiguate'},
}

CELERY_TASK_QUEUES = {q['queue']: {} for q in CELERY_TASK_ROUTES.values()}
CELERY_TASK_QUEUES[CELERY_TASK_DEFAULT_QUEUE] = {}

ELASTIC_QUEUE = 'es-index'
ELASTIC_QUEUE_SETTINGS = {
    'serializer': 'json',
    'compression': 'zlib',
    'no_ack': False,  # WHY KOMBU THAT'S NOT HOW ENGLISH WORKS
}

# Logging
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'WARNING').upper()

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            '()': 'colorlog.ColoredFormatter',
            'format': '%(cyan)s[%(asctime)s]%(log_color)s[%(levelname)s][%(name)s]: %(reset)s%(message)s'
        }
    },
    'handlers': {
        'sentry': {
            'level': 'ERROR',  # To capture more than ERROR, change to WARNING, INFO, etc.
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
            'tags': {'custom-tag': 'x'},
        },
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'console'
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False
        },
        'bots': {
            'handlers': ['console'],
            'level': LOG_LEVEL,
            'propagate': False
        },
        'providers': {
            'handlers': ['console'],
            'level': LOG_LEVEL,
            'propagate': False
        },
        'share': {
            'handlers': ['console'],
            'level': LOG_LEVEL,
            'propagate': False
        },
        'share.search.daemon': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False
        },
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
    },
    'root': {
        'level': 'WARNING',
        'handlers': ['sentry'],
    }
}

# shell_plus convenience utilities
SHELL_PLUS_POST_IMPORTS = (
    ('share.shell_util', '*'),
)


# Custom Settings
SITE_ID = 1
PUBLIC_SENTRY_DSN = os.environ.get('PUBLIC_SENTRY_DSN')

EMBER_SHARE_PREFIX = os.environ.get('EMBER_SHARE_PREFIX', 'share' if DEBUG else '')
EMBER_SHARE_URL = os.environ.get('EMBER_SHARE_URL', 'http://localhost:4200').rstrip('/') + '/'
SHARE_API_URL = os.environ.get('SHARE_API_URL', 'http://localhost:8000').rstrip('/') + '/'
SHARE_WEB_URL = os.environ.get('SHARE_WEB_URL', SHARE_API_URL + EMBER_SHARE_PREFIX).rstrip('/') + '/'
SHARE_USER_AGENT = os.environ.get('SHARE_USER_AGENT', 'SHAREbot/{} (+{})'.format(VERSION, SHARE_WEB_URL))

OSF_API_URL = os.environ.get('OSF_API_URL', 'https://staging-api.osf.io').rstrip('/') + '/'
DOI_BASE_URL = os.environ.get('DOI_BASE_URL', 'http://dx.doi.org/')

ALLOWED_TAGS = ['abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'strong', 'ul']

SUBJECTS_CENTRAL_TAXONOMY = os.environ.get('SUBJECTS_CENTRAL_TAXONOMY', 'bepress')

# API KEYS
DATAVERSE_API_KEY = os.environ.get('DATAVERSE_API_KEY')
PLOS_API_KEY = os.environ.get('PLOS_API_KEY')
SPRINGER_API_KEY = os.environ.get('SPRINGER_API_KEY')
RESEARCHREGISTRY_APPLICATION_ID = os.environ.get('RESEARCHREGISTRY_APPLICATION_ID', '54a1ac1032e4beb07e04ac2c')
RESEARCHREGISTRY_API_KEY = os.environ.get('RESEARCHREGISTRY_API_KEY', 'renderer')
MENDELEY_API_CLIENT_ID = os.environ.get('MENDELEY_API_CLIENT_ID')
MENDELEY_API_CLIENT_SECRET = os.environ.get('MENDELEY_API_CLIENT_SECRET')

# Amazon Web Services Credentials
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
CELERY_TASK_BUCKET_NAME = os.environ.get('CELERY_TASK_BUCKET_NAME')
CELERY_TASK_FOLDER_NAME = os.environ.get('CELERY_TASK_FOLDER_NAME')  # top level folder (e.g. prod, staging)


if DEBUG and os.environ.get('TOOLBAR', False):
    INSTALLED_APPS += ('debug_toolbar', )
    MIDDLEWARE += ('debug_toolbar.middleware.DebugToolbarMiddleware', )
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda _: True
    }
    ALLOWED_HOSTS.append('localhost')

if DEBUG and os.environ.get('PROF', False):
    MIDDLEWARE += ('api.middleware.ProfileMiddleware', )
