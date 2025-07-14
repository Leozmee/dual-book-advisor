"""
Migration des vues Django pour LangChain
Fichier: apps/chat/views_langchain.py

Ce fichier remplace progressivement les vues existantes dans apps/chat/views.py
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import ConversationHistory, Message
from .serializers import MessageSerializer
import logging
import time

# Import du nouveau système LangChain
from agents.langchain_agents.django_integration import (
    get_tech_recommendations,
    get_literature_recommendations, 
    get_manga_recommendations,
    route_query,
    get_system_status,
    get_django_langchain_bridge
)

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class LangChainTechAgentChatView(APIView):
    """Vue LangChain pour l'agent technique - Remplace TechAgentChatView"""
    
    permission_classes = []  # Temporairement désactivé pour les tests
    
    def post(self, request):
        message = request.data.get('message')
        if not message:
            return Response({
                'error': 'Message is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Utilisateur demo pour les tests
        from apps.accounts.models import User
        demo_user, created = User.objects.get_or_create(
            email='demo@example.com',
            defaults={'username': 'demo', 'first_name': 'Demo', 'last_name': 'User'}
        )
        
        # Créer la conversation
        conversation = ConversationHistory.objects.create(
            user=demo_user,
            agent_type='tech',
            title=f"Tech Chat LangChain - {message[:30]}..."
        )
        
        # Sauvegarder le message utilisateur
        user_msg = Message.objects.create(
            conversation=conversation,
            sender='user',
            content=message
        )
        
        try:
            start_time = time.time()
            
            # 🚀 NOUVEAU: Utiliser LangChain au lieu de SimpleAgentManager
            tech_response = get_tech_recommendations(message, demo_user.id)
            
            processing_time = time.time() - start_time
            
            # Ajouter les métadonnées de traitement
            tech_response += f"\n\n⚡ LangChain - {processing_time:.2f}s"
            
            # Sauvegarder la réponse de l'agent
            agent_msg = Message.objects.create(
                conversation=conversation,
                sender='agent',
                content=tech_response,
                rag_sources="LangChain_tech_recommendations",
                processing_time=processing_time
            )
            
            conversation.save()
            
            return Response({
                'conversation_id': conversation.id,
                'user_message': MessageSerializer(user_msg).data,
                'agent_response': MessageSerializer(agent_msg).data,
                'system_info': {
                    'using_langchain': True,
                    'agent_type': 'tech',
                    'processing_time': processing_time
                }
            })
            
        except Exception as e:
            logger.error(f"Erreur LangChain Tech Agent: {e}")
            
            return Response({
                'error': f'Tech agent error: {str(e)}',
                'system_info': {
                    'using_langchain': True,
                    'agent_type': 'tech',
                    'error': str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LangChainSystemStatusView(APIView):
    """Vue pour vérifier le statut du système LangChain"""
    
    permission_classes = []
    
    def get(self, request):
        """Retourne le statut complet du système LangChain"""
        try:
            # Obtenir le statut du système
            system_status = get_system_status()
            
            # Ajouter des informations détaillées
            bridge_status = get_django_langchain_bridge().get_status()
            
            detailed_status = {
                'timestamp': time.time(),
                'langchain_system': system_status,
                'bridge_status': bridge_status,
                'endpoints': {
                    'tech_agent': '/api/chat/langchain/tech/',
                    'literature_agent': '/api/chat/langchain/literature/',
                    'manga_agent': '/api/chat/langchain/manga/',
                    'auto_router': '/api/chat/langchain/router/',
                    'status': '/api/chat/langchain/status/'
                },
                'recommendations': self._get_health_recommendations(system_status, bridge_status)
            }
            
            # Déterminer le code de statut HTTP
            if bridge_status.get('available', False):
                status_code = status.HTTP_200_OK
            else:
                status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            
            return Response(detailed_status, status=status_code)
            
        except Exception as e:
            logger.error(f"Erreur status LangChain: {e}")
            return Response({
                'error': str(e),
                'available': False,
                'timestamp': time.time()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_health_recommendations(self, system_status: dict, bridge_status: dict) -> list:
        """Génère des recommandations basées sur le statut"""
        recommendations = []
        
        if not bridge_status.get('available', False):
            recommendations.append({
                'type': 'error',
                'message': 'LangChain non disponible',
                'action': 'Vérifiez la configuration LANGCHAIN_CONFIG dans settings.py'
            })
        
        if 'error' in system_status:
            recommendations.append({
                'type': 'warning',
                'message': f"Erreur système: {system_status['error']}",
                'action': 'Consultez les logs pour plus de détails'
            })
        
        health = system_status.get('health', {})
        llm_status = health.get('llm', {})
        
        if not llm_status.get('working', False):
            recommendations.append({
                'type': 'error',
                'message': 'LLM non fonctionnel',
                'action': 'Vérifiez vos clés API et la connectivité réseau'
            })
        
        rag_systems = health.get('rag_systems', {})
        for rag_name, rag_available in rag_systems.items():
            if not rag_available:
                recommendations.append({
                    'type': 'warning',
                    'message': f'RAG {rag_name} non disponible',
                    'action': f'Vérifiez la configuration du RAG {rag_name}'
                })
        
        if not recommendations:
            recommendations.append({
                'type': 'success',
                'message': 'Système LangChain opérationnel',
                'action': 'Tous les composants fonctionnent correctement'
            })
        
        return recommendations

# Vues de compatibilité pour migration progressive
class HybridTechAgentChatView(APIView):
    """Vue hybride qui utilise LangChain avec fallback vers l'ancien système"""
    
    permission_classes = []
    
    def post(self, request):
        """Essaie LangChain, puis fallback vers SimpleAgentManager"""
        
        # Tenter d'abord LangChain
        if get_django_langchain_bridge().is_available():
            try:
                langchain_view = LangChainTechAgentChatView()
                response = langchain_view.post(request)
                
                # Ajouter une indication que LangChain a été utilisé
                if response.status_code == 200 and 'system_info' in response.data:
                    response.data['system_info']['migration_status'] = 'langchain_success'
                
                return response
                
            except Exception as e:
                logger.warning(f"LangChain échoué, fallback vers ancien système: {e}")
        
        # Fallback vers l'ancien système
        try:
            from .views import TechAgentChatView
            old_view = TechAgentChatView()
            response = old_view.post(request)
            
            # Ajouter une indication du fallback
            if response.status_code == 200:
                if 'system_info' not in response.data:
                    response.data['system_info'] = {}
                response.data['system_info'].update({
                    'using_langchain': False,
                    'migration_status': 'fallback_to_old_system',
                    'reason': 'LangChain non disponible'
                })
            
            return response
            
        except Exception as e:
            logger.error(f"Fallback aussi échoué: {e}")
            return Response({
                'error': 'Tous les systèmes sont indisponibles',
                'langchain_error': 'Non disponible',
                'fallback_error': str(e)
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

# Migration progressive - URL mapping
"""
Pour migrer progressivement, ajoutez ces URLs dans apps/chat/urls.py :

# Nouvelles URLs LangChain
path('langchain/tech/', LangChainTechAgentChatView.as_view(), name='langchain_tech_agent'),
path('langchain/literature/', LangChainLiteratureAgentChatView.as_view(), name='langchain_literature_agent'),
path('langchain/manga/', LangChainMangaAgentChatView.as_view(), name='langchain_manga_agent'),
path('langchain/router/', LangChainRouterChatView.as_view(), name='langchain_router'),
path('langchain/status/', LangChainSystemStatusView.as_view(), name='langchain_status'),

# URLs hybrides pour migration progressive
path('hybrid/tech/', HybridTechAgentChatView.as_view(), name='hybrid_tech_agent'),

# Remplacer progressivement les anciennes URLs
# path('tech-agent/', LangChainTechAgentChatView.as_view(), name='tech_agent_chat'),  # Nouveau
# path('tech-agent/', views.TechAgentChatView.as_view(), name='tech_agent_chat'),     # Ancien
"""

# Configuration recommandée pour settings.py
LANGCHAIN_SETTINGS_EXAMPLE = """
# Ajoutez ceci dans votre config/settings/base.py ou development.py

LANGCHAIN_CONFIG = {
    # Provider LLM: 'openai', 'anthropic', 'ollama'
    'provider': 'openai',
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
"""

@method_decorator(csrf_exempt, name='dispatch')
class LangChainLiteratureAgentChatView(APIView):
    """Vue LangChain pour l'agent littéraire - Remplace LiteratureAgentChatView"""
    
    permission_classes = []  # Temporairement désactivé pour les tests
    
    def post(self, request):
        message = request.data.get('message')
        if not message:
            return Response({
                'error': 'Message is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Utilisateur demo pour les tests
        from apps.accounts.models import User
        demo_user, created = User.objects.get_or_create(
            email='demo@example.com',
            defaults={'username': 'demo', 'first_name': 'Demo', 'last_name': 'User'}
        )
        
        # Créer la conversation
        conversation = ConversationHistory.objects.create(
            user=demo_user,
            agent_type='literature',
            title=f"Literature Chat LangChain - {message[:30]}..."
        )
        
        # Sauvegarder le message utilisateur
        user_msg = Message.objects.create(
            conversation=conversation,
            sender='user',
            content=message
        )
        
        try:
            start_time = time.time()
            
            # 🚀 NOUVEAU: Utiliser LangChain au lieu de SimpleAgentManager
            literature_response = get_literature_recommendations(message, demo_user.id)
            
            processing_time = time.time() - start_time
            
            # Ajouter les métadonnées de traitement
            literature_response += f"\n\n⚡ LangChain - {processing_time:.2f}s"
            
            # Sauvegarder la réponse de l'agent
            agent_msg = Message.objects.create(
                conversation=conversation,
                sender='agent',
                content=literature_response,
                rag_sources="LangChain_literature_recommendations",
                processing_time=processing_time
            )
            
            conversation.save()
            
            return Response({
                'conversation_id': conversation.id,
                'user_message': MessageSerializer(user_msg).data,
                'agent_response': MessageSerializer(agent_msg).data,
                'system_info': {
                    'using_langchain': True,
                    'agent_type': 'literature',
                    'processing_time': processing_time
                }
            })
            
        except Exception as e:
            logger.error(f"Erreur LangChain Literature Agent: {e}")
            
            # Fallback en cas d'erreur
            fallback_response = "📚 Désolé, je rencontre des difficultés. Veuillez réessayer."
            
            agent_msg = Message.objects.create(
                conversation=conversation,
                sender='agent',
                content=fallback_response,
                rag_sources="LangChain_error_fallback"
            )
            
            return Response({
                'conversation_id': conversation.id,
                'user_message': MessageSerializer(user_msg).data,
                'agent_response': MessageSerializer(agent_msg).data,
                'system_info': {
                    'using_langchain': True,
                    'agent_type': 'literature',
                    'error': str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(csrf_exempt, name='dispatch')
class LangChainMangaAgentChatView(APIView):
    """Vue LangChain pour l'agent manga - Remplace MangaAgentChatView"""
    
    permission_classes = []  # Temporairement désactivé pour les tests
    
    def post(self, request):
        message = request.data.get('message')
        if not message:
            return Response({
                'error': 'Message is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Utilisateur demo pour les tests
        from apps.accounts.models import User
        demo_user, created = User.objects.get_or_create(
            email='demo@example.com',
            defaults={'username': 'demo', 'first_name': 'Demo', 'last_name': 'User'}
        )
        
        # Créer la conversation
        conversation = ConversationHistory.objects.create(
            user=demo_user,
            agent_type='manga',
            title=f"Manga Chat LangChain - {message[:30]}..."
        )
        
        # Sauvegarder le message utilisateur
        user_msg = Message.objects.create(
            conversation=conversation,
            sender='user',
            content=message
        )
        
        try:
            start_time = time.time()
            
            # 🚀 NOUVEAU: Utiliser LangChain au lieu de SimpleAgentManager
            manga_response = get_manga_recommendations(message, demo_user.id)
            
            processing_time = time.time() - start_time
            
            # Ajouter les métadonnées de traitement
            manga_response += f"\n\n⚡ LangChain - {processing_time:.2f}s"
            
            # Sauvegarder la réponse de l'agent
            agent_msg = Message.objects.create(
                conversation=conversation,
                sender='agent',
                content=manga_response,
                rag_sources="LangChain_manga_recommendations",
                processing_time=processing_time
            )
            
            conversation.save()
            
            return Response({
                'conversation_id': conversation.id,
                'user_message': MessageSerializer(user_msg).data,
                'agent_response': MessageSerializer(agent_msg).data,
                'system_info': {
                    'using_langchain': True,
                    'agent_type': 'manga',
                    'processing_time': processing_time
                }
            })
            
        except Exception as e:
            logger.error(f"Erreur LangChain Manga Agent: {e}")
            
            # Fallback en cas d'erreur
            fallback_response = "🎌 Désolé, je rencontre des difficultés. Veuillez réessayer."
            
            agent_msg = Message.objects.create(
                conversation=conversation,
                sender='agent',
                content=fallback_response,
                rag_sources="LangChain_error_fallback"
            )
            
            return Response({
                'conversation_id': conversation.id,
                'user_message': MessageSerializer(user_msg).data,
                'agent_response': MessageSerializer(agent_msg).data,
                'system_info': {
                    'using_langchain': True,
                    'agent_type': 'manga',
                    'error': str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(csrf_exempt, name='dispatch')
class LangChainRouterChatView(APIView):
    """Vue LangChain pour le routage automatique - Nouvelle fonctionnalité"""
    
    permission_classes = []
    
    def post(self, request):
        message = request.data.get('message')
        if not message:
            return Response({
                'error': 'Message is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Utilisateur demo pour les tests
        from apps.accounts.models import User
        demo_user, created = User.objects.get_or_create(
            email='demo@example.com',
            defaults={'username': 'demo', 'first_name': 'Demo', 'last_name': 'User'}
        )
        
        try:
            start_time = time.time()
            
            # 🚀 NOUVEAU: Routage automatique avec LangChain
            router_response = route_query(message, demo_user.id)
            
            processing_time = time.time() - start_time
            
            # Déterminer l'agent utilisé (heuristique basée sur les emojis)
            if "🔧" in router_response:
                detected_agent = "tech"
            elif "📚" in router_response:
                detected_agent = "literature"
            elif "🎌" in router_response:
                detected_agent = "manga"
            else:
                detected_agent = "auto"
            
            # Créer la conversation avec l'agent détecté
            conversation = ConversationHistory.objects.create(
                user=demo_user,
                agent_type=detected_agent,
                title=f"Auto Chat LangChain - {message[:30]}..."
            )
            
            # Sauvegarder le message utilisateur
            user_msg = Message.objects.create(
                conversation=conversation,
                sender='user',
                content=message
            )
            
            # Ajouter les métadonnées de traitement
            router_response += f"\n\n⚡ LangChain Auto-Router - {processing_time:.2f}s"
            
            # Sauvegarder la réponse de l'agent
            agent_msg = Message.objects.create(
                conversation=conversation,
                sender='agent',
                content=router_response,
                rag_sources="LangChain_auto_router",
                processing_time=processing_time
            )
            
            conversation.save()
            
            return Response({
                'conversation_id': conversation.id,
                'user_message': MessageSerializer(user_msg).data,
                'agent_response': MessageSerializer(agent_msg).data,
                'system_info': {
                    'using_langchain': True,
                    'agent_type': 'auto_router',
                    'detected_agent': detected_agent,
                    'processing_time': processing_time
                }
            })
            
        except Exception as e:
            logger.error(f"Erreur LangChain Router: {e}")
            
            return Response({
                'error': f'Router error: {str(e)}',
                'system_info': {
                    'using_langchain': True,
                    'agent_type': 'auto_router',
                    'error': str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)