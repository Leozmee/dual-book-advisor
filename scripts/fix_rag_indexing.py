#!/usr/bin/env python3
"""
Script pour forcer la réindexation du RAG littéraire
Le problème : les livres existent en base mais ne sont pas trouvés par le RAG
"""
import os
import sys
import django
from pathlib import Path

# Configuration Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.books.models import LiteratureBook
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def force_reindex_literature():
    """Force la réindexation complète du RAG littéraire"""
    print("🔧 Force la réindexation du RAG littéraire...")
    
    try:
        from rags.literature_rag.literature_rag_manager import LiteratureRAGManager
        
        # Créer le gestionnaire RAG
        lit_rag = LiteratureRAGManager()
        
        # FORCER la réindexation complète
        print("📋 Suppression de l'ancienne indexation...")
        lit_rag.index_all_books(reset=True)  # Reset = True pour tout recréer
        
        print("✅ Réindexation terminée")
        
        # Test immédiat
        print("\n🧪 Test après réindexation...")
        test_queries = [
            "Harry Potter",
            "fantasy",
            "magic",
            "J.K. Rowling",
            "Tolkien",
            "Lord of the Rings"
        ]
        
        for query in test_queries:
            results = lit_rag.search_books(query, n_results=3)
            print(f"   '{query}' → {len(results)} résultats")
            
            for i, result in enumerate(results, 1):
                title = result.get('title', 'Titre inconnu')
                score = result.get('similarity_score', 0)
                print(f"      {i}. {title} (score: {score:.3f})")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la réindexation: {e}")
        return False

def verify_database_content():
    """Vérifie le contenu exact de quelques livres importants"""
    print("\n🔍 Vérification du contenu de la base...")
    
    # Vérifier Harry Potter
    hp_book = LiteratureBook.objects.filter(title__icontains="Harry Potter").first()
    if hp_book:
        print(f"📚 Premier livre HP trouvé:")
        print(f"   Titre: {hp_book.title}")
        print(f"   Auteur: {hp_book.authors}")
        print(f"   Catégories: {hp_book.categories}")
        print(f"   Description: {hp_book.description[:100]}...")
        print(f"   Note: {hp_book.average_rating}")
    
    # Vérifier Tolkien
    tolkien_book = LiteratureBook.objects.filter(authors__icontains="Tolkien").first()
    if tolkien_book:
        print(f"\n📚 Livre Tolkien trouvé:")
        print(f"   Titre: {tolkien_book.title}")
        print(f"   Auteur: {tolkien_book.authors}")
        print(f"   Catégories: {tolkien_book.categories}")
        print(f"   Description: {tolkien_book.description[:100]}...")

def test_specific_books():
    """Test la recherche de livres spécifiques après réindexation"""
    print("\n🎯 Test de livres spécifiques...")
    
    try:
        from rags.literature_rag.literature_rag_manager import LiteratureRAGManager
        lit_rag = LiteratureRAGManager()
        
        # Test avec des titres exacts
        exact_tests = [
            "Harry Potter and the Sorcerer's Stone",
            "The Lord of the Rings",
            "The Fellowship of the Ring",
        ]
        
        for title in exact_tests:
            print(f"\n🔍 Test titre exact: '{title}'")
            results = lit_rag.search_books(title, n_results=3)
            
            if results:
                best_result = results[0]
                print(f"   ✅ Trouvé: {best_result.get('title')} (score: {best_result.get('similarity_score', 0):.3f})")
            else:
                print(f"   ❌ Aucun résultat")
                
                # Test fallback : recherche en base directe
                db_book = LiteratureBook.objects.filter(title__icontains=title.split()[0]).first()
                if db_book:
                    print(f"   📋 Livre existe en base: {db_book.title}")
                    
    except Exception as e:
        print(f"❌ Erreur test spécifique: {e}")

def check_chromadb_status():
    """Vérifie l'état de ChromaDB"""
    print("\n🗄️ Vérification ChromaDB...")
    
    try:
        from rags.literature_rag.literature_rag_manager import LiteratureRAGManager
        lit_rag = LiteratureRAGManager()
        
        stats = lit_rag.get_stats()
        print(f"📊 Statistiques ChromaDB:")
        print(f"   Collection: {stats.get('collection_name')}")
        print(f"   Livres indexés: {stats.get('indexed_books')}")
        print(f"   Livres en base: {stats.get('total_books_in_db')}")
        print(f"   Statut sync: {stats.get('sync_status')}")
        
        return stats
        
    except Exception as e:
        print(f"❌ Erreur ChromaDB: {e}")
        return None

def main():
    """Fonction principale de correction"""
    print("🚀 Correction de l'indexation RAG Littéraire")
    print("=" * 60)
    
    # 1. Vérifier le contenu de la base
    verify_database_content()
    
    # 2. Vérifier l'état de ChromaDB
    initial_stats = check_chromadb_status()
    
    # 3. Forcer la réindexation
    if force_reindex_literature():
        print("\n✅ Réindexation réussie !")
        
        # 4. Vérifier après réindexation
        final_stats = check_chromadb_status()
        
        # 5. Test de livres spécifiques
        test_specific_books()
        
        print("\n🎉 Correction terminée !")
        print("💡 Testez maintenant avec : python test_agents.py")
        
    else:
        print("\n❌ Réindexation échouée")
        print("💡 Essayez de supprimer manuellement le dossier rags/literature_rag/chroma_db/")

if __name__ == "__main__":
    main()