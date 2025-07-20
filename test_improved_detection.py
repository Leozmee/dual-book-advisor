#!/usr/bin/env python3
"""
Test des améliorations de détection d'auteur
"""
import sys
import os

# Ajouter le projet au path
sys.path.insert(0, '/home/utilisateur/dual-book-advisor')

def test_improved_author_detection():
    """Test de la détection d'auteur améliorée"""
    print("=== Test détection d'auteur améliorée ===")
    
    from agents.langchain_agents.tools.rag_tools import LiteratureBookSearchTool
    
    lit_tool = LiteratureBookSearchTool()
    
    # Tester les cas problématiques
    test_cases = [
        "recommande moi des oeuvres de gustave flaubert",
        "livres de victor hugo",
        "oeuvres de gabriel garcia marquez", 
        "romans de stephen king",
        "gustave flaubert",  # Nom seul
        "alessandro baricco",  # Auteur moins connu
    ]
    
    for query in test_cases:
        print(f"\nTest: '{query}'")
        
        try:
            # Test détection d'auteur
            detected = lit_tool._detect_author_search(query)
            print(f"  Auteur détecté: {detected}")
            
            # Test extraction alternative
            potential = lit_tool._extract_potential_author_from_query(query)
            print(f"  Auteur potentiel: {potential}")
            
        except Exception as e:
            print(f"  Erreur: {e}")

def test_wikipedia_fallback():
    """Test du fallback Wikipedia"""
    print("\n=== Test fallback Wikipedia ===")
    
    from agents.langchain_agents.tools.rag_tools import LiteratureBookSearchTool
    
    lit_tool = LiteratureBookSearchTool()
    
    # Test avec un auteur connu
    author = "victor hugo"
    print(f"Test Wikipedia fallback pour: {author}")
    
    try:
        results = lit_tool._wikipedia_fallback_for_author(author, 3)
        print(f"Résultats Wikipedia: {len(results)}")
        
        for i, result in enumerate(results):
            book = result['book']
            print(f"  {i+1}. {book['title']} - {book['authors']}")
            print(f"     {book['description']}")
            
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    test_improved_author_detection()
    test_wikipedia_fallback()