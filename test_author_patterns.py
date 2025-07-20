#!/usr/bin/env python3
"""
Test des patterns de détection d'auteurs inconnus
"""
import sys
import os

# Ajouter le projet au path
sys.path.insert(0, '/home/utilisateur/dual-book-advisor')

from agents.langchain_agents.nodes.classifier_node import ClassifierNode

def test_author_patterns():
    """Test la détection de patterns avec auteurs inconnus"""
    print("=== Test patterns auteurs inconnus ===")
    
    # Créer une instance partielle du classifier
    classifier = ClassifierNode.__new__(ClassifierNode)
    
    # Ajouter les attributs nécessaires
    classifier.known_authors = ['victor hugo', 'shakespeare', 'joël dicker']  # Liste réduite
    classifier.tech_keywords = ['ai', 'web', 'app', 'code', 'python', 'java']
    classifier.literature_keywords = ['roman', 'livre', 'auteur', 'littérature']
    
    # Test des patterns de noms d'auteurs
    test_cases = [
        "recommande moi des oeuvres de jean paul martin",
        "livres de marie dupuis", 
        "romans de carlos mendoza",
        "jean pierre alexandre",  # Nom seul
        "alessandro ferretti ai",  # Nom + mot-clé technique
        "qui a écrit ce livre",  # Question sans nom
    ]
    
    for query in test_cases:
        query_lower = query.lower()
        print(f"Query: '{query}'")
        
        try:
            # Test détection pattern d'auteur
            detected_author = classifier._detect_author_name_pattern(query_lower)
            print(f"  -> Pattern auteur détecté: {detected_author}")
            
            # Test si c'est une requête littéraire
            is_lit = classifier._is_likely_literature_query(query_lower)
            print(f"  -> Is literature query: {is_lit}")
            
        except Exception as e:
            print(f"  -> Erreur: {e}")
        
        print()

if __name__ == "__main__":
    test_author_patterns()