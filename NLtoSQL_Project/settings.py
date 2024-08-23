from pathlib import Path
import os
import environ
from dotenv import load_dotenv
import dj_database_url


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()
env = environ.Env()
environ.Env.read_env()



# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", {})

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG =  os.environ.get("DEBUG", False)

ALLOWED_HOSTS = ['natural-language-to-sql.onrender.com', 'localhost', '127.0.0.1']



# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "NLtoSQL",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    'NLtoSQL.middleware.LoginRequiredMiddleware',
]

ROOT_URLCONF = "NLtoSQL_Project.urls"

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

WSGI_APPLICATION = "NLtoSQL_Project.wsgi.application"


# Database
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }


# Database configuration
# DATABASES = {
#     'default': env.db('DATABASE_URL', os.environ.get("DATABASE_URL", {})),
# }
DATABASES = {
    'default': dj_database_url.parse(os.environ.get('DATABASE_URL', {}))
}




# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "America/Chicago"

USE_I18N = True

USE_TZ = True

from django.utils import timezone

current_time = timezone.now().strftime("%B %d, %Y - %I:%M %p")
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"
LOGIN_URL = '/login_user/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"




# B2 Configuration
B2_BUCKET_NAME = env('B2_BUCKET_NAME', default="")
B2_APPLICATION_KEY_ID = env('B2_APPLICATION_KEY_ID', default="")
B2_APPLICATION_KEY = env('B2_APPLICATION_KEY', default="")
B2_REGION = env('B2_REGION', default="")

# Google API Configuration
GOOGLE_API_KEY = env('GOOGLE_API_KEY', default="")

# Secret Code (if needed)
SECRET_CODE = env('SECRET_CODE', default="")

