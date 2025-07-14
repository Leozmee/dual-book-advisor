"""
Intégration Django LangChain - Connexion avec le frontend existant
Fichier: agents/langchain_agents/django_integration.py
"""
from typing import Dict, Any, Optional
from django.conf import settings
import logging
import os

logger = logging.getLogger(__name__)

class DjangoLangChainBridge:
    """Pont entre le système LangChain et Django"""
    
    _instance = None
    _graph_manager = None
    
    def __new__(cls):
        """Singleton pour éviter les réinitialisations multiples"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._setup_langchain_manager()
    
    def _setup_langchain_manager(self):
        """Configure le gestionnaire LangChain selon les settings Django"""
        try:
            # Configuration LLM depuis Django settings
            llm_config = getattr(settings, 'LANGCHAIN_CONFIG', {})
            
            # Valeurs par défaut
            llm_provider = llm_config.get('provider', 'openai')
            model_name = llm_config.get('model', 'gpt-3.5-turbo')
            
            # Configuration des clés API
            llm_kwargs = {}
            
            if llm_provider.lower() == 'openai':
                api_key = llm_config.get('openai_api_key') or os.getenv('OPENAI_API_KEY')
                if api_key:
                    llm_kwargs['api_key'] = api_key
                else:
                    logger.warning("⚠️ OPENAI_API_KEY non configuré")
            
            elif llm_provider.lower() == 'anthropic':
                api_key = llm_config.get('anthropic_api_key') or os.getenv('ANTHROPIC_API_KEY')
                if api_key:
                    llm_kwargs['api_key'] = api_key
                else:
                    logger.warning("⚠️ ANTHROPIC_API_KEY non configuré")
            
            elif llm_provider.lower() == 'ollama':
                base_url = llm_config.get('ollama_base_url', 'http://localhost:11434')
                llm_kwargs['base_url'] = base_url
            
            # Importer et créer le gestionnaire
            from .graph_manager import LangChainAgentManager
            from ..minimal_llama_manager import minimal_llama_manager
            
            # Utiliser uniquement Llama 3.2 3B optimisé
            if llm_provider.lower() == 'ollama':
                model_name = 'llama3.2:3b'
                logger.info(f"🦙 Utilisation du modèle Llama optimisé: {model_name}")
            
            self._graph_manager = LangChainAgentManager(
                llm_provider=llm_provider,
                model_name=model_name,
                **llm_kwargs
            )
            
            logger.info(f"✅ LangChain Manager configuré: {llm_provider}:{model_name}")
            
        except Exception as e:
            logger.error(f"❌ Erreur configuration LangChain: {e}")
            # Fallback vers l'ancien système si nécessaire
            self._graph_manager = None
    
    def get_manager(self):
        """Retourne le gestionnaire LangChain ou None si indisponible"""
        return self._graph_manager
    
    def is_available(self) -> bool:
        """Vérifie si LangChain est disponible"""
        return self._graph_manager is not None
    
    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut du système LangChain"""
        if not self.is_available():
            return {
                "available": False,
                "error": "LangChain manager non initialisé"
            }
        
        try:
            health = self._graph_manager.get_system_status()
            return {
                "available": True,
                "health": health,
                "provider": getattr(self._graph_manager.graph_manager, 'llm_provider', 'unknown'),
                "model": getattr(self._graph_manager.graph_manager, 'model_name', 'unknown')
            }
        except Exception as e:
            return {
                "available": False,
                "error": str(e)
            }

# Instance globale du pont (lazy)
django_langchain_bridge = None

def get_django_langchain_bridge():
    """Retourne l'instance du pont, créée lazily"""
    global django_langchain_bridge
    if django_langchain_bridge is None:
        django_langchain_bridge = DjangoLangChainBridge()
    return django_langchain_bridge

