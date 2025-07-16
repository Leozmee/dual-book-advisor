#!/usr/bin/env python
"""
Test script pour vérifier que les corrections fonctionnent
"""
import os
import sys
import django
from django.conf import settings

# Configurer Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from agents.langchain_agents.tools.rag_tools import LiteratureBookSearchTool

def test_author_questions():
    """Test des questions d'auteur"""
    
    tool = LiteratureBookSearchTool()
    
    test_cases = [
        "qui a écrit l'Assommoir",
        "qui a écrit la peste",
        "qui a écrit les misérables",
        "qui a écrit Don Quichotte",
        "qui a écrit Hamlet"
    ]
    
    print("=== Test des questions d'auteur ===")
    print("Vérification que le système trouve les bons auteurs via Wikipedia\n")
    
    for i, query in enumerate(test_cases, 1):
        print(f"{i}. Query: \"{query}\"")
        
        try:
            # Tester la détection
            title = tool._detect_title_search(query)
            print(f"   → Titre détecté: {title}")
            
            # Tester la recherche complète
            results = tool._run(query, n_results=2, user_id=1)
            print(f"   → Résultats: {len(results)} livres trouvés")
            
            if results:
                first_result = results[0]
                print(f"   → Auteur trouvé: {first_result['authors']}")
                print(f"   → Méthode: {first_result['reason']}")
            else:
                print("   → ❌ Aucun résultat")
                
        except Exception as e:
            print(f"   → ❌ Erreur: {e}")
            
        print()

if __name__ == "__main__":
    test_author_questions()