#!/usr/bin/env python3
"""
Script pour tester l'outil Wikipedia directement
"""
import os
import sys
import django
from pathlib import Path

# Configuration Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

django.setup()

from agents.langchain_agents.tools.rag_tools import RAGToolsFactory
import wikipedia

def test_wikipedia_direct():
    """Test direct de la bibliothèque Wikipedia"""
    print("🔍 Test direct Wikipedia")
    print("=" * 50)
    
    test_queries = [
        "Victor Hugo",
        "Les Misérables",
        "Albert Camus",
        "L'Étranger",
        "Marcel Proust",
        "À la recherche du temps perdu"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Recherche directe: '{query}'")
        try:
            # Test recherche en français
            wikipedia.set_lang("fr")
            search_results = wikipedia.search(query, results=3)
            print(f"   Résultats: {search_results}")
            
            if search_results:
                try:
                    page = wikipedia.page(search_results[0])
                    summary = wikipedia.summary(search_results[0], sentences=2)
                    print(f"   ✅ Titre: {page.title}")
                    print(f"   📝 Résumé: {summary[:200]}...")
                except Exception as e:
                    print(f"   ❌ Erreur page: {e}")
            else:
                print("   ❌ Aucun résultat")
                
        except Exception as e:
            print(f"   ❌ Erreur recherche: {e}")

def test_wikipedia_tool():
    """Test de l'outil Wikipedia LangChain"""
    print("\n🛠️ Test outil Wikipedia LangChain")
    print("=" * 50)
    
    try:
        wiki_tool = RAGToolsFactory.get_wikipedia_tool()
        print("✅ Outil Wikipedia créé")
        
        test_queries = [
            "Victor Hugo",
            "Les Misérables Victor Hugo",
            "Albert Camus",
            "L'Étranger Camus",
            "qui a écrit les misérables",
            "auteur de l'étranger"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Test outil: '{query}'")
            try:
                result = wiki_tool._run(query)
                print(f"   Success: {result.get('success')}")
                print(f"   Titre: {result.get('title', 'N/A')}")
                print(f"   Type: {result.get('type', 'N/A')}")
                if result.get('success'):
                    summary = result.get('summary', '')
                    print(f"   Résumé: {summary[:150]}...")
                else:
                    print(f"   Message: {result.get('message', 'N/A')}")
                    
            except Exception as e:
                print(f"   ❌ Erreur: {e}")
                
    except Exception as e:
        print(f"❌ Erreur création outil: {e}")

def test_literature_agent():
    """Test de l'agent littérature complet"""
    print("\n📚 Test agent littérature")
    print("=" * 50)
    
    try:
        from agents.langchain_agents.graph_manager import LangChainGraphManager
        from config.settings.llm_config import LLMConfig
        
        # Créer le manager avec un LLM simple
        llm_config = LLMConfig()
        available_models = llm_config.get_available_models()
        if not available_models:
            print("❌ Aucun modèle LLM disponible")
            return
            
        # Utiliser le premier modèle disponible
        model_name = list(available_models.keys())[0]
        print(f"🤖 Utilisation du modèle: {model_name}")
        
        graph_manager = LangChainGraphManager()
        
        test_questions = [
            "Qui a écrit Les Misérables?",
            "Qui est l'auteur de L'Étranger?",
            "Qui a écrit À la recherche du temps perdu?"
        ]
        
        for question in test_questions:
            print(f"\n❓ Question: '{question}'")
            try:
                # Simuler une requête utilisateur
                result = graph_manager.process_user_input(
                    user_input=question,
                    user_id=1,
                    session_id="test",
                    agent_type="literature"
                )
                print(f"   ✅ Réponse: {result.get('response', 'N/A')[:200]}...")
                
            except Exception as e:
                print(f"   ❌ Erreur agent: {e}")
                
    except Exception as e:
        print(f"❌ Erreur test agent: {e}")

def main():
    """Test complet du système Wikipedia"""
    print("🎯 Diagnostic complet Wikipedia")
    print("=" * 60)
    
    # Test 1: Bibliothèque Wikipedia directe
    test_wikipedia_direct()
    
    # Test 2: Outil Wikipedia LangChain
    test_wikipedia_tool()
    
    # Test 3: Agent littérature complet
    test_literature_agent()
    
    print("\n🎉 Tests terminés!")

if __name__ == "__main__":
    main()