# Fonctions d'interface pour remplacer SimpleAgentManager
def get_tech_recommendations(query: str, user_id: int = 1) -> str:
    """
    Interface compatible avec l'ancien SimpleAgentManager.get_tech_recommendations()
    """
    try:
        bridge = get_django_langchain_bridge()
        
        if not bridge.is_available():
            logger.warning("LangChain indisponible, fallback vers ancien système")
            return _fallback_to_old_system("tech", query, user_id)
        
        manager = bridge.get_manager()
        response = manager.get_tech_recommendations(query, user_id)
        
        logger.info(f"✅ Tech LangChain: '{query}' → {len(response)} caractères")
        return response
        
    except Exception as e:
        logger.error(f"❌ Erreur tech LangChain: {e}")
        return _fallback_to_old_system("tech", query, user_id)

def get_literature_recommendations(query: str, user_id: int = 1) -> str:
    """
    Interface compatible avec l'ancien SimpleAgentManager.get_literature_recommendations()
    """
    try:
        bridge = get_django_langchain_bridge()
        
        if not bridge.is_available():
            logger.warning("LangChain indisponible, fallback vers ancien système")
            return _fallback_to_old_system("literature", query, user_id)
        
        manager = bridge.get_manager()
        response = manager.get_literature_recommendations(query, user_id)
        
        logger.info(f"✅ Literature LangChain: '{query}' → {len(response)} caractères")
        return response
        
    except Exception as e:
        logger.error(f"❌ Erreur literature LangChain: {e}")
        return _fallback_to_old_system("literature", query, user_id)

def get_manga_recommendations(query: str, user_id: int = 1) -> str:
    """
    Interface compatible avec l'ancien SimpleAgentManager.get_manga_recommendations()
    """
    try:
        bridge = get_django_langchain_bridge()
        
        if not bridge.is_available():
            logger.warning("LangChain indisponible, fallback vers ancien système")
            return _fallback_to_old_system("manga", query, user_id)
        
        manager = bridge.get_manager()
        response = manager.get_manga_recommendations(query, user_id)
        
        logger.info(f"✅ Manga LangChain: '{query}' → {len(response)} caractères")
        return response
        
    except Exception as e:
        logger.error(f"❌ Erreur manga LangChain: {e}")
        return _fallback_to_old_system("manga", query, user_id)

def route_query(query: str, user_id: int = 1) -> str:
    """
    Interface compatible avec l'ancien SimpleAgentManager.route_query()
    """
    try:
        bridge = get_django_langchain_bridge()
        
        if not bridge.is_available():
            logger.warning("LangChain indisponible, fallback vers ancien système")
            return _fallback_to_old_system("router", query, user_id)
        
        manager = bridge.get_manager()
        response = manager.route_query(query, user_id)
        
        logger.info(f"✅ Route LangChain: '{query}' → {len(response)} caractères")
        return response
        
    except Exception as e:
        logger.error(f"❌ Erreur route LangChain: {e}")
        return _fallback_to_old_system("router", query, user_id)

def get_agent_response(query: str, agent_type: str = "router", user_id: int = 1) -> str:
    """
    Interface compatible avec l'ancien SimpleAgentManager.get_agent_response()
    """
    try:
        bridge = get_django_langchain_bridge()
        
        if not bridge.is_available():
            logger.warning("LangChain indisponible, fallback vers ancien système")
            return _fallback_to_old_system(agent_type, query, user_id)
        
        manager = bridge.get_manager()
        response = manager.get_agent_response(query, agent_type, user_id)
        
        logger.info(f"✅ Agent {agent_type} LangChain: '{query}' → {len(response)} caractères")
        return response
        
    except Exception as e:
        logger.error(f"❌ Erreur agent {agent_type} LangChain: {e}")
        return _fallback_to_old_system(agent_type, query, user_id)

def get_system_status() -> Dict[str, Any]:
    """
    Interface compatible avec l'ancien SimpleAgentManager.get_system_status()
    """
    try:
        bridge = get_django_langchain_bridge()
        
        if not bridge.is_available():
            return {
                "langchain_available": False,
                "using_fallback": True,
                "status": "LangChain non disponible - utilisation du fallback"
            }
        
        manager = bridge.get_manager()
        status = manager.get_system_status()
        status["langchain_available"] = True
        status["using_fallback"] = False
        
        return status
        
    except Exception as e:
        return {
            "langchain_available": False,
            "using_fallback": True,
            "error": str(e)
        }

