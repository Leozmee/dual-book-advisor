"""
Module d'expansion de requêtes pour améliorer la recherche RAG
"""
import re
from typing import Dict, List
from django.conf import settings

def expand_query(query: str) -> str:
    """Enrichit une requête pour améliorer la recherche sémantique"""
    query_lower = query.lower()
    expanded_parts = [query]
    
    # Utiliser le dictionnaire de traduction des settings
    translations = getattr(settings, 'QUERY_TRANSLATIONS', {})
    
    for key, expansion in translations.items():
        if key.lower() in query_lower:
            expanded_parts.append(expansion)
            break  # Prendre la première correspondance principale
    
    # Ajout de synonymes contextuels
    if any(word in query_lower for word in ['livre', 'book', 'ouvrage']):
        expanded_parts.append('book literature reading')
    
    if any(word in query_lower for word in ['recommandation', 'suggestion', 'conseil']):
        expanded_parts.append('recommendation suggest similar')
    
    if any(word in query_lower for word in ['apprendre', 'learn', 'étudier']):
        expanded_parts.append('learn study tutorial beginner guide')
    
    return ' '.join(expanded_parts)

def detect_language(query: str) -> str:
    """Détecte la langue d'une requête"""
    french_indicators = ['de', 'le', 'la', 'les', 'du', 'des', 'un', 'une', 'oeuvres', 'livres', 'apprendre']
    english_indicators = ['the', 'and', 'or', 'to', 'for', 'with', 'books', 'learn', 'programming']
    
    query_lower = query.lower()
    french_count = sum(1 for word in french_indicators if word in query_lower)
    english_count = sum(1 for word in english_indicators if word in query_lower)
    
    return 'french' if french_count > english_count else 'english'

def normalize_author_query(query: str) -> str:
    """Normalise les requêtes d'auteurs pour améliorer la correspondance"""
    # Variations courantes d'auteurs
    author_variations = {
        'tolstoy': ['tolstoi', 'tolstoï', 'leo tolstoy', 'leon tolstoi'],
        'stephen king': ['king', 's. king', 'stephen edwin king'],
        'murakami': ['haruki murakami', 'h. murakami'],
        'victor hugo': ['hugo', 'v. hugo'],
        'shakespeare': ['william shakespeare', 'w. shakespeare'],
    }
    
    query_lower = query.lower()
    for standard, variations in author_variations.items():
        for variation in variations:
            if variation in query_lower:
                return query_lower.replace(variation, standard)
    
    return query
