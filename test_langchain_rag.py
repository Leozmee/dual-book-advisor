#!/usr/bin/env python
"""
Test du système LangChain avec RAG
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

def test_langchain_system():
    """Test complet du système LangChain"""
    print("🧪 Test du système LangChain avec RAG")
    print("=" * 50)
    
    try:
        # 1. Test de l'intégration Django
        print("\n1. Test de l'intégration Django...")
        from agents.langchain_agents.django_integration import get_django_langchain_bridge
        
        bridge = get_django_langchain_bridge()
        print(f"   Pont disponible: {bridge.is_available()}")
        
        if bridge.is_available():
            status = bridge.get_status()
            print(f"   Statut: {status}")
        
        # 2. Test des RAG tools
        print("\n2. Test des outils RAG...")
        from agents.langchain_agents.tools.rag_tools import (
            TechBookSearchTool,
            LiteratureBookSearchTool,
            validate_rag_systems
        )
        
        rag_status = validate_rag_systems()
        print(f"   Statut RAG: {rag_status}")
        
        # 3. Test Tech RAG
        print("\n3. Test Tech RAG...")
        tech_tool = TechBookSearchTool()
        tech_results = tech_tool._run("Python programming", n_results=2)
        print(f"   Tech results: {len(tech_results)} livres trouvés")
        for book in tech_results[:2]:
            print(f"     - {book.get('title', 'N/A')} par {book.get('author', 'N/A')}")
        
        # 4. Test Literature RAG
        print("\n4. Test Literature RAG...")
        lit_tool = LiteratureBookSearchTool()
        lit_results = lit_tool._run("roman français", n_results=2)
        print(f"   Literature results: {len(lit_results)} livres trouvés")
        for book in lit_results[:2]:
            print(f"     - {book.get('title', 'N/A')} par {book.get('author', 'N/A')}")
        
        # 5. Test LangChain fonctions
        print("\n5. Test des fonctions LangChain...")
        from agents.langchain_agents.django_integration import (
            get_tech_recommendations,
            get_literature_recommendations
        )
        
        print("   Test tech recommendations...")
        tech_response = get_tech_recommendations("apprendre Python", user_id=1)
        print(f"   Tech response: {len(tech_response)} caractères")
        print(f"   Début: {tech_response[:100]}...")
        
        print("   Test literature recommendations...")  
        lit_response = get_literature_recommendations("roman français", user_id=1)
        print(f"   Literature response: {len(lit_response)} caractères")
        print(f"   Début: {lit_response[:100]}...")
        
        print("\n✅ Tests terminés avec succès!")
        
    except Exception as e:
        print(f"\n❌ Erreur durant les tests: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_langchain_system()