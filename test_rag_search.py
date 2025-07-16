#!/usr/bin/env python3
"""
Test pour vérifier quel RAG contient "Au Bonheur des Dames"
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

def test_rag_search():
    """Test la recherche dans les différents RAG"""
    
    query = "Au Bonheur des Dames"
    print(f"🔍 Recherche: '{query}'")
    
    # Test Literature RAG
    print("\n📚 Test Literature RAG:")
    try:
        from rags.literature_rag.literature_rag_manager import LiteratureRAGManager
        lit_rag = LiteratureRAGManager()
        lit_results = lit_rag.search_books(query=query, n_results=3)
        
        if lit_results:
            print(f"✅ {len(lit_results)} résultats trouvés")
            for i, result in enumerate(lit_results, 1):
                print(f"  {i}. {result['title']} - {result['authors']}")
        else:
            print("❌ Aucun résultat")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Test Manga RAG
    print("\n🎌 Test Manga RAG:")
    try:
        from rags.manga_rag.manga_rag_manager import MangaRAGManager
        manga_rag = MangaRAGManager()
        manga_results = manga_rag.search_content(query=query, n_results=3)
        
        if manga_results:
            print(f"✅ {len(manga_results)} résultats trouvés")
            for i, result in enumerate(manga_results, 1):
                print(f"  {i}. {result['title']} - {result.get('author', 'N/A')}")
        else:
            print("❌ Aucun résultat")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Test Tech RAG
    print("\n🔧 Test Tech RAG:")
    try:
        from rags.tech_rag.tech_rag_manager import TechRAGManager
        tech_rag = TechRAGManager()
        tech_results = tech_rag.search_books(query=query, n_results=3)
        
        if tech_results:
            print(f"✅ {len(tech_results)} résultats trouvés")
            for i, result in enumerate(tech_results, 1):
                print(f"  {i}. {result['title']} - {result['author']}")
        else:
            print("❌ Aucun résultat")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

def test_specific_agent_responses():
    """Test les réponses spécifiques des agents"""
    
    query = "qui a écrit Au Bonheur des Dames"
    print(f"\n🧪 Test des réponses d'agents pour: '{query}'")
    
    try:
        from agents.simple_agents import SimpleAgentManager
        agent_manager = SimpleAgentManager(use_gemma=False)
        
        # Test agent littéraire
        print("\n📚 Réponse agent littéraire:")
        lit_response = agent_manager.get_literature_recommendations(query)
        print(lit_response[:300] + "...")
        
        # Test agent manga
        print("\n🎌 Réponse agent manga:")
        manga_response = agent_manager.get_manga_recommendations(query)
        print(manga_response[:300] + "...")
        
        # Test via routage
        print("\n🔄 Réponse via routage:")
        routed_response = agent_manager.route_query(query)
        print(routed_response[:300] + "...")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_rag_search()
    test_specific_agent_responses()