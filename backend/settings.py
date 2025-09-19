# backend/settings.py
from pathlib import Path
import os
from dotenv import load_dotenv

# --- Caminhos base ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- .env ---
# Crie um arquivo .env na raiz do projeto (mesmo nível do manage.py)
# Exemplo:
#   DEBUG=1
#   SECRET_KEY=dev-secret-key-qualquer
#   USE_SQLITE=1
#   PGDATABASE=paciencia_rpg
#   PGUSER=postgres
#   PGPASSWORD=postgres
#   PGHOST=127.0.0.1
#   PGPORT=5432
#   ALLOWED_HOSTS=127.0.0.1,localhost
load_dotenv(BASE_DIR / ".env")

# --- Segurança / Debug ---
DEBUG = os.getenv("DEBUG", "1") == "1"
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-nao-use-em-producao")
ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",") if h.strip()]

# --- Apps instalados ---
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Terceiros
    "rest_framework",

    # Apps do projeto
    "game",
]

# (Opcional) CORS: se quiser usar um front em http://localhost:5173
# 1) pip install django-cors-headers
# 2) descomente as linhas abaixo:
# INSTALLED_APPS += ["corsheaders"]
# MIDDLEWARE = ["corsheaders.middleware.CorsMiddleware", *MIDDLEWARE]
# CORS_ALLOWED_ORIGINS = [
#     os.getenv("FRONTEND_ORIGIN", "http://localhost:5173"),
# ]

# --- Middleware ---
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# --- URLs / WSGI ---
ROOT_URLCONF = "backend.urls"
WSGI_APPLICATION = "backend.wsgi.application"
# (Opcional) se usar ASGI:
# ASGI_APPLICATION = "backend.asgi.application"

# --- Templates ---
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # pasta templates/ na raiz do projeto
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

# --- Banco de Dados ---
# Se USE_SQLITE=1 no .env, usa SQLite para desenvolvimento rápido.
# Caso contrário, usa PostgreSQL com as variáveis PG*.
if os.getenv("USE_SQLITE", "0") == "1":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("PGDATABASE", "paciencia_rpg"),
            "USER": os.getenv("PGUSER", "postgres"),
            "PASSWORD": os.getenv("PGPASSWORD", "postgres"),
            "HOST": os.getenv("PGHOST", "127.0.0.1"),
            "PORT": os.getenv("PGPORT", "5432"),
        }
    }

# --- Validação de senha (padrão Django) ---
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- Internacionalização / Fuso ---
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Araguaina"
USE_I18N = True
USE_TZ = True  # mantém datas em UTC internamente; TIME_ZONE afeta apresentação

# --- Arquivos estáticos ---
# Em dev, Django serve STATIC_URL; em prod, configure um servidor de arquivos.
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]  # pasta static/ para seus assets (opcional)
STATIC_ROOT = BASE_DIR / "staticfiles"    # onde 'collectstatic' vai juntar (produção)

# (Opcional) Arquivos de mídia enviados por usuários:
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# --- REST Framework (básico) ---
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        # habilite o browsable API no dev, se quiser:
        "rest_framework.renderers.BrowsableAPIRenderer" if DEBUG else "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ],
}

# --- Campo padrão para PK ---
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- CSRF (útil se tiver front separado) ---
# Ex.: http://localhost:5173
# CSRF_TRUSTED_ORIGINS = [os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")]
