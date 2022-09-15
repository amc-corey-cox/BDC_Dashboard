"""
Django settings for bdcat_data_submission project.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

import datetime
import os, io
import environ
import logging
from google.cloud import secretmanager
from django.utils.timezone import get_current_timezone_name

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# Handle environment variables
# SECURITY WARNING: This defaults to False, but set to True in your env file for local dev
env = environ.Env(DEBUG=(bool, False))

# load .env
env_file = os.path.join(BASE_DIR, ".env")
if os.path.isfile(env_file):
    print(
        "Using local .env file: " + env_file
    )
    # if local env file
    env.read_env(env_file)
elif os.environ.get("GOOGLE_CLOUD_PROJECT", None):
    # if running on GCP, use Secret Manager to get env variables
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")

    client = secretmanager.SecretManagerServiceClient()
    settings_name = os.environ.get("SETTINGS_NAME", "django_settings")
    name = f"projects/{project_id}/secrets/{settings_name}/versions/latest"
    payload = client.access_secret_version(name=name).payload.data.decode("UTF-8")
    env.read_env(io.StringIO(payload))
    print(
        "Using Google Cloud secrets"
    )
else:
    print(
        "No local .env or GOOGLE_CLOUD_PROJECT detected. Using container environment variables."
    )

SECRET_KEY = env("SECRET_KEY")

# debug toolbar
DEBUG = env("DEBUG")
if DEBUG:
    import socket

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[:-1] + "1" for ip in ips] + ["127.0.0.1", "10.0.2.2"]

# SECURITY WARNING: App Engine's security features ensure that it is safe to
# have ALLOWED_HOSTS = ['*'] when the app is deployed. If you deploy a Django
# app not on App Engine, make sure to set an appropriate host here
ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    "tracker",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "widget_tweaks",
    "debug_toolbar",
    # all auth
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
#    "allauth.socialaccount.providers.google",
    # custom nih sso provider
    "nihsso",
    # audit log
    "simple_history",
    # health check
    "health_check",
    "health_check.db",
    "health_check.cache",
    "health_check.storage",
    "health_check.contrib.migrations",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
    "tracker.middleware.CustomHeaderMiddleware"
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "templates"),
            os.path.join(BASE_DIR, "templates", "allauth"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    'formatters': {
        'verbose': {
            'format': '{asctime} {levelname} [{module}] {message}',
            'style': '{',
        },
    },
    "handlers": { 
        "console": {
            "level": os.getenv("DJANGO_LOG_LEVEL", "DEBUG"),
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },        
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "DEBUG"),
            "propagate": True,
        },
    },
}

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases
if os.environ.get("POSTGRES_HOST", None):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": env("POSTGRES_DB"),
            "USER": env("POSTGRES_USER"),
            "PASSWORD": env("POSTGRES_PASSWORD"),
            "HOST": env("POSTGRES_HOST"),
            "PORT": env("POSTGRES_PORT"),
        }
    }


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# django-allauth
# https://github.com/pennersr/django-allauth
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_PROVIDERS = {}

if os.environ.get("GOOGLE_CLIENT_ID", None):
	google_settings = {
		"SCOPE": ["profile", "email", "openid"],
		"AUTH_PARAMS": {
			"access_type": "online",
		},
		"APP": {
			"client_id": env("GOOGLE_CLIENT_ID"),
			"secret": env("GOOGLE_CLIENT_SECRET"),
			"key": "",
		},
	}
	SOCIALACCOUNT_PROVIDERS['google'] = google_settings
	print("Adding Google as an Account Provider")

if os.environ.get("NIH_CLIENT_ID", None):
	nih_settings = {
		"SCOPE": ["openid", "profile", "email", "member"],
		"APP": {
			"client_id": env("NIH_CLIENT_ID"),
			"secret": env("NIH_CLIENT_SECRET"),
			"key": "",
		},
	}
	SOCIALACCOUNT_PROVIDERS['nihsso'] = nih_settings
	NIH_OAUTH_SERVER_TOKEN_URL = os.environ.get("NIH_OAUTH_SERVER_TOKEN_URL")
	NIH_OAUTH_SERVER_INFO_URL = os.environ.get("NIH_OAUTH_SERVER_INFO_URL")
	NIH_OAUTH_SERVER_AUTH_URL= os.environ.get("NIH_OAUTH_SERVER_AUTH_URL")
	print("Adding NIH SSO as an Account Provider")

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

SITE_ID = int(os.environ.get("ALLAUTH_SITE_ID", 3))
AUTH_USER_MODEL = "tracker.User"
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_DEFAULT_HTTP_PROTOCOL = os.environ.get("ACCOUNT_DEFAULT_HTTP_PROTOCOL", "https")
ACCOUNT_EMAIL_VERIFICATION = "none"
SOCIALACCOUNT_ADAPTER = "nihsso.adapters.NIHSSOSocialAccountAdapter"

SESSION_COOKIE_AGE = 30 * 60  # 30 minutes in seconds
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

if os.environ.get("AZURE_SITES_URL", None):
    CSRF_TRUSTED_ORIGINS = [env("AZURE_SITES_URL")]  # this is required for Django 4+


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/
LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/New_York"
USE_I18N = True
USE_L10N = True
USE_TZ = True

DATE_FORMAT = 'N j, Y, P T'
DATETIME_FORMAT = 'N j, Y, P T'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Whitenoise
WHITENOISE_AUTOREFRESH = True
WHITENOISE_MANIFEST_STRICT = False


# SendGrid settings
if os.environ.get("SENDGRID_API_KEY", None):
	EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
	SENDGRID_API_KEY = env("SENDGRID_API_KEY")
	SENDGRID_ADMIN_EMAIL = env("SENDGRID_ADMIN_EMAIL")
	SENDGRID_NO_REPLY_EMAIL = env("SENDGRID_NO_REPLY_EMAIL")
	SENDGRID_SANDBOX_MODE_IN_DEBUG = False
	# sendgrid templates for users
	SENDGRID_TICKET_CREATED_TEMPLATE_ID_USER = env("SENDGRID_TICKET_CREATED_TEMPLATE_ID_USER")
	SENDGRID_TICKET_DELETED_TEMPLATE_ID_USER = env("SENDGRID_TICKET_DELETED_TEMPLATE_ID_USER")
	SENDGRID_TICKET_REJECTED_TEMPLATE_ID_USER = env("SENDGRID_TICKET_REJECTED_TEMPLATE_ID_USER")
	SENDGRID_TICKET_UPDATED_TEMPLATE_ID_USER = env("SENDGRID_TICKET_UPDATED_TEMPLATE_ID_USER")
	SENDGRID_BUCKET_CREATED_TEMPLATE_ID_USER = env("SENDGRID_BUCKET_CREATED_TEMPLATE_ID_USER")
	# sendgrid templates for admins
	SENDGRID_TICKET_CREATED_TEMPLATE_ID_ADMIN = env("SENDGRID_TICKET_CREATED_TEMPLATE_ID_ADMIN")
	SENDGRID_TICKET_DELETED_TEMPLATE_ID_ADMIN = env("SENDGRID_TICKET_DELETED_TEMPLATE_ID_ADMIN")
	SENDGRID_TICKET_UPDATED_TEMPLATE_ID_ADMIN = env("SENDGRID_TICKET_UPDATED_TEMPLATE_ID_ADMIN")
	SENDGRID_DATA_UPLOAD_COMPLETED_TEMPLATE_ID_ADMIN = env("SENDGRID_DATA_UPLOAD_COMPLETED_TEMPLATE_ID_ADMIN")


# Misc
ROOT_URLCONF = "bdcat_data_submission.urls"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"  # Default primary key field type
WSGI_APPLICATION = "bdcat_data_submission.wsgi.application"
