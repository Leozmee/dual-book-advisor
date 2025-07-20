#!/usr/bin/env python3
"""
Debug de la recherche littéraire pour comprendre les problèmes
"""
import sys
import os

# Ajouter le projet au path
sys.path.insert(0, '/home/utilisateur/dual-book-advisor')

def debug_literature_search():
    """Debug de la recherche littéraire avec des auteurs problématiques"""
    print("=== Debug recherche littéraire ===")
    
    from agents.langchain_agents.tools.rag_tools import LiteratureBookSearchTool
    
    lit_tool = LiteratureBookSearchTool()
    
    # Tester les auteurs problématiques
    test_cases = [
        "victor hugo",
        "gustave flaubert", 
        "stendhal",
        "œuvres de victor hugo",
        "livres de gustave flaubert"
    ]
    
    for query in test_cases:
        print(f"\n=== Test: '{query}' ===")
        
        try:
            # 1. Test détection d'auteur
            detected_author = lit_tool._detect_author_search(query)
            print(f"Auteur détecté: {detected_author}")
            
            # 2. Test recherche complète
            results = lit_tool._run(query, n_results=3, user_id=1)
            print(f"Nombre de résultats: {len(results)}")
            
            if results:
                print("Résultats:")
                for i, result in enumerate(results[:2]):  # Afficher 2 premiers
                    print(f"  {i+1}. {result.get('title', 'NO_TITLE')}")
                    print(f"     Auteur(s): {result.get('authors', 'NO_AUTHORS')}")
                    print(f"     Score: {result.get('similarity_score', 'NO_SCORE')}")
                    print(f"     Reason: {result.get('reason', 'NO_REASON')}")
            else:
                print("Aucun résultat trouvé")
                
        except Exception as e:
            print(f"Erreur: {e}")
            import traceback
            traceback.print_exc()

def debug_direct_db_search():
    """Debug recherche directe dans la base de données"""
    print("\n=== Debug recherche directe DB ===")
    
    try:
        from apps.books.models import LiteratureBook
        
        # Tester quelques recherches directes
        authors_to_test = ["victor hugo", "gustave flaubert", "hugo", "flaubert"]
        
        for author in authors_to_test:
            print(f"\n--- Recherche DB pour '{author}' ---")
            books = LiteratureBook.objects.filter(
                authors__icontains=author
            ).order_by('-average_rating')[:3]
            
            print(f"Livres trouvés: {books.count()}")
            for book in books:
                print(f"  - {book.title} par {book.authors}")
                
    except Exception as e:
        print(f"Erreur recherche DB: {e}")

if __name__ == "__main__":
    debug_literature_search()
    debug_direct_db_search()