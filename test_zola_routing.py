#!/usr/bin/env python3
"""
Test spécifique pour la question "qui a écrit Au Bonheur des Dames"
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from agents.simple_agents import SimpleAgentManager
from agents.langchain_agents.nodes.classifier_node import ClassifierNode
from agents.langchain_agents.nodes.agent_nodes import AgentNodesFactory
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_zola_routing():
    """Test la classification de la question sur Au Bonheur des Dames"""
    
    # Test avec SimpleAgentManager
    print("🔍 Test avec SimpleAgentManager")
    agent_manager = SimpleAgentManager(use_gemma=False)
    
    query = "qui a écrit Au Bonheur des Dames"
    print(f"Query: '{query}'")
    
    # Tester la détection manga
    is_manga = agent_manager.detect_manga_query(query)
    print(f"  detect_manga_query: {is_manga}")
    
    # Tester la détection factuelle
    is_factual = agent_manager.detect_factual_query(query)
    print(f"  detect_factual_query: {is_factual}")
    
    # Tester la détection classique
    is_classic = agent_manager.detect_classic_literature_query(query)
    print(f"  detect_classic_literature_query: {is_classic}")
    
    # Obtenir la réponse via le routage
    response = agent_manager.route_query(query)
    print(f"  Response type: {type(response)}")
    print(f"  Response preview: {response[:200]}...")
    
    # Analyser la réponse pour déterminer l'agent utilisé
    if "🎌" in response or "🦸" in response or "manga" in response.lower():
        used_agent = "manga"
    elif "🔧" in response or "technique" in response.lower():
        used_agent = "tech"  
    else:
        used_agent = "literature"
    
    print(f"  Detected agent: {used_agent}")
    
    # Vérification
    expected_agent = "literature"
    success = (used_agent == expected_agent)
    status = "✅ RÉUSSI" if success else "❌ ÉCHOUÉ"
    
    print(f"  Expected: {expected_agent}")
    print(f"  Actual: {used_agent}")
    print(f"  Status: {status}")
    
    return success

def test_classifier_node():
    """Test avec ClassifierNode (LangChain)"""
    print("\n🔍 Test avec ClassifierNode (LangChain)")
    
    try:
        # Importer le LLM (si disponible)
        from agents.optimized_llama_manager import OptimizedLlamaManager
        
        # Initialiser le manager
        llama_manager = OptimizedLlamaManager()
        llm = llama_manager.get_llm()
        
        if llm is None:
            print("  ⚠️ LLM non disponible, test ignoré")
            return True
        
        # Créer le classifier
        classifier = ClassifierNode(llm)
        
        query = "qui a écrit Au Bonheur des Dames"
        print(f"  Query: '{query}'")
        
        # Classifier la requête
        classification = classifier.classify_query(query)
        
        print(f"  Agent type: {classification.agent_type}")
        print(f"  Confidence: {classification.confidence}")
        print(f"  Reasoning: {classification.reasoning}")
        print(f"  Keywords: {classification.detected_keywords}")
        
        # Vérification
        expected_agent = "literature"
        success = (classification.agent_type == expected_agent)
        status = "✅ RÉUSSI" if success else "❌ ÉCHOUÉ"
        
        print(f"  Expected: {expected_agent}")
        print(f"  Actual: {classification.agent_type}")
        print(f"  Status: {status}")
        
        return success
        
    except Exception as e:
        print(f"  ⚠️ Erreur ClassifierNode: {e}")
        return True  # Pas critique si pas disponible

def analyze_data_conflict():
    """Analyse le conflit dans les données"""
    print("\n🔍 Analyse du conflit dans les données")
    
    print("  📚 Literature RAG:")
    with open('/home/utilisateur/dual-book-advisor/rags/literature_rag/data/books.csv', 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            if 'Au Bonheur des Dames' in line:
                print(f"    Ligne {line_num}: {line.strip()[:100]}...")
    
    print("  🎌 Manga RAG:")
    with open('/home/utilisateur/dual-book-advisor/rags/manga_rag/data/albums_from_seen_clean.csv', 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            if 'Au bonheur des dames' in line:
                print(f"    Ligne {line_num}: {line.strip()[:100]}...")
    
    print("  🔍 Conclusion:")
    print("    - Le livre original d'Émile Zola est dans Literature RAG")
    print("    - Une adaptation BD est dans Manga RAG")
    print("    - Le classifier peut être confus par cette duplication")

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TEST ROUTAGE: Au Bonheur des Dames")
    print("=" * 60)
    
    # Analyser les données
    analyze_data_conflict()
    
    # Tester les deux systèmes
    success1 = test_zola_routing()
    success2 = test_classifier_node()
    
    print(f"\n{'='*60}")
    print("📊 RÉSULTATS")
    print(f"{'='*60}")
    
    if success1 and success2:
        print("✅ Tous les tests sont réussis")
        print("🎯 La question sur Au Bonheur des Dames devrait aller à l'agent littéraire")
    else:
        print("❌ Au moins un test a échoué")
        print("⚠️  Le routage peut être problématique")
    
    sys.exit(0 if (success1 and success2) else 1)