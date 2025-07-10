#!/usr/bin/env python3
"""
Script de test pour l'intégration des images de couverture
Fichier: scripts/test_cover_images.py
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
from agents.simple_agents import SimpleAgentManager
from agents.cover_image_service import cover_service

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_cover_service_apis():
    """Test des différentes APIs du service d'images"""
    print("🧪 Test des APIs du service d'images")
    print("=" * 50)
    
    # Test 1: Agent Manga - doit utiliser AniList
    print("\n🎌 Test Agent Manga (AniList prioritaire)")
    manga_tests = [
        ("Naruto", "", "manga"),
        ("One Piece", "", "manga"),
        ("Dragon Ball", "", "manga")
    ]
    
    for title, author, content_type in manga_tests:
        print(f"\n🔍 Test: {title}")
        cover_url = cover_service.get_cover_image(title, author, content_type)
        if cover_url:
            print(f"✅ Image trouvée: {cover_url[:80]}...")
        else:
            print("❌ Aucune image trouvée")
    
    # Test 2: Agent Littérature - doit utiliser Google Books + Open Library
    print("\n\n📚 Test Agent Littérature (Google Books + Open Library)")
    literature_tests = [
        ("Harry Potter", "J.K. Rowling", "book"),
        ("1984", "George Orwell", "book"),
        ("Pride and Prejudice", "Jane Austen", "book")
    ]
    
    for title, author, content_type in literature_tests:
        print(f"\n🔍 Test: {title} par {author}")
        cover_url = cover_service.get_cover_image(title, author, content_type)
        if cover_url:
            print(f"✅ Image trouvée: {cover_url[:80]}...")
        else:
            print("❌ Aucune image trouvée")
    
    # Test 3: Health check des services
    print("\n\n🏥 Health Check des APIs")
    health = cover_service.health_check()
    for service, status in health.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {service}: {'Disponible' if status else 'Indisponible'}")


def test_agents_with_images():
    """Test des agents avec images intégrées"""
    print("\n\n🤖 Test des agents avec images")
    print("=" * 50)
    
    # Initialiser le gestionnaire d'agents
    agent_manager = SimpleAgentManager(use_gemma=False, use_cover_images=True)
    
    # Test 1: Agent Manga
    print("\n🎌 Test Agent Manga")
    manga_query = "manga comme naruto"
    response = agent_manager.get_manga_recommendations(manga_query)
    print("Réponse agent manga:")
    print(response[:500] + "..." if len(response) > 500 else response)
    
    # Vérifier la présence d'images
    if "![" in response and "](" in response:
        print("✅ Images détectées dans la réponse manga")
    else:
        print("❌ Aucune image détectée dans la réponse manga")
    
    # Test 2: Agent Littérature
    print("\n\n📚 Test Agent Littérature")
    lit_query = "livres comme Harry Potter"
    response = agent_manager.get_literature_recommendations(lit_query)
    print("Réponse agent littérature:")
    print(response[:500] + "..." if len(response) > 500 else response)
    
    # Vérifier la présence d'images
    if "![" in response and "](" in response:
        print("✅ Images détectées dans la réponse littérature")
    else:
        print("❌ Aucune image détectée dans la réponse littérature")
    
    # Test 3: Agent Technique
    print("\n\n🔧 Test Agent Technique")
    tech_query = "livres Python débutant"
    response = agent_manager.get_tech_recommendations(tech_query)
    print("Réponse agent technique:")
    print(response[:500] + "..." if len(response) > 500 else response)
    
    # Vérifier la présence d'images
    if "![" in response and "](" in response:
        print("✅ Images détectées dans la réponse technique")
    else:
        print("❌ Aucune image détectée dans la réponse technique")


def test_routing_with_images():
    """Test du routage avec images"""
    print("\n\n🧭 Test du routage avec images")
    print("=" * 50)
    
    agent_manager = SimpleAgentManager(use_gemma=False, use_cover_images=True)
    
    test_queries = [
        ("recommande moi des mangas action", "manga"),
        ("livres de Victor Hugo", "littérature"),
        ("apprendre JavaScript", "technique"),
        ("comics superman", "manga/comics")
    ]
    
    for query, expected_agent in test_queries:
        print(f"\n🔍 Test: '{query}' (attendu: {expected_agent})")
        response = agent_manager.route_query(query)
        
        # Vérifier la présence d'images
        if "![" in response and "](" in response:
            print("✅ Images détectées dans la réponse routée")
        else:
            print("❌ Aucune image détectée dans la réponse routée")
        
        # Afficher le début de la réponse
        print(f"Réponse (début): {response[:200]}...")


def main():
    """Fonction principale de test"""
    print("🚀 Test d'intégration des images de couverture")
    print("=" * 60)
    
    try:
        # Test 1: APIs de base
        test_cover_service_apis()
        
        # Test 2: Agents avec images
        test_agents_with_images()
        
        # Test 3: Routage avec images
        test_routing_with_images()
        
        # Statistiques du cache
        print("\n\n📊 Statistiques du cache")
        print("=" * 30)
        cache_stats = cover_service.get_cache_stats()
        print(f"Images en cache: {cache_stats['cached_items']}")
        if cache_stats['cache_keys']:
            print("Exemples de clés:")
            for key in cache_stats['cache_keys'][:5]:
                print(f"  • {key}")
        
        print("\n✅ Tests terminés avec succès!")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors des tests: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)