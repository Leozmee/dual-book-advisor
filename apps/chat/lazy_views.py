"""
Lazy view loading to avoid blocking Django startup
"""
from django.utils.module_loading import import_string
from django.views.generic.base import View

class LazyViewWrapper:
    """Wrapper to load views lazily"""
    def __init__(self, view_path):
        self.view_path = view_path
        self._view = None
    
    def __call__(self, *args, **kwargs):
        if self._view is None:
            self._view = import_string(self.view_path)
        return self._view(*args, **kwargs)
    
    def as_view(self, *args, **kwargs):
        if self._view is None:
            self._view = import_string(self.view_path)
        return self._view.as_view(*args, **kwargs)

# Lazy views for llama agents
LlamaTechAgentView = LazyViewWrapper('apps.chat.views_llama_agents.LlamaTechAgentView')
LlamaLiteratureAgentView = LazyViewWrapper('apps.chat.views_llama_agents.LlamaLiteratureAgentView')
LlamaMangaAgentView = LazyViewWrapper('apps.chat.views_llama_agents.LlamaMangaAgentView')
LlamaRouterAgentView = LazyViewWrapper('apps.chat.views_llama_agents.LlamaRouterAgentView')
LlamaSystemStatusView = LazyViewWrapper('apps.chat.views_llama_agents.LlamaSystemStatusView')

# Lazy views for llama stats
LlamaStatsView = LazyViewWrapper('apps.chat.views_llama_stats.LlamaStatsView')
LlamaHealthView = LazyViewWrapper('apps.chat.views_llama_stats.LlamaHealthView')
LlamaTestView = LazyViewWrapper('apps.chat.views_llama_stats.LlamaTestView')
LlamaConfigView = LazyViewWrapper('apps.chat.views_llama_stats.LlamaConfigView')
LlamaResetStatsView = LazyViewWrapper('apps.chat.views_llama_stats.LlamaResetStatsView')
LlamaDashboardView = LazyViewWrapper('apps.chat.views_llama_stats.LlamaDashboardView')

# Lazy views for langchain
LangChainTechAgentChatView = LazyViewWrapper('apps.chat.views_langchain.LangChainTechAgentChatView')
LangChainLiteratureAgentChatView = LazyViewWrapper('apps.chat.views_langchain.LangChainLiteratureAgentChatView')
LangChainMangaAgentChatView = LazyViewWrapper('apps.chat.views_langchain.LangChainMangaAgentChatView')
LangChainRouterChatView = LazyViewWrapper('apps.chat.views_langchain.LangChainRouterChatView')
LangChainSystemStatusView = LazyViewWrapper('apps.chat.views_langchain.LangChainSystemStatusView')
HybridTechAgentChatView = LazyViewWrapper('apps.chat.views_langchain.HybridTechAgentChatView')
DualCoordinatorChatView = LazyViewWrapper('apps.chat.views_langchain.DualCoordinatorChatView')