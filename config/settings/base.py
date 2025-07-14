import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-dual-book-advisor-change-in-production-123456789'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

LOCAL_APPS = [
    'config',  # Pour les commandes de management personnalisées
    'apps.accounts',
    'apps.books',
    'apps.chat',
    'apps.dashboard',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'corsheaders',
]

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS + THIRD_PARTY_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# PostgreSQL (commenté pour utiliser SQLite par défaut)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.environ.get('DB_NAME', 'dual_book_advisor'),
#         'USER': os.environ.get('DB_USER', 'postgres'),
#         'PASSWORD': os.environ.get('DB_PASSWORD', 'postgres'),
#         'HOST': os.environ.get('DB_HOST', 'localhost'),
#         'PORT': os.environ.get('DB_PORT', '5432'),
#     }
# }

# Password validation
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
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

# Custom user model
AUTH_USER_MODEL = 'accounts.User'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'apps': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# RAG Configuration

# 🚀 CONFIGURATION RAG AMÉLIORÉE (REMPLACE L'ANCIENNE)
RAG_CONFIG = {
    'embedding_model': 'sentence-transformers/all-MiniLM-L6-v2',
    'chunk_size': 512,
    'top_k_results': 8,  # ✅ Augmenté pour plus de choix (était 5)
    'similarity_threshold': 0.25,  # ✅ Réduit pour plus de résultats (était 0.5)
    'tech_data_path': BASE_DIR / 'rags' / 'tech_rag' / 'data',
    'literature_data_path': BASE_DIR / 'rags' / 'literature_rag' / 'data',
    'tech_chroma_path': BASE_DIR / 'rags' / 'tech_rag' / 'chroma_db',
    'literature_chroma_path': BASE_DIR / 'rags' / 'literature_rag' / 'chroma_db',
    
    # ✅ NOUVELLES OPTIONS POUR AMÉLIORER LES RECHERCHES
    'multilingual_queries': True,  # Support français/anglais
    'query_expansion': True,       # Expansion automatique des requêtes
    'semantic_boost': True,        # Boost sémantique
    'fallback_threshold': 0.3,     # Seuil minimal pour éviter les résultats vides
    'max_results_per_query': 10,   # Maximum de résultats à traiter
    'use_fuzzy_matching': True,    # Correspondance floue pour noms d'auteurs
}

# 🌍 DICTIONNAIRE DE TRADUCTION POUR REQUÊTES MULTILINGUES
QUERY_TRANSLATIONS = {
    # Auteurs littéraires
    'tolstoy': 'Leo Tolstoy War Peace Anna Karenina Russian literature classic',
    'tolstoï': 'Leo Tolstoy War Peace Anna Karenina Russian literature classic',
    'stephen king': 'Stephen King horror thriller It Shining Carrie Salem',
    'murakami': 'Haruki Murakami Norwegian Wood Kafka Shore Japanese literature',
    'victor hugo': 'Victor Hugo Les Misérables Hunchback Notre Dame French classic',
    'shakespeare': 'William Shakespeare Hamlet Romeo Juliet Macbeth English',
    'camus': 'Albert Camus Stranger Plague Myth Sisyphus existentialism',
    'sartre': 'Jean-Paul Sartre Nausea Being Nothingness existentialism',
    
    # Genres littéraires
    'romans': 'novels fiction literature story narrative',
    'fantasy': 'fantasy magic adventure fiction magical worlds',
    'science fiction': 'science fiction sci-fi futuristic space technology',
    'thriller': 'thriller suspense mystery crime psychological',
    'romance': 'romance love relationship contemporary historical',
    'policier': 'mystery detective crime investigation police',
    
    # Technique
    'python': 'Python programming language development beginner advanced',
    'javascript': 'JavaScript web development frontend backend Node.js',
    'c#': 'C# CSharp .NET Microsoft programming Windows development',
    'java': 'Java programming language enterprise development Android',
    'web développement': 'web development HTML CSS JavaScript frontend backend',
    'machine learning': 'machine learning AI artificial intelligence data science',
    'data science': 'data science analysis statistics Python R visualization',
    'développement mobile': 'mobile development Android iOS React Native Flutter',
    
    # Intentions
    'apprendre': 'learn beginner tutorial introduction guide',
    'débutant': 'beginner introductory basic fundamentals getting started',
    'avancé': 'advanced expert professional deep dive comprehensive',
    'recommandation': 'recommendation suggest similar like comparable',
    'oeuvres principales': 'main works major novels best books masterpieces',
}

# Agent Configuration
AGENT_CONFIG = {
    'tech_agent': {
        'model_name': 'google/flan-t5-base',
        'max_length': 512,
        'temperature': 0.7,
    },
    'literature_agent': {
        'model_name': 'google/flan-t5-base',
        'max_length': 512,
        'temperature': 0.8,
    },
}

# LangChain Configuration
LANGCHAIN_PROVIDER = os.environ.get('LANGCHAIN_PROVIDER', 'openai')  # openai, anthropic, huggingface
LANGCHAIN_MODEL = os.environ.get('LANGCHAIN_MODEL', 'gpt-3.5-turbo')

# API Keys (à définir dans les variables d'environnement)
# OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
# ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')

# Configuration LangChain
LANGCHAIN_CONFIG = {
    # Provider: 'openai', 'anthropic', 'ollama'
    'provider': 'openai',  # Changez selon vos besoins
    'model': 'gpt-3.5-turbo',
    
    # Clés API (utilisez les variables d'environnement)
    'openai_api_key': os.getenv('OPENAI_API_KEY'),
    'anthropic_api_key': os.getenv('ANTHROPIC_API_KEY'),
    
    # Configuration Ollama (si utilisé)
    'ollama_base_url': 'http://localhost:11434',
    
    # Paramètres LLM
    'temperature': 0.7,
    'max_tokens': 1000,
    'timeout': 30
}

# Logging pour LangChain
LOGGING['loggers'].update({
    'agents.langchain_agents': {
        'handlers': ['console'],
        'level': 'INFO',
        'propagate': False,
    },
    'langchain': {
        'handlers': ['console'],
        'level': 'WARNING',
        'propagate': False,
    }
})