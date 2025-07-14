from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Database for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# CORS settings for development
CORS_ALLOW_ALL_ORIGINS = True

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Static files for development
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Django Debug Toolbar (désactivé temporairement)
# if DEBUG:
#     INSTALLED_APPS += ['debug_toolbar']
#     MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
#     INTERNAL_IPS = ['127.0.0.1']

# Logging for development
LOGGING['handlers']['console']['level'] = 'DEBUG'
LOGGING['loggers']['django']['level'] = 'DEBUG'
LOGGING['loggers']['apps']['level'] = 'DEBUG'

# Configuration LangChain avec Llama 3.2 3B optimisé
LANGCHAIN_CONFIG = {
    # Provider LLM: utiliser 'ollama' pour Llama local
    'provider': 'ollama',
    'model': 'llama3.2:3b',  # Modèle unique optimisé
    
    # Configuration Ollama
    'ollama_base_url': 'http://localhost:11434',
    
    # Configuration OpenAI/Anthropic (désactivées)
    'openai_api_key': None,
    'anthropic_api_key': None,
    
    # Paramètres LLM optimisés pour Llama 3.2 3B
    'temperature': 0.7,
    'max_tokens': 512,
    'timeout': 30,
    
    # Configuration Llama spécifique
    'llama_optimized': True,
    'collect_stats': True,
    'auto_performance_monitoring': True
}

# Logging pour Llama optimisé
LOGGING['loggers'].update({
    'agents.lazy_llama_manager': {
        'handlers': ['console'],
        'level': 'INFO',
        'propagate': False,
    },
    'apps.chat.views_llama_agents': {
        'handlers': ['console'],
        'level': 'INFO',
        'propagate': False,
    },
    'apps.chat.views_llama_stats': {
        'handlers': ['console'],
        'level': 'INFO',
        'propagate': False,
    },
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