#!/usr/bin/env python
"""
Script de configuration et d'initialisation des systèmes RAG
"""
import os
import sys
import django
from pathlib import Path

# Configuration Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

import logging
from django.conf import settings
from rags.tech_rag.tech_rag_manager import TechRAGManager
from rags.literature_rag.literature_rag_manager import LiteratureRAGManager

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_tech_rag(reset: bool = False):
    """Configure le système RAG pour les livres techniques"""
    logger.info("=== Configuration du RAG Technique ===")
    
    try:
        # Initialiser le gestionnaire RAG technique
        tech_rag = TechRAGManager()
        
        # Indexer tous les livres techniques
        logger.info("Indexation des livres techniques...")
        tech_rag.index_all_books(reset=reset)
        
        # Vérifier les statistiques
        stats = tech_rag.get_stats()
        logger.info(f"Statistiques RAG Technique: {stats}")
        
        # Test de recherche
        logger.info("Test de recherche...")
        test_results = tech_rag.search_books("python machine learning", n_results=3)
        logger.info(f"Test réussi: {len(test_results)} résultats trouvés")
        
        for i, result in enumerate(test_results, 1):
            logger.info(f"  {i}. {result['title']} - Score: {result['similarity_score']:.3f}")
        
        logger.info("✅ RAG Technique configuré avec succès")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la configuration du RAG Technique: {e}")
        return False


def setup_literature_rag(reset: bool = False):
    """Configure le système RAG pour les livres littéraires"""
    logger.info("=== Configuration du RAG Littéraire ===")
    
    try:
        # Initialiser le gestionnaire RAG littéraire
        literature_rag = LiteratureRAGManager()
        
        # Indexer tous les livres littéraires
        logger.info("Indexation des livres littéraires...")
        literature_rag.index_all_books(reset=reset)
        
        # Vérifier les statistiques
        stats = literature_rag.get_stats()
        logger.info(f"Statistiques RAG Littéraire: {stats}")
        
        # Test de recherche
        logger.info("Test de recherche...")
        test_results = literature_rag.search_books("romance historique", n_results=3)
        logger.info(f"Test réussi: {len(test_results)} résultats trouvés")
        
        for i, result in enumerate(test_results, 1):
            logger.info(f"  {i}. {result['title']} - Score: {result['similarity_score']:.3f}")
        
        logger.info("✅ RAG Littéraire configuré avec succès")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la configuration du RAG Littéraire: {e}")
        return False


def check_requirements():
    """Vérifie que les prérequis sont remplis"""
    logger.info("=== Vérification des prérequis ===")
    
    errors = []
    
    # Vérifier la base de données
    try:
        from apps.books.models import TechBook, LiteratureBook
        
        tech_count = TechBook.objects.count()
        literature_count = LiteratureBook.objects.count()
        
        logger.info(f"Livres techniques en base: {tech_count}")
        logger.info(f"Livres littéraires en base: {literature_count}")
        
        if tech_count == 0:
            errors.append("Aucun livre technique trouvé. Exécutez d'abord import_tech_books.py")
        
        if literature_count == 0:
            errors.append("Aucun livre littéraire trouvé. Exécutez d'abord import_literature_books.py")
            
    except Exception as e:
        errors.append(f"Erreur d'accès à la base de données: {e}")
    
    # Vérifier les répertoires ChromaDB
    tech_chroma_path = settings.RAG_CONFIG['tech_chroma_path']
    literature_chroma_path = settings.RAG_CONFIG['literature_chroma_path']
    
    logger.info(f"Répertoire ChromaDB technique: {tech_chroma_path}")
    logger.info(f"Répertoire ChromaDB littéraire: {literature_chroma_path}")
    
    # Créer les répertoires s'ils n'existent pas
    os.makedirs(tech_chroma_path, exist_ok=True)
    os.makedirs(literature_chroma_path, exist_ok=True)
    
    # Vérifier les dépendances
    try:
        import chromadb
        import sentence_transformers
        logger.info("✅ Dépendances ChromaDB et sentence-transformers installées")
    except ImportError as e:
        errors.append(f"Dépendances manquantes: {e}")
    
    if errors:
        logger.error("❌ Prérequis non remplis:")
        for error in errors:
            logger.error(f"  - {error}")
        return False
    
    logger.info("✅ Tous les prérequis sont remplis")
    return True


def main():
    """Fonction principale"""
    logger.info("🚀 Initialisation des systèmes RAG pour Dual Book Advisor")
    
    # Vérifier les arguments
    import argparse
    parser = argparse.ArgumentParser(description='Configuration des systèmes RAG')
    parser.add_argument('--reset', action='store_true', 
                       help='Réinitialiser les collections ChromaDB existantes')
    parser.add_argument('--tech-only', action='store_true',
                       help='Configurer uniquement le RAG technique')
    parser.add_argument('--literature-only', action='store_true',
                       help='Configurer uniquement le RAG littéraire')
    
    args = parser.parse_args()
    
    # Vérifier les prérequis
    if not check_requirements():
        logger.error("❌ Configuration impossible - prérequis non remplis")
        sys.exit(1)
    
    success = True
    
    # Configuration du RAG technique
    if not args.literature_only:
        if not setup_tech_rag(reset=args.reset):
            success = False
    
    # Configuration du RAG littéraire
    if not args.tech_only:
        if not setup_literature_rag(reset=args.reset):
            success = False
    
    # Résumé final
    if success:
        logger.info("🎉 Configuration RAG terminée avec succès!")
        logger.info("Les agents peuvent maintenant utiliser la recherche sémantique intelligente.")
        
        # Afficher les informations de configuration
        logger.info("\n=== Configuration RAG ===")
        logger.info(f"Modèle d'embedding: {settings.RAG_CONFIG['embedding_model']}")
        logger.info(f"Taille des chunks: {settings.RAG_CONFIG['chunk_size']}")
        logger.info(f"Seuil de similarité: {settings.RAG_CONFIG['similarity_threshold']}")
        logger.info(f"Top-K résultats: {settings.RAG_CONFIG['top_k_results']}")
        
    else:
        logger.error("❌ Configuration RAG échouée")
        sys.exit(1)


if __name__ == "__main__":
    main()