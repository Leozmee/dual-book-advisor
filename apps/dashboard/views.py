from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from apps.chat.models import ConversationHistory, Message
from apps.books.models import Recommendation, TechBook, LiteratureBook
from apps.accounts.models import User


class DashboardView(TemplateView):
    """
    Home page view serving HTML template
    """
    template_name = 'dashboard/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stats'] = {
            'tech_books': TechBook.objects.count(),
            'literature_books': LiteratureBook.objects.count(),
            'total_users': User.objects.count(),
            'total_conversations': ConversationHistory.objects.count(),
        }
        return context


class ChatView(TemplateView):
    """
    Chat interface view
    """
    template_name = 'chat/chat.html'


class DashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Get user's conversation statistics
        conversations = ConversationHistory.objects.filter(user=user)
        tech_conversations = conversations.filter(agent_type='tech').count()
        literature_conversations = conversations.filter(agent_type='literature').count()
        
        # Get recent conversations
        recent_conversations = conversations.order_by('-updated_at')[:5]
        
        # Get message statistics
        total_messages = Message.objects.filter(conversation__user=user).count()
        user_messages = Message.objects.filter(conversation__user=user, sender='user').count()
        
        # Get recommendations
        recommendations = Recommendation.objects.filter(user=user).order_by('-created_at')[:5]
        
        return Response({
            'user': {
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            },
            'statistics': {
                'total_conversations': conversations.count(),
                'tech_conversations': tech_conversations,
                'literature_conversations': literature_conversations,
                'total_messages': total_messages,
                'user_messages': user_messages,
                'total_recommendations': recommendations.count(),
            },
            'recent_conversations': [
                {
                    'id': conv.id,
                    'title': conv.title,
                    'agent_type': conv.agent_type,
                    'updated_at': conv.updated_at,
                    'message_count': conv.messages.count()
                }
                for conv in recent_conversations
            ],
            'recent_recommendations': [
                {
                    'id': rec.id,
                    'book_title': rec.book_title,
                    'agent_type': rec.agent_type,
                    'score': rec.score,
                    'created_at': rec.created_at,
                    'reason': rec.reason[:100] + '...' if len(rec.reason) > 100 else rec.reason
                }
                for rec in recommendations
            ]
        })


class UserStatsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Conversation stats by agent type
        conversation_stats = ConversationHistory.objects.filter(user=user).values('agent_type').annotate(
            count=Count('id')
        )
        
        # Message stats by month (last 6 months)
        from django.utils import timezone
        from datetime import datetime, timedelta
        
        six_months_ago = timezone.now() - timedelta(days=180)
        
        message_stats = Message.objects.filter(
            conversation__user=user,
            created_at__gte=six_months_ago
        ).extra(
            select={'month': "date_trunc('month', created_at)"}
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')
        
        return Response({
            'conversation_stats': list(conversation_stats),
            'message_stats': list(message_stats),
            'total_conversations': ConversationHistory.objects.filter(user=user).count(),
            'total_messages': Message.objects.filter(conversation__user=user).count(),
            'total_recommendations': Recommendation.objects.filter(user=user).count(),
        })