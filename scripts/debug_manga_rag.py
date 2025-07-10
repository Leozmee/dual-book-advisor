#!/usr/bin/env python3
"""
Debug du RAG manga et des données disponibles
"""
import os
import sys
import django

# Ajouter le répertoire du projet au path
sys.path.insert(0, '/home/utilisateur/dual-book-advisor')

# Configurer Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from agents.ollama_gemma_manager import GemmaAgentManager

def debug_manga_rag():
    print("=== DEBUG MANGA RAG ===")
    
    manager = GemmaAgentManager()
    
    # Vérifier l'état du manga RAG
    print(f"Manga RAG initialisé: {manager.manga_rag is not None}")
    
    if manager.manga_rag:
        print("✅ Manga RAG disponible")
        
        # Test de recherche
        test_queries = ["Naruto", "One Piece", "manga", "shounen"]
        
        for query in test_queries:
            print(f"\n--- Test query: '{query}' ---")
            try:
                results = manager.manga_rag.search_content(query, n_results=3)
                print(f"Résultats trouvés: {len(results)}")
                
                for i, result in enumerate(results):
                    print(f"  {i+1}. {result.get('title', 'N/A')} - {result.get('author', 'N/A')}")
                    
            except Exception as e:
                print(f"❌ Erreur recherche '{query}': {e}")
    else:
        print("❌ Manga RAG non disponible - Test du fallback")
        
        # Test du fallback
        try:
            fallback_results = manager._search_manga_comics_fallback("Naruto")
            print(f"Fallback résultats: {len(fallback_results)}")
            for result in fallback_results:
                print(f"  - {result.get('title', 'N/A')}")
        except Exception as e:
            print(f"❌ Erreur fallback: {e}")

def test_manga_request():
    print("\n=== TEST REQUÊTE MANGA COMPLÈTE ===")
    
    manager = GemmaAgentManager()
    
    # Test avec des requêtes variées
    queries = [
        "Recommande-moi des mangas comme Naruto",
        "Je cherche des shounen populaires",
        "Quels sont les meilleurs mangas d'action ?",
        "manga"
    ]
    
    for query in queries:
        print(f"\n--- Requête: '{query}' ---")
        
        response = manager.get_manga_recommendations(query)
        print(f"Réponse (taille): {len(response)}")
        
        # Vérifier si des images sont présentes
        import re
        image_matches = re.findall(r'📸\s*!\[([^\]]*)\]\(([^)]+)\)', response)
        print(f"Images trouvées: {len(image_matches)}")
        
        # Afficher le début de la réponse
        print(f"Début: {response[:200]}...")
        
        if "Aucun manga/comics trouvé" in response:
            print("⚠️ Aucun contenu trouvé - problème de données")

if __name__ == "__main__":
    debug_manga_rag()
    test_manga_request()