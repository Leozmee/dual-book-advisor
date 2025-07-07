#!/usr/bin/env python3
"""
Script pour réindexer complètement le RAG littéraire
"""
import os
import sys
import django
from pathlib import Path

# Configuration Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

def reindex_literature_rag():
    """Réindexe complètement le RAG littéraire"""
    print("🚀 Démarrage de la réindexation complète du RAG littéraire...")
    
    try:
        django.setup()
        
        from rags.literature_rag.literature_rag_manager import LiteratureRAGManager
        from apps.books.models import LiteratureBook
        
        # Statistiques initiales
        total_books = LiteratureBook.objects.count()
        print(f"📊 Total de livres en base: {total_books}")
        
        # Initialiser le gestionnaire RAG
        print("🔧 Initialisation du gestionnaire RAG...")
        rag_manager = LiteratureRAGManager()
        
        # Supprimer et recréer la collection
        print("🗑️ Suppression de l'ancienne collection...")
        rag_manager.collection = rag_manager.chroma_manager.create_collection(
            rag_manager.collection_name, 
            reset=True
        )
        print("✅ Collection réinitialisée")
        
        # Réindexer tous les livres
        print("📚 Indexation de tous les livres...")
        rag_manager.index_all_books()
        
        # Statistiques finales
        stats = rag_manager.get_stats()
        print(f"📈 Statistiques finales:")
        print(f"   - Livres indexés: {stats.get('indexed_books', 0)}")
        print(f"   - Total en base: {stats.get('total_books_in_db', 0)}")
        print(f"   - Statut: {stats.get('sync_status', 'unknown')}")
        
        if stats.get('sync_status') == 'synchronized':
            print("🎉 Réindexation terminée avec succès!")
            return True
        else:
            print("⚠️ Réindexation incomplète")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la réindexation: {e}")
        return False

if __name__ == "__main__":
    success = reindex_literature_rag()
    sys.exit(0 if success else 1)