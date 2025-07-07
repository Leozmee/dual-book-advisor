#!/usr/bin/env python3
"""
Script rapide pour indexer les mangas
"""
import os
import sys
import django
from pathlib import Path

# Configuration Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

def quick_index_manga():
    """Indexe rapidement les mangas"""
    print("🎌 Indexation rapide des mangas...")
    
    try:
        django.setup()
        
        from rags.manga_rag.manga_rag_manager import MangaRAGManager
        
        # Initialiser le gestionnaire RAG
        manga_rag = MangaRAGManager()
        
        # Charger les données
        manga_df = manga_rag.load_manga_data()
        print(f"📊 {len(manga_df)} mangas chargés")
        
        if len(manga_df) == 0:
            print("❌ Aucun manga trouvé dans le CSV")
            return False
        
        # Indexer (sans reset pour aller plus vite)
        print("🔄 Indexation en cours...")
        manga_rag.index_all_manga(reset=True)
        
        # Test de recherche
        print("🔍 Test Naruto...")
        results = manga_rag.search_manga("naruto", n_results=3)
        print(f"✅ {len(results)} résultats trouvés pour Naruto")
        
        for result in results[:2]:
            print(f"   - {result['title']} (score: {result['similarity_score']:.2f})")
        
        # Test de recherche One Piece
        print("🔍 Test One Piece...")
        results = manga_rag.search_manga("one piece", n_results=2)
        print(f"✅ {len(results)} résultats trouvés pour One Piece")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = quick_index_manga()
    sys.exit(0 if success else 1)