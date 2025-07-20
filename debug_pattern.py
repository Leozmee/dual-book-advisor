#!/usr/bin/env python3
"""
Debug spécifique du pattern "livres de victor hugo"
"""
import re

def test_pattern():
    query = "livres de victor hugo"
    query_lower = query.lower().strip()
    
    print(f"Testing: '{query_lower}'")
    
    # Test du pattern spécifique
    pattern = r'\b(?:livres?|œuvres?|oeuvres?|romans?|books?)\s+de\s+([a-zA-ZÀ-ÿ]+\s+[a-zA-ZÀ-ÿ]+(?:\s+[a-zA-ZÀ-ÿ]+)*)\b'
    
    print(f"Pattern: {pattern}")
    
    match = re.search(pattern, query_lower)
    if match:
        print(f"Match trouvé: '{match.group(1)}'")
        print(f"Groupes: {match.groups()}")
    else:
        print("Aucun match")
    
    # Test sans \b
    pattern2 = r'(?:livres?|œuvres?|oeuvres?|romans?|books?)\s+de\s+([a-zA-ZÀ-ÿ]+\s+[a-zA-ZÀ-ÿ]+(?:\s+[a-zA-ZÀ-ÿ]+)*)'
    print(f"\nPattern sans \\b: {pattern2}")
    
    match2 = re.search(pattern2, query_lower)
    if match2:
        print(f"Match trouvé: '{match2.group(1)}'")
    else:
        print("Aucun match")
    
    # Test avec tous les patterns
    author_patterns = [
        r'\b(?:livres?|œuvres?|oeuvres?|romans?|books?)\s+de\s+([a-zA-ZÀ-ÿ]+\s+[a-zA-ZÀ-ÿ]+(?:\s+[a-zA-ZÀ-ÿ]+)*)\b',
        r'\b(?:œuvres?|oeuvres?|romans?|livres?|books?)\s+(?:de|d\'|par|by)\s+([a-zA-ZÀ-ÿ]+\s+[a-zA-ZÀ-ÿ]+(?:\s+[a-zA-ZÀ-ÿ]+)*)',
        r'recommande.*(?:œuvres?|oeuvres?|romans?|livres?).*(?:de|d\'|par|by)\s+([a-zA-ZÀ-ÿ]+\s+[a-zA-ZÀ-ÿ]+(?:\s+[a-zA-ZÀ-ÿ]+)*)',
    ]
    
    print("\nTest avec tous les patterns:")
    for i, pattern in enumerate(author_patterns):
        match = re.search(pattern, query_lower)
        if match:
            print(f"Pattern {i+1} match: '{match.group(1)}'")
        else:
            print(f"Pattern {i+1}: no match")

if __name__ == "__main__":
    test_pattern()