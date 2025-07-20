#!/usr/bin/env python3
"""
Debug complet de la détection d'auteur pour "livres de victor hugo"
"""
import sys
import os

# Ajouter le projet au path
sys.path.insert(0, '/home/utilisateur/dual-book-advisor')

from agents.langchain_agents.tools.rag_tools import LiteratureBookSearchTool

def debug_full_detection():
    query = "livres de victor hugo"
    
    print(f"Debug complet pour: '{query}'")
    
    # Créer l'instance
    lit_tool = LiteratureBookSearchTool()
    
    # Tester la méthode _detect_author_search directement
    import re
    
    query_lower = query.lower().strip()
    print(f"Query lower: '{query_lower}'")
    
    # Les patterns exactement comme dans le code
    author_patterns = [
        r'\b(?:livres?|œuvres?|oeuvres?|romans?|books?)\s+de\s+([a-zA-ZÀ-ÿ]+\s+[a-zA-ZÀ-ÿ]+(?:\s+[a-zA-ZÀ-ÿ]+)*)\b',
        r'\b(?:œuvres?|oeuvres?|romans?|livres?|books?)\s+(?:de|d\'|par|by)\s+([a-zA-ZÀ-ÿ]+\s+[a-zA-ZÀ-ÿ]+(?:\s+[a-zA-ZÀ-ÿ]+)*)',
        r'recommande.*(?:œuvres?|oeuvres?|romans?|livres?).*(?:de|d\'|par|by)\s+([a-zA-ZÀ-ÿ]+\s+[a-zA-ZÀ-ÿ]+(?:\s+[a-zA-ZÀ-ÿ]+)*)',
        r'(?:donne|donnez)\s+(?:moi|nous)\s+(?:des|les)\s+(?:œuvres?|oeuvres?|romans?|livres?)\s+(?:de|d\'|par)\s+([a-zA-ZÀ-ÿ]+\s+[a-zA-ZÀ-ÿ]+(?:\s+[a-zA-ZÀ-ÿ]+)*)',
        r'(?:suggestions?|conseils?)\s+(?:de|d\'|par)\s+([a-zA-ZÀ-ÿ]+\s+[a-zA-ZÀ-ÿ]+(?:\s+[a-zA-ZÀ-ÿ]+)*)',
        r'auteur\s+([a-zA-ZÀ-ÿ]+\s+[a-zA-ZÀ-ÿ]+(?:\s+[a-zA-ZÀ-ÿ]+)*)',
        r'écrivain\s+([a-zA-ZÀ-ÿ]+\s+[a-zA-ZÀ-ÿ]+(?:\s+[a-zA-ZÀ-ÿ]+)*)',
        r'écrit\s+par\s+([a-zA-ZÀ-ÿ]+\s+[a-zA-ZÀ-ÿ]+(?:\s+[a-zA-ZÀ-ÿ]+)*)',
        r'written\s+by\s+([a-zA-ZÀ-ÿ]+\s+[a-zA-ZÀ-ÿ]+(?:\s+[a-zA-ZÀ-ÿ]+)*)',
        r'^([a-zA-ZÀ-ÿ]+\s+[a-zA-ZÀ-ÿ]+(?:\s+[a-zA-ZÀ-ÿ]+)*)\s*$',
        r'^([a-zA-ZÀ-ÿ]+\s+(?:de|du|van|von|da|di)\s+[a-zA-ZÀ-ÿ]+)\s*$',
    ]
    
    for i, pattern in enumerate(author_patterns):
        match = re.search(pattern, query_lower)
        if match:
            author_name = match.group(1).strip()
            print(f"Pattern {i+1} match: '{author_name}'")
            
            # Nettoyer et normaliser le nom (comme dans le code)
            author_name = re.sub(r'\s+', ' ', author_name)
            author_name = author_name.strip('.,!?;:()')
            print(f"  Après nettoyage: '{author_name}'")
            
            # Vérifier les conditions de validation
            print(f"  Longueur >= 4: {len(author_name) >= 4}")
            print(f"  Contient des lettres: {re.search(r'[a-zA-ZÀ-ÿ]', author_name) is not None}")
            
            # Exclure les phrases qui contiennent des mots-clés non-littéraires
            excluded_words = ['qui', 'a écrit', 'écrit', 'wrote', 'written', 'est', 'était', 'sera', 'what', 'comment', 'pourquoi', 'when', 'where', 'how', 'the', 'and', 'or']
            contains_excluded = any(word in author_name.lower() for word in excluded_words)
            print(f"  Contient mots exclus: {contains_excluded}")
            
            if not contains_excluded:
                # Validation supplémentaire
                has_space = ' ' in author_name
                is_known_single = author_name.lower() in ['shakespeare', 'molière', 'voltaire', 'racine', 'corneille', 'baudelaire', 'verlaine', 'rimbaud']
                is_long = len(author_name) >= 8
                
                print(f"  A un espace: {has_space}")
                print(f"  Est un nom connu unique: {is_known_single}")
                print(f"  Est long (>=8): {is_long}")
                
                if has_space or is_known_single or is_long:
                    print(f"  ✅ VALIDE: {author_name}")
                    break
                else:
                    print(f"  ❌ Non valide")
        else:
            print(f"Pattern {i+1}: no match")
    
    # Comparer avec la vraie méthode
    print(f"\nMéthode réelle: {lit_tool._detect_author_search(query)}")

if __name__ == "__main__":
    debug_full_detection()