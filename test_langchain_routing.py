#!/usr/bin/env python3
"""
Test spécifique pour le système LangChain
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from agents.langchain_agents.nodes.classifier_node import ClassifierNode
from agents.langchain_agents.graph_manager import BookAdvisorGraphManager
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_langchain_routing():
    """Test le routage avec le système LangChain"""
    
    print("🔍 Test avec le système LangChain")
    
    try:
        # Initialiser le BookAdvisorGraphManager avec Ollama
        graph_manager = BookAdvisorGraphManager(
            llm_provider="ollama",
            model_name="llama3.2:3b"
        )
        
        # Test queries
        queries = [
            "qui a écrit Au Bonheur des Dames",
            "j'ai aimé Naruto",
            "livres Python débutant",
            "romans comme Tolstoï"
        ]
        
        for query in queries:
            print(f"\n📝 Query: '{query}'")
            
            try:
                # Utiliser le graph manager pour traiter la requête
                result = graph_manager.get_recommendation(query, user_id=1)
                
                # Analyser la réponse
                if result and 'response' in result:
                    response = result['response']
                    agent_used = result.get('agent_used', 'unknown')
                    
                    print(f"  Agent utilisé: {agent_used}")
                    print(f"  Réponse: {response[:150]}...")
                    
                    # Vérifier la classification pour Au Bonheur des Dames
                    if query == "qui a écrit Au Bonheur des Dames":
                        expected_agent = "literature"
                        success = (agent_used == expected_agent)
                        status = "✅ RÉUSSI" if success else "❌ ÉCHOUÉ"
                        
                        print(f"  Expected: {expected_agent}")
                        print(f"  Status: {status}")
                        
                        if not success:
                            print(f"  ⚠️ PROBLÈME: La question littéraire va vers {agent_used}")
                            
                            # Analyser pourquoi
                            if 'metadata' in result and 'classification' in result['metadata']:
                                classification = result['metadata']['classification']
                                print(f"  Reasoning: {classification.get('reasoning', 'N/A')}")
                                print(f"  Keywords: {classification.get('detected_keywords', [])}")
                else:
                    print(f"  ❌ Pas de réponse obtenue")
                    
            except Exception as e:
                print(f"  ❌ Erreur lors du traitement: {e}")
                
    except Exception as e:
        print(f"❌ Erreur initialisation GraphManager: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_langchain_routing()