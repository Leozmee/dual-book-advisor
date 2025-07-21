from django.urls import path
from . import views, langchain_views, views_model_management
from .lazy_views import (
    LlamaTechAgentView, LlamaLiteratureAgentView, LlamaMangaAgentView, 
    LlamaRouterAgentView, LlamaSystemStatusView, LlamaStatsView, 
    LlamaHealthView, LlamaTestView, LlamaConfigView, 
    LlamaResetStatsView, LlamaDashboardView,
    LangChainTechAgentChatView, LangChainLiteratureAgentChatView,
    LangChainMangaAgentChatView, LangChainRouterChatView,
    LangChainSystemStatusView, HybridTechAgentChatView,
    DualCoordinatorChatView
)

app_name = 'chat'

urlpatterns = [
    path('conversations/', views.ConversationListView.as_view(), name='conversations'),
    path('conversations/create/', views.ConversationCreateView.as_view(), name='create_conversation'),
    path('conversations/<int:pk>/', views.ConversationDetailView.as_view(), name='conversation_detail'),
    path('conversations/<int:pk>/messages/', views.MessageListView.as_view(), name='messages'),
    path('conversations/<int:conversation_id>/send/', views.SendMessageView.as_view(), name='send_message'),
    path('tech-agent/', views.TechAgentChatView.as_view(), name='tech_agent_chat'),
    path('literature-agent/', views.LiteratureAgentChatView.as_view(), name='literature_agent_chat'),
    path('manga-agent/', views.MangaAgentChatView.as_view(), name='manga_agent_chat'),
    path('coordinator-agent/', views.CoordinatorAgentChatView.as_view(), name='coordinator_agent_chat'),
    
    # LangChain endpoints - legacy function-based views
    path('langchain/', langchain_views.langchain_chat, name='langchain_chat'),
    path('langchain/status/', langchain_views.agent_status, name='agent_status'),
    path('langchain/tech-direct/', langchain_views.tech_agent_direct, name='tech_agent_direct'),
    path('langchain/literature-direct/', langchain_views.literature_agent_direct, name='literature_agent_direct'),
    
    # LangChain endpoints - class-based views
    path('langchain/tech/', LangChainTechAgentChatView.as_view(), name='langchain_tech_agent'),
    path('langchain/literature/', LangChainLiteratureAgentChatView.as_view(), name='langchain_literature_agent'),
    path('langchain/manga/', LangChainMangaAgentChatView.as_view(), name='langchain_manga_agent'),
    path('langchain/router/', LangChainRouterChatView.as_view(), name='langchain_router'),
    path('langchain/status-view/', LangChainSystemStatusView.as_view(), name='langchain_status'),
    
    # URLs hybrides pour migration progressive
    path('hybrid/tech/', HybridTechAgentChatView.as_view(), name='hybrid_tech_agent'),
    
    # URL pour le chat dual coordinateurs (LangChain + Gemma)
    path('dual-coordinator/', DualCoordinatorChatView.as_view(), name='dual_coordinator_chat'),
    
    # URLs pour la gestion des modèles (ancienne version multi-modèles)
    path('models/status/', views_model_management.ModelStatusView.as_view(), name='model_status'),
    path('models/evaluation/', views_model_management.ModelEvaluationView.as_view(), name='model_evaluation'),
    path('models/switch/', views_model_management.ModelSwitchView.as_view(), name='model_switch'),
    path('models/benchmark/', views_model_management.ModelBenchmarkView.as_view(), name='model_benchmark'),
    path('models/config/', views_model_management.ModelConfigView.as_view(), name='model_config'),
    path('models/health/', views_model_management.ModelHealthView.as_view(), name='model_health'),
    
    # URLs pour Llama 3.2 3B optimisé (nouvelle version simplifiée)
    path('llama/tech/', LlamaTechAgentView.as_view(), name='llama_tech_agent'),
    path('llama/literature/', LlamaLiteratureAgentView.as_view(), name='llama_literature_agent'),
    path('llama/manga/', LlamaMangaAgentView.as_view(), name='llama_manga_agent'),
    path('llama/router/', LlamaRouterAgentView.as_view(), name='llama_router_agent'),
    path('llama/status/', LlamaSystemStatusView.as_view(), name='llama_system_status'),
    
    # URLs pour les statistiques Llama
    path('llama/stats/', LlamaStatsView.as_view(), name='llama_stats'),
    path('llama/health/', LlamaHealthView.as_view(), name='llama_health'),
    path('llama/test/', LlamaTestView.as_view(), name='llama_test'),
    path('llama/config/', LlamaConfigView.as_view(), name='llama_config'),
    path('llama/reset-stats/', LlamaResetStatsView.as_view(), name='llama_reset_stats'),
    path('llama/dashboard/', LlamaDashboardView.as_view(), name='llama_dashboard'),
]