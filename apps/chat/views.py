from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import ConversationHistory, Message
from .serializers import ConversationHistorySerializer, MessageSerializer
from agents.simple_agents import SimpleAgentManager
from typing import List, Dict
import logging
import time

logger = logging.getLogger(__name__)


class ConversationListView(generics.ListAPIView):
    serializer_class = ConversationHistorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ConversationHistory.objects.filter(user=self.request.user).order_by('-updated_at')


class ConversationCreateView(generics.CreateAPIView):
    serializer_class = ConversationHistorySerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ConversationDetailView(generics.RetrieveAPIView):
    serializer_class = ConversationHistorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ConversationHistory.objects.filter(user=self.request.user)


class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        conversation_id = self.kwargs['pk']
        conversation = get_object_or_404(
            ConversationHistory, 
            id=conversation_id, 
            user=self.request.user
        )
        return Message.objects.filter(conversation=conversation).order_by('created_at')


class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, conversation_id):
        conversation = get_object_or_404(
            ConversationHistory, 
            id=conversation_id, 
            user=request.user
        )
        
        user_message = request.data.get('message')
        if not user_message:
            return Response({
                'error': 'Message is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Save user message
        user_msg = Message.objects.create(
            conversation=conversation,
            sender='user',
            content=user_message
        )
        
        # Get agent response based on conversation type
        try:
            if conversation.agent_type == 'tech':
                agent_response = self._get_tech_agent_response(user_message, conversation)
            else:
                agent_response = self._get_literature_agent_response(user_message, conversation)
            
            # Save agent response with RAG metadata
            agent_msg = Message.objects.create(
                conversation=conversation,
                sender='agent',
                content=agent_response,
                rag_sources=f"RAG_{conversation.agent_type}_search"
            )
            
            # Update conversation timestamp
            conversation.save()
            
            return Response({
                'user_message': MessageSerializer(user_msg).data,
                'agent_response': MessageSerializer(agent_msg).data
            })
            
        except Exception as e:
            return Response({
                'error': f'Failed to get agent response: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_tech_agent_response(self, message, conversation):
        """Générer une réponse intelligente avec l'agent technique"""
        try:
            start_time = time.time()
            agent_manager = SimpleAgentManager()
            
            # Obtenir des recommandations de l'agent technique
            response = agent_manager.get_tech_recommendations(
                query=message,
                user_id=conversation.user.id
            )
            
            processing_time = time.time() - start_time
            response += f"\n\n⚡ Recherche sémantique - {processing_time:.2f}s"
            
            return response
                
        except Exception as e:
            logger.error(f"Erreur dans l'agent technique: {e}")
            return f"🔧 Désolé, j'ai rencontré un problème technique. Pouvez-vous reformuler votre demande ?"
    
    def _generate_contextual_intro(self, message: str, recommendations: List[Dict]) -> str:
        """Génère une introduction contextuelle basée sur la requête utilisateur"""
        import re
        
        message_lower = message.lower()
        
        # Détection des contextes spécifiques
        if re.search(r'\b(musique|music|audio)\b', message_lower):
            return "Excellent choix ! La programmation audio et musicale est un domaine fascinant. Voici mes recommandations pour allier votre passion musicale à la technologie :"
        
        elif re.search(r'\b(sport|fitness|santé|health)\b', message_lower):
            return "Parfait ! Le sport et la technologie se marient très bien. Voici des recommandations pour développer des applications fitness, analyser des données sportives ou créer des outils de santé :"
        
        elif re.search(r'\b(art|design|créatif)\b', message_lower):
            return "Génial ! La programmation créative ouvre des horizons infinis. Voici mes suggestions pour allier art et code :"
        
        elif re.search(r'\b(jeu|game|gaming)\b', message_lower):
            return "Excellent ! Le développement de jeux est un domaine passionnant. Voici mes recommandations pour créer vos propres jeux :"
        
        elif re.search(r'\b(apprendre|learn|débutant|beginner)\b', message_lower):
            return "Parfait pour débuter ! J'ai sélectionné des livres adaptés aux débutants pour vous lancer dans la programmation :"
        
        elif re.search(r'\b(web|site|internet)\b', message_lower):
            return "Le développement web est un excellent choix ! Voici mes recommandations pour créer des sites et applications web modernes :"
        
        elif re.search(r'\b(mobile|app|application)\b', message_lower):
            return "Les applications mobiles ont un grand avenir ! Voici mes suggestions pour développer vos propres apps :"
        
        elif re.search(r'\b(data|données|machine learning|ai)\b', message_lower):
            return "La data science et l'IA sont des domaines d'avenir ! Voici mes recommandations pour maîtriser ces technologies :"
        
        else:
            return "J'ai analysé votre demande et voici mes recommandations techniques personnalisées :"
    
    def _generate_fallback_response(self, message: str) -> str:
        """Génère une réponse de fallback adaptative quand aucun livre n'est trouvé"""
        import re
        
        message_lower = message.lower()
        
        # Suggestions contextuelles même sans résultats
        if re.search(r'\b(musique|music|audio)\b', message_lower):
            return "🔧 Je comprends votre intérêt pour la musique ! Même si je n'ai pas trouvé de correspondance exacte, essayez de rechercher 'Python audio' ou 'JavaScript music' pour des livres sur la programmation musicale."
        
        elif re.search(r'\b(sport|fitness|santé|health)\b', message_lower):
            return "🔧 Votre passion pour le sport est inspirante ! Recherchez 'Python data analysis' ou 'mobile app development' pour créer des applications fitness et analyser des données sportives."
        
        elif re.search(r'\b(art|design|créatif)\b', message_lower):
            return "🔧 L'art et la programmation font bon ménage ! Essayez 'creative coding', 'Python graphics' ou 'JavaScript animation' pour des projets artistiques."
        
        else:
            return "🔧 Je n'ai pas trouvé de correspondance exacte, mais je peux vous aider ! Précisez un langage (Python, JavaScript, C#) ou un domaine (web, mobile, data) qui vous intéresse."
    
    def _get_literature_agent_response(self, message, conversation):
        """Générer une réponse intelligente avec l'agent littéraire"""
        try:
            start_time = time.time()
            agent_manager = SimpleAgentManager()
            
            # Obtenir des recommandations de l'agent littéraire
            response = agent_manager.get_literature_recommendations(
                query=message,
                user_id=conversation.user.id
            )
            
            processing_time = time.time() - start_time
            response += f"\n\n⚡ Recherche sémantique - {processing_time:.2f}s"
            
            return response
                
        except Exception as e:
            logger.error(f"Erreur dans l'agent littéraire: {e}")
            return f"📚 Désolé, j'ai rencontré un problème. Pouvez-vous reformuler votre demande littéraire ?"


class TechAgentChatView(APIView):
    permission_classes = []  # Temporarily disable auth for testing
    
    def post(self, request):
        message = request.data.get('message')
        if not message:
            return Response({
                'error': 'Message is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # For demo purposes, use a default user or create anonymous session
        from apps.accounts.models import User
        demo_user, created = User.objects.get_or_create(
            email='demo@example.com',
            defaults={'username': 'demo', 'first_name': 'Demo', 'last_name': 'User'}
        )
        
        # Create new conversation for each chat session
        conversation = ConversationHistory.objects.create(
            user=demo_user,
            agent_type='tech',
            title=f"Tech Chat - {message[:30]}..."
        )
        
        # Save user message
        user_msg = Message.objects.create(
            conversation=conversation,
            sender='user',
            content=message
        )
        
        # Get tech book recommendations using SimpleAgentManager
        agent_manager = SimpleAgentManager()
        tech_response = agent_manager.get_tech_recommendations(message, demo_user.id)
        
        agent_msg = Message.objects.create(
            conversation=conversation,
            sender='agent',
            content=tech_response,
            rag_sources="RAG_tech_recommendations"
        )
        
        conversation.save()
        
        return Response({
            'conversation_id': conversation.id,
            'user_message': MessageSerializer(user_msg).data,
            'agent_response': MessageSerializer(agent_msg).data
        })
    
    def _get_tech_recommendation(self, message):
        """Obtenir des recommandations techniques intelligentes avec RAG"""
        try:
            start_time = time.time()
            tech_rag = TechRAGManager()
            
            # Utiliser l'utilisateur demo par défaut
            from apps.accounts.models import User
            demo_user = User.objects.get(email='demo@example.com')
            
            # Obtenir des recommandations basées sur le RAG
            recommendations = tech_rag.get_book_recommendations(
                user_id=demo_user.id,
                query=message,
                n_recommendations=3
            )
            
            processing_time = time.time() - start_time
            
            if recommendations:
                # Analyser le contexte de la requête pour personnaliser la réponse
                context_intro = self._generate_contextual_intro(message, recommendations)
                response = f"🔧 {context_intro}\n\n"
                
                for i, rec in enumerate(recommendations, 1):
                    book = rec['book']
                    response += f"{i}. **{book['title']}** par {book['author']}\n"
                    response += f"   ⭐ Note: {book['rating']}/5"
                    if book['price'] > 0:
                        response += f" | 💰 ${book['price']}"
                    response += f"\n   📊 Pertinence: {rec['similarity_score']:.1%}\n"
                    response += f"   💡 {rec['reason']}\n"
                    response += f"   📖 {book['description'][:120]}...\n\n"
                
                response += f"\n⚡ Recherche sémantique - {processing_time:.2f}s"
                return response
            else:
                return self._generate_fallback_response(message)
                
        except Exception as e:
            logger.error(f"Erreur RAG technique: {e}")
            # Fallback vers l'ancienne méthode en cas d'erreur
            from apps.books.models import TechBook
            books = TechBook.objects.filter(rating__gte=4.0).order_by('?')[:2]
            if books:
                response = "🔧 Voici quelques excellents livres techniques:\n\n"
                for book in books:
                    response += f"📚 **{book.title}** par {book.author}\n"
                    response += f"⭐ Note: {book.rating}/5\n\n"
                return response
            return "🔧 Je suis là pour vous aider avec les recommandations techniques!"
    
    def _generate_contextual_intro(self, message: str, recommendations: List[Dict]) -> str:
        """Génère une introduction contextuelle basée sur la requête utilisateur"""
        import re
        
        message_lower = message.lower()
        
        # Détection des contextes spécifiques
        if re.search(r'\b(musique|music|audio)\b', message_lower):
            return "Excellent choix ! La programmation audio et musicale est un domaine fascinant. Voici mes recommandations pour allier votre passion musicale à la technologie :"
        
        elif re.search(r'\b(sport|fitness|santé|health)\b', message_lower):
            return "Parfait ! Le sport et la technologie se marient très bien. Voici des recommandations pour développer des applications fitness, analyser des données sportives ou créer des outils de santé :"
        
        elif re.search(r'\b(art|design|créatif)\b', message_lower):
            return "Génial ! La programmation créative ouvre des horizons infinis. Voici mes suggestions pour allier art et code :"
        
        elif re.search(r'\b(jeu|game|gaming)\b', message_lower):
            return "Excellent ! Le développement de jeux est un domaine passionnant. Voici mes recommandations pour créer vos propres jeux :"
        
        elif re.search(r'\b(apprendre|learn|débutant|beginner)\b', message_lower):
            return "Parfait pour débuter ! J'ai sélectionné des livres adaptés aux débutants pour vous lancer dans la programmation :"
        
        elif re.search(r'\b(web|site|internet)\b', message_lower):
            return "Le développement web est un excellent choix ! Voici mes recommandations pour créer des sites et applications web modernes :"
        
        elif re.search(r'\b(mobile|app|application)\b', message_lower):
            return "Les applications mobiles ont un grand avenir ! Voici mes suggestions pour développer vos propres apps :"
        
        elif re.search(r'\b(data|données|machine learning|ai)\b', message_lower):
            return "La data science et l'IA sont des domaines d'avenir ! Voici mes recommandations pour maîtriser ces technologies :"
        
        else:
            return "J'ai analysé votre demande et voici mes recommandations techniques personnalisées :"
    
    def _generate_fallback_response(self, message: str) -> str:
        """Génère une réponse de fallback adaptative quand aucun livre n'est trouvé"""
        import re
        
        message_lower = message.lower()
        
        # Suggestions contextuelles même sans résultats
        if re.search(r'\b(musique|music|audio)\b', message_lower):
            return "🔧 Je comprends votre intérêt pour la musique ! Même si je n'ai pas trouvé de correspondance exacte, essayez de rechercher 'Python audio' ou 'JavaScript music' pour des livres sur la programmation musicale."
        
        elif re.search(r'\b(sport|fitness|santé|health)\b', message_lower):
            return "🔧 Votre passion pour le sport est inspirante ! Recherchez 'Python data analysis' ou 'mobile app development' pour créer des applications fitness et analyser des données sportives."
        
        elif re.search(r'\b(art|design|créatif)\b', message_lower):
            return "🔧 L'art et la programmation font bon ménage ! Essayez 'creative coding', 'Python graphics' ou 'JavaScript animation' pour des projets artistiques."
        
        else:
            return "🔧 Je n'ai pas trouvé de correspondance exacte, mais je peux vous aider ! Précisez un langage (Python, JavaScript, C#) ou un domaine (web, mobile, data) qui vous intéresse."


class LiteratureAgentChatView(APIView):
    permission_classes = []  # Temporarily disable auth for testing
    
    def post(self, request):
        message = request.data.get('message')
        if not message:
            return Response({
                'error': 'Message is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # For demo purposes, use a default user or create anonymous session
        from apps.accounts.models import User
        demo_user, created = User.objects.get_or_create(
            email='demo@example.com',
            defaults={'username': 'demo', 'first_name': 'Demo', 'last_name': 'User'}
        )
        
        # Create new conversation for each chat session
        conversation = ConversationHistory.objects.create(
            user=demo_user,
            agent_type='literature',
            title=f"Literature Chat - {message[:30]}..."
        )
        
        # Save user message
        user_msg = Message.objects.create(
            conversation=conversation,
            sender='user',
            content=message
        )
        
        # Get literature book recommendations based on message
        literature_response = self._get_literature_recommendation(message)
        
        agent_msg = Message.objects.create(
            conversation=conversation,
            sender='agent',
            content=literature_response,
            rag_sources="RAG_literature_recommendations"
        )
        
        conversation.save()
        
        return Response({
            'conversation_id': conversation.id,
            'user_message': MessageSerializer(user_msg).data,
            'agent_response': MessageSerializer(agent_msg).data
        })
    def _get_literature_recommendation(self, message):
        """Obtenir des recommandations littéraires intelligentes avec RAG"""
        try:
            start_time = time.time()
            literature_rag = LiteratureRAGManager()
            
            # Utiliser l'utilisateur demo par défaut
            from apps.accounts.models import User
            demo_user = User.objects.get(email='demo@example.com')
            
            # Obtenir des recommandations basées sur le RAG
            recommendations = literature_rag.get_book_recommendations(
                user_id=demo_user.id,
                query=message,
                n_recommendations=3
            )
            
            processing_time = time.time() - start_time
            
            if recommendations:
                response = "📚 Mes suggestions littéraires personnalisées:\n\n"
                
                for i, rec in enumerate(recommendations, 1):
                    book = rec['book']
                    response += f"{i}. **{book['title']}** de {book['authors']}\n"
                    response += f"   ⭐ Note: {book['average_rating']}/5"
                    if book['published_year']:
                        response += f" | 📅 {book['published_year']}"
                    response += f"\n   📊 Pertinence: {rec['similarity_score']:.1%}\n"
                    response += f"   💡 {rec['reason']}\n"
                    response += f"   📖 {book['description'][:120]}...\n\n"
                
                response += f"\n⚡ Recherche sémantique - {processing_time:.2f}s"
                return response
            else:
                return "📚 Je n'ai pas trouvé de livres correspondant exactement à votre demande. Parlez-moi des genres, auteurs ou ambiances qui vous plaisent!"
                
        except Exception as e:
            logger.error(f"Erreur RAG littéraire: {e}")
            # Fallback vers l'ancienne méthode en cas d'erreur
            from apps.books.models import LiteratureBook
            books = LiteratureBook.objects.filter(average_rating__gte=4.0).order_by('?')[:2]
            if books:
                response = "📚 Voici d'excellents livres littéraires:\n\n"
                for book in books:
                    response += f"📚 **{book.title}** de {book.authors}\n"
                    response += f"⭐ Note: {book.average_rating}/5\n\n"
                return response
            return "📚 Je suis là pour vous faire découvrir de merveilleux livres!"
