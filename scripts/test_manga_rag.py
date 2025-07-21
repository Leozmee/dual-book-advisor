#!/usr/bin/env python3
"""
Script simple pour tester le RAG manga
"""
import os
import sys
import django
from pathlib import Path

# Configuration Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

django.setup()

from rags.manga_rag.manga_rag_manager import MangaRAGManager

def test_manga_search():
    """Test simple des recherches manga"""
    print("🎌 Test du RAG Manga")
    print("=" * 30)
    
    try:
        # Initialiser le manager
        manga_rag = MangaRAGManager()
        print("✅ Gestionnaire RAG manga initialisé")
        
        # Tests de recherche
        test_queries = [
            "naruto",
            "dragon ball", 
            "one piece",
            "attack on titan",
            "romance",
            "action",
            "shoujo"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Recherche: '{query}'")
            try:
                results = manga_rag.search_manga(query, n_results=5)
                if results:
                    print(f"   ✅ {len(results)} résultats trouvés")
                    for i, result in enumerate(results[:3]):
                        title = result.get('title', 'N/A')
                        score = result.get('similarity_score', 0)
                        print(f"   {i+1}. {title} (score: {score:.3f})")
                else:
                    print("   ❌ Aucun résultat")
            except Exception as e:
                print(f"   ❌ Erreur: {e}")
        
        print(f"\n🎉 Test terminé!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        return False

if __name__ == "__main__":
    test_manga_search()