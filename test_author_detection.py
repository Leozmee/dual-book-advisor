#!/usr/bin/env python3
"""
Test de la détection d'auteur dans LiteratureBookSearchTool
"""
import sys
import os

# Ajouter le projet au path
sys.path.insert(0, '/home/utilisateur/dual-book-advisor')

# Import du RAG tool
from agents.langchain_agents.tools.rag_tools import LiteratureBookSearchTool

def test_author_detection():
    """Test de la méthode _detect_author_search"""
    print("=== Test de détection d'auteur ===")
    
    # Créer une instance du tool
    lit_tool = LiteratureBookSearchTool()
    
    # Tester la détection d'auteur avec plusieurs requêtes
    test_queries = [
        "recommande moi des oeuvres de joël dicker",
        "livres de victor hugo", 
        "oeuvres de gabriel garcia marquez",
        "romans de stephen king",
        "joël dicker",
        "donne moi des livres de elena ferrante",
        "œuvres de marguerite duras",
        "qui a écrit l'étranger"
    ]
    
    for query in test_queries:
        try:
            detected_author = lit_tool._detect_author_search(query)
            print(f"Query: '{query}'")
            print(f"  -> Auteur détecté: {detected_author}")
            print()
        except Exception as e:
            print(f"Erreur pour '{query}': {e}")
            print()

def test_title_detection():
    """Test de la méthode _detect_title_search"""
    print("=== Test de détection de titre ===")
    
    # Créer une instance du tool
    lit_tool = LiteratureBookSearchTool()
    
    # Tester la détection de titre
    title_queries = [
        "qui a écrit madame bovary",
        "auteur de l'étranger",
        "qui a écrit les misérables"
    ]
    
    for query in title_queries:
        try:
            detected_title = lit_tool._detect_title_search(query)
            print(f"Query: '{query}'")
            print(f"  -> Titre détecté: {detected_title}")
            print()
        except Exception as e:
            print(f"Erreur pour '{query}': {e}")
            print()

if __name__ == "__main__":
    test_author_detection()
    test_title_detection()