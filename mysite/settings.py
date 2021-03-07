# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Django settings for mysite project.

Generated by 'django-admin startproject' using Django 3.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""
import io
import os

import environ


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_file = os.path.join(BASE_DIR, ".env")


env = environ.Env()
# If no .env has been provided, pull it from Secret Manager
if os.path.isfile(env_file):
    env.read_env(env_file)
else:
    # Create local settings if running with CI, for unit testing
    if os.getenv("TRAMPOLINE_CI", None):
        placeholder = f"SECRET_KEY=a\nGS_BUCKET_NAME=none\nDATABASE_URL=sqlite:///{os.path.join(BASE_DIR, 'db.sqlite3')}"
        env.read_env(io.StringIO(placeholder))
    else:
        # [START cloudrun_django_secretconfig]
        import google.auth
        from google.cloud import secretmanager

        _, project = google.auth.default()

        if project:
            client = secretmanager.SecretManagerServiceClient()

            SETTINGS_NAME = os.environ.get("SETTINGS_NAME", "django_settings")
            name = f"projects/{project}/secrets/{SETTINGS_NAME}/versions/latest"
            payload = client.access_secret_version(name=name).payload.data.decode(
                "UTF-8"
            )
        env.read_env(io.StringIO(payload))
        # [END cloudrun_django_secretconfig]


SECRET_KEY = env("SECRET_KEY")

ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    "polls.apps.PollsConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "mysite",
    "storages",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "mysite.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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
WSGI_APPLICATION = "mysite.wsgi.application"


# [START cloudrun_django_dbconfig]
# Use django-environ to parse the connection string
DATABASES = {"default": env.db()}
# [END cloudrun_django_dbconfig]

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator", },
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator", },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"
DEBUG = True

USE_I18N = True

USE_L10N = True

USE_TZ = True

# [START cloudrun_django_staticconfig]
# Define static storage via django-storages[google]
GS_BUCKET_NAME = env("GS_BUCKET_NAME")

DEFAULT_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
STATICFILES_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
GS_DEFAULT_ACL = "publicRead"
# [END cloudrun_django_staticconfig]
