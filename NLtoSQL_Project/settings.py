

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-h4()6*kzem6&!i!_rtd1g0%h-l4bz4hj=-aw6nll@d==dj!exx"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


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
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        'HOST': 'aws-0-us-east-1.pooler.supabase.com',
        'PORT': '6543',
        'USER': 'postgres.vkzhpwggfsbybgfxater',
        'PASSWORD': 'BE1Tage1djUPs7up',
        'NAME': 'postgres'
    }
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


# SUPABASE_URL = "https://vkzhpwggfsbybgfxater.supabase.co"
# SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZremhwd2dnZnNieWJnZnhhdGVyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjEwOTQ4NzAsImV4cCI6MjAzNjY3MDg3MH0.M6bJ61mRI2PHFyA2xEmIO-ECSa9Yy7L5jWSAJontjdY"



B2_BUCKET_NAME = "NLtoSqlBucket"

B2_APPLICATION_KEY_ID = '005aaa508488e6a0000000002'
B2_APPLICATION_KEY = 'K005P5sd2Ia9N5FsPqUeu8W0hAY+2ow'
B2_REGION = 'us-east-005'  


B2_ENDPOINT_URL = 'https://s3.us-east-005.backblazeb2.com'
B2_KEY_ID = '005aaa508488e6a0000000002'
B2_APPLICATION_KEY = 'K005P5sd2Ia9N5FsPqUeu8W0hAY+2ow'
B2_BUCKET_NAME = 'NLtoSqlBucket'