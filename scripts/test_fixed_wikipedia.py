#!/usr/bin/env python3
"""
Script pour tester le comportement corrigé de l'agent avec Wikipedia
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

from agents.langchain_agents.nodes.agent_nodes import LiteratureAgentNode
from langchain_community.llms import Ollama

def test_literature_agent_with_wikipedia():
    """Test l'agent littérature avec les corrections Wikipedia"""
    print("🧪 Test agent littérature avec Wikipedia corrigé")
    print("=" * 60)
    
    try:
        # Créer un LLM simple avec Ollama
        try:
            llm = Ollama(model="llama3.2:1b", temperature=0.1)
            print("🤖 Utilisation du modèle Ollama: llama3.2:1b")
        except:
            # Fallback vers un autre modèle
            try:
                llm = Ollama(model="mistral", temperature=0.1)
                print("🤖 Utilisation du modèle Ollama: mistral")
            except:
                print("❌ Aucun modèle Ollama disponible")
                return
        
        # Créer l'agent littérature
        lit_agent = LiteratureAgentNode(llm)
        print("✅ Agent littérature initialisé")
        
        # Questions test
        test_questions = [
            "Qui a écrit Les Misérables ?",
            "Qui est l'auteur de L'Étranger ?",
            "Qui a écrit À la recherche du temps perdu ?",
            "Auteur de Madame Bovary",
            "Qui a écrit Le Rouge et le Noir ?"
        ]
        
        for question in test_questions:
            print(f"\n❓ Question: '{question}'")
            print("-" * 50)
            
            try:
                # Exécuter l'agent
                result = lit_agent.agent_executor.invoke({
                    "input": question
                })
                
                response = result.get("output", "Pas de réponse")
                print(f"✅ Réponse: {response}")
                
                # Afficher les étapes intermédiaires si disponibles
                if "intermediate_steps" in result:
                    steps = result["intermediate_steps"]
                    print(f"🔍 Étapes: {len(steps)} outils utilisés")
                    for i, (action, observation) in enumerate(steps):
                        tool_name = action.tool
                        tool_input = action.tool_input
                        print(f"   {i+1}. {tool_name}: {tool_input}")
                
            except Exception as e:
                print(f"❌ Erreur: {e}")
        
        print(f"\n🎉 Tests terminés!")
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")

def test_direct_tools():
    """Test direct des outils pour comparaison"""
    print("\n🔧 Test direct des outils")
    print("=" * 40)
    
    try:
        from agents.langchain_agents.tools.rag_tools import RAGToolsFactory
        
        # Créer les outils
        lit_tool = RAGToolsFactory.get_tool_by_agent_type("literature")
        wiki_tool = RAGToolsFactory.get_wikipedia_tool()
        
        print("✅ Outils créés")
        
        test_queries = [
            "Les Misérables",
            "L'Étranger",
            "Victor Hugo",
            "Albert Camus"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Test: '{query}'")
            
            # Test outil littérature
            print("   📚 RAG Littérature:")
            try:
                lit_result = lit_tool._run(query)
                if lit_result.get('success') and lit_result.get('books'):
                    books = lit_result['books'][:2]  # 2 premiers
                    for book in books:
                        title = book.get('title', 'N/A')
                        author = book.get('authors', 'N/A')
                        print(f"      - {title} par {author}")
                else:
                    print(f"      ❌ {lit_result.get('message', 'Échec')}")
            except Exception as e:
                print(f"      ❌ Erreur: {e}")
            
            # Test outil Wikipedia
            print("   🌍 Wikipedia:")
            try:
                wiki_result = wiki_tool._run(query)
                if wiki_result.get('success'):
                    title = wiki_result.get('title', 'N/A')
                    summary = wiki_result.get('summary', '')[:100]
                    print(f"      ✅ {title}: {summary}...")
                else:
                    print(f"      ❌ {wiki_result.get('message', 'Échec')}")
            except Exception as e:
                print(f"      ❌ Erreur: {e}")
    
    except Exception as e:
        print(f"❌ Erreur outils: {e}")

def main():
    """Test complet"""
    print("🎯 Test complet Wikipedia corrigé")
    print("=" * 70)
    
    # Test 1: Outils directs
    test_direct_tools()
    
    # Test 2: Agent complet
    test_literature_agent_with_wikipedia()

if __name__ == "__main__":
    main()