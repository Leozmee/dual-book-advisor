#!/usr/bin/env python3
"""
Debug des mots exclus pour "victor hugo"
"""

def debug_excluded():
    author_name = "victor hugo"
    excluded_words = ['qui', 'a écrit', 'écrit', 'wrote', 'written', 'est', 'était', 'sera', 'what', 'comment', 'pourquoi', 'when', 'where', 'how', 'the', 'and', 'or']
    
    print(f"Nom d'auteur: '{author_name}'")
    print("Vérification des mots exclus:")
    
    for word in excluded_words:
        if word in author_name.lower():
            print(f"  ❌ '{word}' trouvé dans '{author_name}'")
        else:
            print(f"  ✅ '{word}' NOT in '{author_name}'")
    
    contains_excluded = any(word in author_name.lower() for word in excluded_words)
    print(f"\nContient mots exclus: {contains_excluded}")

if __name__ == "__main__":
    debug_excluded()