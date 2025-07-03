"""
Agents module for book recommendations
"""

from .simple_agents import SimpleAgentManager

# LangChain agents temporairement désactivés
# from .langchain_agents import (
#     BookRecommendationAgent,
#     RouterAgent,
#     LangChainAgentManager
# )

__all__ = [
    'SimpleAgentManager',
    # 'BookRecommendationAgent',
    # 'RouterAgent', 
    # 'LangChainAgentManager'
]