def _fallback_to_old_system(agent_type: str, query: str, user_id: int = 1) -> str:
    """
    Fallback vers l'ancien système SimpleAgentManager si LangChain n'est pas disponible
    """
    try:
        # Import dynamique pour éviter les dépendances circulaires
        from agents.simple_agents import SimpleAgentManager
        
        old_manager = SimpleAgentManager(use_gemma=False)  # Sans Gemma pour éviter les conflits
        
        if agent_type == "tech":
            return old_manager.get_tech_recommendations(query, user_id)
        elif agent_type == "literature":
            return old_manager.get_literature_recommendations(query, user_id)
        elif agent_type == "manga":
            return old_manager.get_manga_recommendations(query, user_id)
        elif agent_type == "router":
            return old_manager.route_query(query)
        else:
            return old_manager.get_agent_response(query, agent_type)
            
    except Exception as e:
        logger.error(f"❌ Erreur fallback vers ancien système: {e}")
        return f"🤖 Désolé, je rencontre des difficultés techniques pour traiter votre demande sur {agent_type}. Veuillez réessayer plus tard."

# Configuration Django recommandée
def get_recommended_django_settings() -> Dict[str, Any]:
    """Retourne la configuration Django recommandée pour LangChain"""
    return {
        "LANGCHAIN_CONFIG": {
            # Provider: 'openai', 'anthropic', 'ollama'
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            
            # Clés API (préférez les variables d'environnement)
            "openai_api_key": None,  # Utilisez OPENAI_API_KEY env var
            "anthropic_api_key": None,  # Utilisez ANTHROPIC_API_KEY env var
            
            # Configuration Ollama
            "ollama_base_url": "http://localhost:11434",
            
            # Options avancées
            "temperature": 0.7,
            "max_tokens": 1000,
            "timeout": 30
        },
        
        # Logging pour LangChain
        "LOGGING": {
            "loggers": {
                "agents.langchain_agents": {
                    "handlers": ["console"],
                    "level": "INFO",
                    "propagate": False,
                },
                "langchain": {
                    "handlers": ["console"],
                    "level": "WARNING",
                    "propagate": False,
                },
            }
        }
    }

# Test d'intégration
def test_django_integration():
    """Test de l'intégration Django"""
    print("🧪 Test de l'intégration Django LangChain")
    print("=" * 50)
    
    # Test du pont
    bridge = get_django_langchain_bridge()
    print(f"🔗 Pont disponible: {bridge.is_available()}")
    
    if bridge.is_available():
        status = bridge.get_status()
        print(f"📊 Statut: {status}")
    
    # Test des fonctions d'interface
    test_queries = {
        "tech": "apprendre Python",
        "literature": "romans de Tolstoï",
        "manga": "manga comme Naruto"
    }
    
    for agent_type, query in test_queries.items():
        print(f"\n🧪 Test {agent_type}: '{query}'")
        try:
            if agent_type == "tech":
                response = get_tech_recommendations(query)
            elif agent_type == "literature":
                response = get_literature_recommendations(query)
            elif agent_type == "manga":
                response = get_manga_recommendations(query)
            
            print(f"   ✅ Réponse: {len(response)} caractères")
            print(f"   📝 Début: {response[:100]}...")
            
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
    
    # Test du routage
    print(f"\n🔄 Test routage automatique")
    try:
        response = route_query("j'aimerais apprendre le machine learning")
        print(f"   ✅ Route: {len(response)} caractères")
    except Exception as e:
        print(f"   ❌ Erreur route: {e}")
    
    # Test du statut système
    print(f"\n📊 Test statut système")
    try:
        status = get_system_status()
        print(f"   ✅ Statut: {status.get('langchain_available', False)}")
    except Exception as e:
        print(f"   ❌ Erreur statut: {e}")

if __name__ == "__main__":
    test_django_integration()