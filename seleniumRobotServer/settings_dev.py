"""
Django settings for seleniumRobotServer project.

Generated by 'django-admin startproject' using Django 1.10.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""
# Login/ mdp: admin / adminServer
import os
import ldap
from django_auth_ldap.config import LDAPSearch

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'snapshotServer.app.SnapshotServerConfig',
    'variableServer.app.VariableserverConfig',
    'commonsServer.apps.CommonsserverConfig',
    'elementInfoServer.app.ElementinfoserverConfig',
    'django_nose',
]

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = [
    '--with-coverage',
    '--with-xunit',
    '--cover-package=snapshotServer',
    '--cover-package=variableServer',
    '--cover-package=elementInfServer',
    '--cover-branches',
    '--cover-inclusive',
    '--cover-erase',
    '--cover-html',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'seleniumRobotServer.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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


AUTHENTICATION_BACKENDS = (
    "seleniumRobotServer.ldapbackends.LDAPBackend1", #"seleniumRobotServer.ldapbackends.LDAPBackend2", "seleniumRobotServer.ldapbackends.LDAPBackend3",
    'django.contrib.auth.backends.ModelBackend',
)

WSGI_APPLICATION = 'seleniumRobotServer.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
     'default': {
         'ENGINE': 'django.db.backends.sqlite3',
         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
     }
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'seleniumServer',
#         'USER': 'seleniumRobot',
#         'PASSWORD': 'robotDb',
#         'HOST': '',
#         'PORT': '',
#     }
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# REST_FRAMEWORK = {
#     # Use Django's standard `django.contrib.auth` permissions,
#     'DEFAULT_PERMISSION_CLASSES': [
#         'rest_framework.permissions.DjangoModelPermissions'
#     ],
#     'DEFAULT_AUTHENTICATION_CLASSES': [
#         'rest_framework.authentication.TokenAuthentication'
#     ]
# }
REST_FRAMEWORK = {
    # allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny'
    ]
}

os.makedirs(os.path.join(BASE_DIR, 'log'), exist_ok=True)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'simple': {
            'format': '[%(asctime)s] %(levelname)s %(message)s',
        'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
        'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': { 
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'development_logfile': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.FileHandler',
            'filename': BASE_DIR + '/log/django_dev.log',
            'formatter': 'verbose'
        },
        'production_logfile': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'logging.FileHandler',
            'filename': BASE_DIR + '/log/django_production.log',
            'formatter': 'simple'
        },
        'dba_logfile': {
            'level': 'DEBUG',
            'filters': ['require_debug_false','require_debug_true'],
            'class': 'logging.FileHandler',
            'filename': BASE_DIR + '/log/django_dba.log', 
            'formatter': 'simple'
        },
    },
    'loggers': {
        'snapshotServer': {
            'handlers': ['console','development_logfile','production_logfile'],
            'level': 'DEBUG',
         },
        'django': {
            'handlers': ['console','development_logfile','production_logfile'],
        },
        'py.warnings': {
            'handlers': ['console','development_logfile'],
        },
        'django_auth_ldap': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    }
}

# -------- Application specific flags ------------
# whether we restrict the view/change/delete/add to the user, in admin view to only applications he has rights for (issue #28)
RESTRICT_ACCESS_TO_APPLICATION_IN_ADMIN = False

# first LDAP server configuration
AUTH_LDAP_1_SERVER_URI = "ldap://mycompany.com:389"
AUTH_LDAP_1_BIND_DN = 'CN=user,OU=ou,DC=company,DC=com'
AUTH_LDAP_1_BIND_PASSWORD = 'pwd'
AUTH_LDAP_1_USER_SEARCH = LDAPSearch("OU=ou,DC=company,DC=com", ldap.SCOPE_SUBTREE, "(uid=%(user)s)")

# second LDAP server configuration (uncomment "seleniumRobotServer.ldapbackends.LDAPBackend2" in AUTHENTICATION_BACKENDS to use it)
AUTH_LDAP_2_SERVER_URI = "ldap://mycompany.com:389"
AUTH_LDAP_2_BIND_DN = 'CN=user,OU=ou,DC=company,DC=com'
AUTH_LDAP_2_BIND_PASSWORD = 'pwd'
AUTH_LDAP_2_USER_SEARCH = LDAPSearch("OU=ou,DC=company,DC=com", ldap.SCOPE_SUBTREE, "(uid=%(user)s)")

# third LDAP server configuration (uncomment "seleniumRobotServer.ldapbackends.LDAPBackend3" in AUTHENTICATION_BACKENDS to use it)
AUTH_LDAP_3_SERVER_URI = "ldap://mycompany.com:389"
AUTH_LDAP_3_BIND_DN = 'CN=user,OU=ou,DC=company,DC=com'
AUTH_LDAP_3_BIND_PASSWORD = 'pwd'
AUTH_LDAP_3_USER_SEARCH = LDAPSearch("OU=ou,DC=company,DC=com", ldap.SCOPE_SUBTREE, "(uid=%(user)s)")

