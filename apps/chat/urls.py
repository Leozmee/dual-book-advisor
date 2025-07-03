from django.urls import path
from . import views, langchain_views

app_name = 'chat'

urlpatterns = [
    path('conversations/', views.ConversationListView.as_view(), name='conversations'),
    path('conversations/create/', views.ConversationCreateView.as_view(), name='create_conversation'),
    path('conversations/<int:pk>/', views.ConversationDetailView.as_view(), name='conversation_detail'),
    path('conversations/<int:pk>/messages/', views.MessageListView.as_view(), name='messages'),
    path('conversations/<int:conversation_id>/send/', views.SendMessageView.as_view(), name='send_message'),
    path('tech-agent/', views.TechAgentChatView.as_view(), name='tech_agent_chat'),
    path('literature-agent/', views.LiteratureAgentChatView.as_view(), name='literature_agent_chat'),
    
    # LangChain endpoints
    path('langchain/', langchain_views.langchain_chat, name='langchain_chat'),
    path('langchain/status/', langchain_views.agent_status, name='agent_status'),
    path('langchain/tech/', langchain_views.tech_agent_direct, name='tech_agent_direct'),
    path('langchain/literature/', langchain_views.literature_agent_direct, name='literature_agent_direct'),
]