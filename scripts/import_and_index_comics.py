#!/usr/bin/env python3
"""
Script d'import et d'indexation des comics/BD
Fichier: scripts/import_and_index_comics.py
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

import logging
import time
from rags.manga_rag.manga_rag_manager import MangaRAGManager

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Fonction principale d'import et d'indexation"""
    print("🚀 Démarrage de l'import et indexation comics/mangas")
    print("=" * 60)
    
    try:
        # Initialiser le gestionnaire RAG unifié
        print("📂 Initialisation du gestionnaire RAG...")
        rag_manager = MangaRAGManager()
        
        # Vérifier les fichiers sources
        print("\n🔍 Vérification des fichiers sources...")
        
        manga_exists = rag_manager.manga_data_path.exists()
        comics_exists = rag_manager.comics_data_path.exists()
        
        print(f"   📊 Mangas japonais: {'✅ Trouvé' if manga_exists else '❌ Non trouvé'} ({rag_manager.manga_data_path})")
        print(f"   📊 Comics/BD: {'✅ Trouvé' if comics_exists else '❌ Non trouvé'} ({rag_manager.comics_data_path})")
        
        if not manga_exists and not comics_exists:
            print("\n❌ Aucun fichier source trouvé. Arrêt du script.")
            return
        
        # Charger et analyser les données
        print("\n📈 Chargement des données...")
        start_time = time.time()
        
        manga_df = rag_manager.load_manga_data()
        comics_df = rag_manager.load_comics_data()
        all_data = rag_manager.load_all_data()
        
        load_time = time.time() - start_time
        
        print(f"   📊 Mangas chargés: {len(manga_df)}")
        print(f"   📊 Comics chargés: {len(comics_df)}")
        print(f"   📊 Total combiné: {len(all_data)}")
        print(f"   ⏱️ Temps de chargement: {load_time:.2f}s")
        
        if all_data.empty:
            print("\n❌ Aucune donnée à indexer. Arrêt du script.")
            return
        
        # Afficher un aperçu des données comics
        if not comics_df.empty:
            print("\n📋 Aperçu des comics/BD:")
            sample_comics = comics_df.head(3)
            for idx, row in sample_comics.iterrows():
                print(f"   • {row.get('title', 'N/A')} - {row.get('author', 'N/A')} ({row.get('rating', 0)}/5)")
        
        # Demander confirmation pour l'indexation
        print(f"\n🤖 Prêt à indexer {len(all_data)} entrées dans ChromaDB")
        confirm = input("Continuer ? (o/N): ").lower().strip()
        
        if confirm not in ['o', 'oui', 'y', 'yes']:
            print("❌ Indexation annulée par l'utilisateur.")
            return
        
        # Indexation
        print("\n🔄 Indexation en cours...")
        print("   ⚠️ Cette opération peut prendre plusieurs minutes...")
        
        index_start = time.time()
        rag_manager.index_all_content(reset=True)
        index_time = time.time() - index_start
        
        print(f"   ✅ Indexation terminée en {index_time:.2f}s")
        
        # Vérification et tests
        print("\n🧪 Tests de vérification...")
        
        # Test de recherche manga
        if not manga_df.empty:
            manga_results = rag_manager.search_content("naruto", n_results=2, content_type='manga')
            print(f"   🎌 Test manga ('naruto'): {len(manga_results)} résultats")
            if manga_results:
                print(f"      └─ {manga_results[0]['title']} (score: {manga_results[0]['similarity_score']:.2f})")
        
        # Test de recherche comics
        if not comics_df.empty:
            comics_results = rag_manager.search_content("superman", n_results=2, content_type='comics')
            print(f"   🦸 Test comics ('superman'): {len(comics_results)} résultats")
            if comics_results:
                print(f"      └─ {comics_results[0]['title']} (score: {comics_results[0]['similarity_score']:.2f})")
        
        # Test de recherche générale
        general_results = rag_manager.search_content("aventure", n_results=3, content_type='all')
        print(f"   🔍 Test général ('aventure'): {len(general_results)} résultats")
        if general_results:
            for i, result in enumerate(general_results[:2], 1):
                source_type = "🎌" if result['source_type'] == 'manga_japonais' else "🦸"
                print(f"      {i}. {source_type} {result['title']} (score: {result['similarity_score']:.2f})")
        
        # Statistiques finales
        print("\n📊 Statistiques finales:")
        stats = rag_manager.get_stats()
        print(f"   📚 Collection: {stats['collection_name']}")
        print(f"   🎌 Mangas indexés: {stats['manga_in_csv']}")
        print(f"   🦸 Comics indexés: {stats['comics_in_csv']}")
        print(f"   📊 Total indexé: {stats['indexed_total']}")
        print(f"   🔄 Statut sync: {stats['sync_status']}")
        
        # Health check
        print("\n🏥 Vérification de santé du système...")
        health = rag_manager.health_check()
        print(f"   🟢 Statut: {health['status']}")
        print(f"   📂 Collection accessible: {health['collection_accessible']}")
        print(f"   🎌 Tests manga: {health['manga_test_results']} résultats")
        print(f"   🦸 Tests comics: {health['comics_test_results']} résultats")
        
        total_time = time.time() - start_time
        print(f"\n🎉 Import terminé avec succès en {total_time:.2f}s")
        print("=" * 60)
        
        # Instructions pour l'utilisation
        print("\n💡 Instructions d'utilisation:")
        print("   1. L'agent manga peut maintenant recommander mangas ET comics")
        print("   2. Exemples de requêtes:")
        print("      • 'manga comme naruto' → mangas japonais")
        print("      • 'comics superman' → comics/BD")
        print("      • 'bd aventure' → comics/BD d'aventure")
        print("      • 'histoire d'action' → mangas + comics d'action")
        print("   3. Le système détecte automatiquement le type de contenu souhaité")
        
    except Exception as e:
        logger.error(f"Erreur lors de l'import: {e}")
        print(f"\n❌ Erreur: {e}")
        return 1
    
    return 0


def test_search_functionality():
    """Fonction de test avancée pour vérifier les fonctionnalités"""
    print("\n🧪 Tests avancés...")
    
    try:
        rag_manager = MangaRAGManager()
        
        test_queries = [
            ("naruto", "manga"),
            ("superman", "comics"),
            ("aventure", "all"),
            ("humour", "all"),
            ("action", "all")
        ]
        
        for query, content_type in test_queries:
            results = rag_manager.search_content(query, n_results=2, content_type=content_type)
            print(f"   🔍 '{query}' ({content_type}): {len(results)} résultats")
            
            for result in results[:1]:  # Afficher le premier résultat
                source_icon = "🎌" if result['source_type'] == 'manga_japonais' else "🦸"
                print(f"      └─ {source_icon} {result['title']} ({result['similarity_score']:.2f})")
    
    except Exception as e:
        print(f"❌ Erreur lors des tests: {e}")


if __name__ == "__main__":
    try:
        exit_code = main()
        
        # Tests supplémentaires si demandé
        if exit_code == 0:
            test_advanced = input("\nExecuter les tests avancés ? (o/N): ").lower().strip()
            if test_advanced in ['o', 'oui', 'y', 'yes']:
                test_search_functionality()
        
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n❌ Arrêt demandé par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        sys.exit(1)