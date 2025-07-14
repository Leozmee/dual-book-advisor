"""
Vues Django simplifiées pour les agents Llama 3.2 3B
Fichier: apps/chat/views_llama_agents.py

Vues d'agents optimisées spécifiquement pour Llama 3.2 3B
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
import logging
import time

from .models import ConversationHistory, Message
from .serializers import MessageSerializer
from agents.minimal_llama_manager import minimal_llama_manager

logger = logging.getLogger(__name__)

class LlamaTechAgentView(APIView):
    """Agent technique optimisé avec Llama 3.2 3B"""
    
    permission_classes = []
    
    def post(self, request):
        try:
            message = request.data.get('message')
            if not message:
                return Response({
                    'error': 'Message requis'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Utilisateur demo
            from apps.accounts.models import User
            demo_user, created = User.objects.get_or_create(
                email='demo@example.com',
                defaults={'username': 'demo', 'first_name': 'Demo', 'last_name': 'User'}
            )
            
            # Créer la conversation
            conversation = ConversationHistory.objects.create(
                user=demo_user,
                agent_type='tech',
                title=f"Tech Llama - {message[:30]}..."
            )
            
            # Sauvegarder le message utilisateur
            user_msg = Message.objects.create(
                conversation=conversation,
                sender='user',
                content=message
            )
            
            # Générer la réponse avec Llama optimisé
            start_time = time.time()
            response, metrics = minimal_llama_manager.generate_response(
                message, 
                agent_type='tech'
            )
            processing_time = time.time() - start_time
            
            # Enrichir la réponse avec les métadonnées
            enriched_response = f"🔧 **Recommandations Techniques (Llama 3.2 3B)**\n\n{response}"
            enriched_response += f"\n\n⚡ Traitement: {processing_time:.2f}s"
            enriched_response += f" | Tokens: {metrics.get('tokens_generated', 0)}"
            enriched_response += f" | Grade: {minimal_llama_manager.stats.get_performance_grade()}"
            
            # Sauvegarder la réponse
            agent_msg = Message.objects.create(
                conversation=conversation,
                sender='agent',
                content=enriched_response,
                rag_sources="Llama_3.2_3B_tech",
                processing_time=processing_time
            )
            
            conversation.save()
            
            return Response({
                'success': True,
                'conversation_id': conversation.id,
                'user_message': MessageSerializer(user_msg).data,
                'agent_response': MessageSerializer(agent_msg).data,
                'llama_metrics': metrics,
                'system_info': {
                    'model': 'llama3.2:3b',
                    'agent_type': 'tech',
                    'processing_time': processing_time,
                    'performance_grade': minimal_llama_manager.stats.get_performance_grade(),
                    'total_queries': minimal_llama_manager.stats.total_queries
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Erreur agent technique Llama: {e}")
            return Response({
                'success': False,
                'error': str(e),
                'model': 'llama3.2:3b'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LlamaLiteratureAgentView(APIView):
    """Agent littéraire optimisé avec Llama 3.2 3B"""
    
    permission_classes = []
    
    def post(self, request):
        try:
            message = request.data.get('message')
            if not message:
                return Response({
                    'error': 'Message requis'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Utilisateur demo
            from apps.accounts.models import User
            demo_user, created = User.objects.get_or_create(
                email='demo@example.com',
                defaults={'username': 'demo', 'first_name': 'Demo', 'last_name': 'User'}
            )
            
            # Créer la conversation
            conversation = ConversationHistory.objects.create(
                user=demo_user,
                agent_type='literature',
                title=f"Littérature Llama - {message[:30]}..."
            )
            
            # Sauvegarder le message utilisateur
            user_msg = Message.objects.create(
                conversation=conversation,
                sender='user',
                content=message
            )
            
            # Générer la réponse avec Llama optimisé
            start_time = time.time()
            response, metrics = minimal_llama_manager.generate_response(
                message, 
                agent_type='literature'
            )
            processing_time = time.time() - start_time
            
            # Enrichir la réponse avec les métadonnées
            enriched_response = f"📚 **Recommandations Littéraires (Llama 3.2 3B)**\n\n{response}"
            enriched_response += f"\n\n⚡ Traitement: {processing_time:.2f}s"
            enriched_response += f" | Tokens: {metrics.get('tokens_generated', 0)}"
            enriched_response += f" | Grade: {minimal_llama_manager.stats.get_performance_grade()}"
            
            # Sauvegarder la réponse
            agent_msg = Message.objects.create(
                conversation=conversation,
                sender='agent',
                content=enriched_response,
                rag_sources="Llama_3.2_3B_literature",
                processing_time=processing_time
            )
            
            conversation.save()
            
            return Response({
                'success': True,
                'conversation_id': conversation.id,
                'user_message': MessageSerializer(user_msg).data,
                'agent_response': MessageSerializer(agent_msg).data,
                'llama_metrics': metrics,
                'system_info': {
                    'model': 'llama3.2:3b',
                    'agent_type': 'literature',
                    'processing_time': processing_time,
                    'performance_grade': minimal_llama_manager.stats.get_performance_grade(),
                    'total_queries': minimal_llama_manager.stats.total_queries
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Erreur agent littéraire Llama: {e}")
            return Response({
                'success': False,
                'error': str(e),
                'model': 'llama3.2:3b'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LlamaMangaAgentView(APIView):
    """Agent manga optimisé avec Llama 3.2 3B"""
    
    permission_classes = []
    
    def post(self, request):
        try:
            message = request.data.get('message')
            if not message:
                return Response({
                    'error': 'Message requis'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Utilisateur demo
            from apps.accounts.models import User
            demo_user, created = User.objects.get_or_create(
                email='demo@example.com',
                defaults={'username': 'demo', 'first_name': 'Demo', 'last_name': 'User'}
            )
            
            # Créer la conversation
            conversation = ConversationHistory.objects.create(
                user=demo_user,
                agent_type='manga',
                title=f"Manga Llama - {message[:30]}..."
            )
            
            # Sauvegarder le message utilisateur
            user_msg = Message.objects.create(
                conversation=conversation,
                sender='user',
                content=message
            )
            
            # Générer la réponse avec Llama optimisé
            start_time = time.time()
            response, metrics = minimal_llama_manager.generate_response(
                message, 
                agent_type='manga'
            )
            processing_time = time.time() - start_time
            
            # Enrichir la réponse avec les métadonnées
            enriched_response = f"🎌 **Recommandations Manga (Llama 3.2 3B)**\n\n{response}"
            enriched_response += f"\n\n⚡ Traitement: {processing_time:.2f}s"
            enriched_response += f" | Tokens: {metrics.get('tokens_generated', 0)}"
            enriched_response += f" | Grade: {minimal_llama_manager.stats.get_performance_grade()}"
            
            # Sauvegarder la réponse
            agent_msg = Message.objects.create(
                conversation=conversation,
                sender='agent',
                content=enriched_response,
                rag_sources="Llama_3.2_3B_manga",
                processing_time=processing_time
            )
            
            conversation.save()
            
            return Response({
                'success': True,
                'conversation_id': conversation.id,
                'user_message': MessageSerializer(user_msg).data,
                'agent_response': MessageSerializer(agent_msg).data,
                'llama_metrics': metrics,
                'system_info': {
                    'model': 'llama3.2:3b',
                    'agent_type': 'manga',
                    'processing_time': processing_time,
                    'performance_grade': minimal_llama_manager.stats.get_performance_grade(),
                    'total_queries': minimal_llama_manager.stats.total_queries
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Erreur agent manga Llama: {e}")
            return Response({
                'success': False,
                'error': str(e),
                'model': 'llama3.2:3b'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LlamaRouterAgentView(APIView):
    """Agent routeur intelligent avec Llama 3.2 3B"""
    
    permission_classes = []
    
    def post(self, request):
        try:
            message = request.data.get('message')
            if not message:
                return Response({
                    'error': 'Message requis'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Utilisateur demo
            from apps.accounts.models import User
            demo_user, created = User.objects.get_or_create(
                email='demo@example.com',
                defaults={'username': 'demo', 'first_name': 'Demo', 'last_name': 'User'}
            )
            
            # Détection automatique du type de requête
            detected_type = self._detect_query_type(message)
            
            # Créer la conversation
            conversation = ConversationHistory.objects.create(
                user=demo_user,
                agent_type=detected_type,
                title=f"Router Llama ({detected_type}) - {message[:30]}..."
            )
            
            # Sauvegarder le message utilisateur
            user_msg = Message.objects.create(
                conversation=conversation,
                sender='user',
                content=message
            )
            
            # Générer la réponse avec Llama optimisé
            start_time = time.time()
            response, metrics = minimal_llama_manager.generate_response(
                message, 
                agent_type=detected_type
            )
            processing_time = time.time() - start_time
            
            # Enrichir la réponse avec les métadonnées
            type_icons = {'tech': '🔧', 'literature': '📚', 'manga': '🎌', 'general': '🤖'}
            icon = type_icons.get(detected_type, '🤖')
            
            enriched_response = f"{icon} **Recommandations {detected_type.title()} (Llama 3.2 3B)**\n\n{response}"
            enriched_response += f"\n\n⚡ Traitement: {processing_time:.2f}s"
            enriched_response += f" | Agent: {detected_type}"
            enriched_response += f" | Tokens: {metrics.get('tokens_generated', 0)}"
            enriched_response += f" | Grade: {minimal_llama_manager.stats.get_performance_grade()}"
            
            # Sauvegarder la réponse
            agent_msg = Message.objects.create(
                conversation=conversation,
                sender='agent',
                content=enriched_response,
                rag_sources=f"Llama_3.2_3B_{detected_type}",
                processing_time=processing_time
            )
            
            conversation.save()
            
            return Response({
                'success': True,
                'conversation_id': conversation.id,
                'user_message': MessageSerializer(user_msg).data,
                'agent_response': MessageSerializer(agent_msg).data,
                'llama_metrics': metrics,
                'system_info': {
                    'model': 'llama3.2:3b',
                    'agent_type': detected_type,
                    'auto_detected': True,
                    'processing_time': processing_time,
                    'performance_grade': minimal_llama_manager.stats.get_performance_grade(),
                    'total_queries': minimal_llama_manager.stats.total_queries
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Erreur agent routeur Llama: {e}")
            return Response({
                'success': False,
                'error': str(e),
                'model': 'llama3.2:3b'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _detect_query_type(self, message: str) -> str:
        """Détecte le type de requête basé sur des mots-clés"""
        message_lower = message.lower()
        
        # Mots-clés techniques
        tech_keywords = [
            'python', 'javascript', 'java', 'programmation', 'code', 'développement',
            'web', 'mobile', 'data science', 'machine learning', 'ia', 'algorithme',
            'framework', 'api', 'database', 'sql', 'développeur', 'informatique'
        ]
        
        # Mots-clés manga/comics
        manga_keywords = [
            'manga', 'anime', 'naruto', 'one piece', 'dragon ball', 'attack on titan',
            'shounen', 'seinen', 'shoujo', 'josei', 'comics', 'bd', 'bande dessinée',
            'superhéros', 'marvel', 'dc', 'tintin', 'astérix'
        ]
        
        # Mots-clés littéraires
        literature_keywords = [
            'roman', 'littérature', 'auteur', 'écrivain', 'poésie', 'théâtre',
            'classique', 'contemporain', 'français', 'étranger', 'prix', 'goncourt',
            'nobel', 'fiction', 'récit', 'nouvelle', 'essai'
        ]
        
        # Compter les occurrences
        tech_score = sum(1 for keyword in tech_keywords if keyword in message_lower)
        manga_score = sum(1 for keyword in manga_keywords if keyword in message_lower)
        literature_score = sum(1 for keyword in literature_keywords if keyword in message_lower)
        
        # Déterminer le type
        if tech_score > 0 and tech_score >= manga_score and tech_score >= literature_score:
            return 'tech'
        elif manga_score > 0 and manga_score >= literature_score:
            return 'manga'
        elif literature_score > 0:
            return 'literature'
        else:
            return 'general'

class LlamaSystemStatusView(APIView):
    """Vue pour le statut du système Llama"""
    
    permission_classes = []
    
    def get(self, request):
        try:
            # Obtenir toutes les informations système
            stats = minimal_llama_manager.get_detailed_stats()
            health = minimal_llama_manager.get_health_status()
            
            system_status = {
                'model_name': minimal_llama_manager.MODEL_NAME,
                'model_info': minimal_llama_manager.MODEL_INFO,
                'health_status': health,
                'performance_stats': stats['performance_stats'],
                'timing_stats': stats['timing_stats'],
                'usage_stats': stats['usage_stats'],
                'recommendations': minimal_llama_manager.get_recommendations(),
                'endpoints': {
                    'tech_agent': '/api/chat/llama/tech/',
                    'literature_agent': '/api/chat/llama/literature/',
                    'manga_agent': '/api/chat/llama/manga/',
                    'router_agent': '/api/chat/llama/router/',
                    'stats': '/api/chat/llama/stats/',
                    'health': '/api/chat/llama/health/',
                    'dashboard': '/api/chat/llama/dashboard/'
                },
                'system_ready': health['status'] == 'healthy'
            }
            
            return Response({
                'success': True,
                'system_status': system_status,
                'timestamp': time.time()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Erreur statut système Llama: {e}")
            return Response({
                'success': False,
                'error': str(e),
                'timestamp': time.time()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)