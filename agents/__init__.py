"""
Agents module for book recommendations
"""

from .simple_agents import SimpleAgentManager
from .ollama_gemma_manager import GemmaAgentManager, OllamaGemmaManager

__all__ = [
    'SimpleAgentManager',
    'GemmaAgentManager',
    'OllamaGemmaManager'
]