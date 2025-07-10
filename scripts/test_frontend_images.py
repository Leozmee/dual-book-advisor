#!/usr/bin/env python3
"""
Script de test pour vérifier l'intégration frontend des images
Fichier: scripts/test_frontend_images.py
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

import json
from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()


def test_api_responses():
    """Test que les APIs retournent des images dans le bon format"""
    print("🧪 Test des réponses API avec images")
    print("=" * 50)
    
    # Configurer ALLOWED_HOSTS pour les tests
    from django.conf import settings
    original_allowed_hosts = settings.ALLOWED_HOSTS
    settings.ALLOWED_HOSTS = ['testserver'] + settings.ALLOWED_HOSTS
    
    client = Client()
    
    # Créer un utilisateur test si nécessaire
    user, created = User.objects.get_or_create(
        username='testuser', 
        defaults={'email': 'test@example.com'}
    )
    if created:
        user.set_password('testpass')
        user.save()
    
    # Se connecter
    client.login(username='testuser', password='testpass')
    
    # Tests des différents agents
    test_cases = [
        {
            'name': 'Agent Manga',
            'url': '/api/chat/manga-agent/',
            'message': 'manga comme naruto',
            'expected_images': True
        },
        {
            'name': 'Agent Littérature', 
            'url': '/api/chat/literature-agent/',
            'message': 'livres comme Harry Potter',
            'expected_images': True
        },
        {
            'name': 'Agent Technique',
            'url': '/api/chat/tech-agent/',
            'message': 'livres Python débutant',
            'expected_images': True
        },
        {
            'name': 'Agent Coordinateur',
            'url': '/api/chat/coordinator-agent/',
            'message': 'recommande moi des mangas action',
            'expected_images': True
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🔍 Test {test_case['name']}")
        print(f"Message: '{test_case['message']}'")
        
        try:
            response = client.post(
                test_case['url'],
                data=json.dumps({'message': test_case['message']}),
                content_type='application/json'
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data.get('agent_response', {}).get('content', '')
                
                # Chercher les images dans le contenu
                image_count = content.count('📸 ![')
                print(f"Status: ✅ Réponse OK")
                print(f"Images trouvées: {image_count}")
                
                if image_count > 0:
                    print("✅ Images présentes dans la réponse")
                    
                    # Extraire et afficher les URLs des images
                    import re
                    image_matches = re.findall(r'📸\s*!\[([^\]]*)\]\(([^)]+)\)', content)
                    for i, (title, url) in enumerate(image_matches[:2], 1):
                        print(f"  {i}. {title}: {url[:60]}...")
                else:
                    print("❌ Aucune image trouvée dans la réponse")
                
                # Afficher un extrait de la réponse
                preview = content.replace('\n', ' ')[:200]
                print(f"Aperçu: {preview}...")
                
            else:
                print(f"❌ Erreur HTTP: {response.status_code}")
                print(f"Réponse: {response.content.decode()[:200]}...")
                
        except Exception as e:
            print(f"❌ Erreur lors du test: {e}")
    
    # Restaurer ALLOWED_HOSTS
    settings.ALLOWED_HOSTS = original_allowed_hosts


def test_image_extraction():
    """Test de l'extraction d'images côté frontend"""
    print("\n\n🔍 Test d'extraction d'images JavaScript")
    print("=" * 50)
    
    # Simuler le contenu d'une réponse d'agent avec images
    sample_content = """🎌 **Recommandations Manga**

📸 ![Naruto](https://s4.anilist.co/file/anilistcdn/media/manga/cover/large/nx30011-9yUF1dXWgDOx.jpg)

1. 🎌 **Naruto** par Masashi Kishimoto
   ⭐ Note: 4.5/5 | 📅 Année: 1999
   📊 Pertinence: 95.2%
   💡 Très pertinent pour votre recherche
   📖 L'histoire de Naruto Uzumaki, un jeune ninja...

📸 ![One Piece](https://s4.anilist.co/file/anilistcdn/media/manga/cover/large/bx30013-BeslEMqiPhlk.jpg)

2. 🎌 **One Piece** par Eiichiro Oda  
   ⭐ Note: 4.8/5 | 📅 Année: 1997
   📊 Pertinence: 92.1%
   💡 Excellent choix pour les fans d'action
   📖 Les aventures de Monkey D. Luffy..."""
   
    print("Contenu d'exemple:")
    print(sample_content[:200] + "...")
    
    # Simuler l'extraction JavaScript (version Python pour test)
    import re
    
    # Regex identique à celle du JavaScript
    image_regex = r'📸\s*!\[([^\]]*)\]\(([^)]+)\)'
    matches = re.findall(image_regex, sample_content)
    
    print(f"\n📊 Images extraites: {len(matches)}")
    
    for i, (title, url) in enumerate(matches, 1):
        print(f"  {i}. Titre: {title}")
        print(f"     URL: {url[:60]}...")
        
        # Simuler l'extraction des métadonnées
        lines = sample_content.split('\n')
        for line in lines:
            if title in line:
                # Chercher l'auteur
                author_match = re.search(r'(?:par|de|by)\s+([^\n]+?)(?:\s|$)', line)
                if author_match:
                    print(f"     Auteur: {author_match.group(1).strip()}")
                
                # Chercher la note
                rating_match = re.search(r'⭐[^0-9]*([0-9.]+)/5', line)
                if rating_match:
                    print(f"     Note: {rating_match.group(1)}/5")
                break
        print()
    
    # Test de suppression des images du contenu
    content_without_images = re.sub(r'📸\s*!\[([^\]]*)\]\(([^)]+)\)\s*', '', sample_content)
    print("📝 Contenu nettoyé (sans images):")
    print(content_without_images[:300] + "...")


def main():
    """Fonction principale de test"""
    print("🚀 Test d'intégration frontend des images")
    print("=" * 60)
    
    try:
        # Test 1: Réponses API
        test_api_responses()
        
        # Test 2: Extraction JavaScript
        test_image_extraction()
        
        print("\n✅ Tests frontend terminés!")
        print("\n💡 Instructions pour tester dans le navigateur:")
        print("1. Démarrez le serveur Django: python manage.py runserver")
        print("2. Allez sur http://localhost:8000/chat/")
        print("3. Sélectionnez un agent et demandez des recommandations")
        print("4. Vérifiez que les images apparaissent dans la galerie à droite")
        
    except Exception as e:
        print(f"❌ Erreur lors des tests: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)