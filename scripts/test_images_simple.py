#!/usr/bin/env python3
"""
Script de test simple pour vérifier les images
"""
import os
import sys
import re
from pathlib import Path

# Setup Django
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

import django
django.setup()

from agents.cover_image_service import cover_service

def test_image_service():
    """Test direct du service d'images"""
    print("🧪 Test direct du service d'images")
    print("=" * 50)
    
    # Test quelques livres populaires
    tests = [
        ("Naruto", "", "manga"),
        ("Harry Potter", "J.K. Rowling", "book"),
        ("Python Programming", "Philip Robbins", "book"),
        ("One Piece", "", "manga"),
    ]
    
    for title, author, content_type in tests:
        print(f"\n🔍 Test: {title}")
        try:
            cover_url = cover_service.get_cover_image(title, author, content_type)
            if cover_url:
                print(f"✅ Image trouvée: {cover_url[:80]}...")
            else:
                print("❌ Aucune image trouvée")
        except Exception as e:
            print(f"❌ Erreur: {e}")

def test_image_extraction():
    """Test d'extraction d'images du format markdown"""
    print("\n\n🔍 Test d'extraction d'images")
    print("=" * 50)
    
    # Contenu d'exemple avec images
    sample_content = """🎌 **Recommandations Manga**

📸 ![Naruto](https://s4.anilist.co/file/anilistcdn/media/manga/cover/large/nx30011-9yUF1dXWgDOx.jpg)

1. 🎌 **Naruto** par Masashi Kishimoto
   ⭐ Note: 4.5/5 | 📅 Année: 1999
   📊 Pertinence: 95.2%

📸 ![One Piece](https://s4.anilist.co/file/anilistcdn/media/manga/cover/large/bx30013-BeslEMqiPhlk.jpg)

2. 🎌 **One Piece** par Eiichiro Oda
   ⭐ Note: 4.8/5 | 📅 Année: 1997
   📊 Pertinence: 92.1%"""
   
    # Regex pour extraire les images
    image_regex = r'📸\s*!\[([^\]]*)\]\(([^)]+)\)'
    matches = re.findall(image_regex, sample_content)
    
    print(f"📊 Images extraites: {len(matches)}")
    for i, (title, url) in enumerate(matches, 1):
        print(f"  {i}. {title}: {url[:60]}...")
    
    # Test de suppression des images
    content_without_images = re.sub(r'📸\s*!\[([^\]]*)\]\(([^)]+)\)\s*', '', sample_content)
    print(f"\n📝 Contenu sans images (premiers 200 caractères):")
    print(content_without_images[:200] + "...")

def test_health_check():
    """Test de santé des APIs"""
    print("\n\n🏥 Test de santé des APIs")
    print("=" * 50)
    
    try:
        health = cover_service.health_check()
        for service, status in health.items():
            status_icon = "✅" if status else "❌"
            print(f"{status_icon} {service}: {'Disponible' if status else 'Indisponible'}")
    except Exception as e:
        print(f"❌ Erreur lors du health check: {e}")

def main():
    print("🚀 Test simple des images")
    print("=" * 60)
    
    test_image_service()
    test_image_extraction()
    test_health_check()
    
    # Statistiques du cache
    print("\n📊 Statistiques du cache")
    print("=" * 30)
    try:
        cache_stats = cover_service.get_cache_stats()
        print(f"Images en cache: {cache_stats['cached_items']}")
        if cache_stats['cache_keys']:
            print("Exemples de clés:")
            for key in cache_stats['cache_keys'][:3]:
                print(f"  • {key}")
    except Exception as e:
        print(f"❌ Erreur cache: {e}")
    
    print("\n✅ Tests terminés!")

if __name__ == "__main__":
    main()