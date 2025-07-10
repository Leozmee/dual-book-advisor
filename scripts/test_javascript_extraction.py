#!/usr/bin/env python3
"""
Script pour tester l'extraction d'images JavaScript simulée
"""
import re
import json

def test_javascript_extraction():
    """Simule l'extraction d'images côté JavaScript"""
    print("🧪 Test d'extraction d'images JavaScript")
    print("=" * 50)
    
    # Contenu d'exemple qui simule une réponse d'agent
    sample_responses = [
        {
            "name": "Réponse Manga",
            "content": """🎌 **Recommandations Manga**

📸 ![Naruto](https://s4.anilist.co/file/anilistcdn/media/manga/cover/large/nx30011-9yUF1dXWgDOx.jpg)

1. 🎌 **Naruto** par Masashi Kishimoto
   ⭐ Note: 4.5/5 | 📅 Année: 1999
   📊 Pertinence: 95.2%
   💡 Très pertinent pour votre recherche

📸 ![One Piece](https://s4.anilist.co/file/anilistcdn/media/manga/cover/large/bx30013-BeslEMqiPhlk.jpg)

2. 🎌 **One Piece** par Eiichiro Oda
   ⭐ Note: 4.8/5 | 📅 Année: 1997
   📊 Pertinence: 92.1%
   💡 Excellent choix pour les fans d'action"""
        },
        {
            "name": "Réponse Littérature",
            "content": """📚 **Recommandations Littéraires**

📸 ![Harry Potter](https://books.google.com/books/content?id=nvijsUyJYR4C&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api)

1. **Harry Potter** de J. K. Rowling
   ⭐ Note: 4.78/5 | 📅 2004
   📊 Pertinence: 41.8%
   💡 Pertinent pour votre recherche

📸 ![1984](https://books.google.com/books/content?id=DNMwEAAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api)

2. **1984** par George Orwell
   ⭐ Note: 4.2/5 | 📅 1949
   📊 Pertinence: 38.5%
   💡 Classique incontournable"""
        },
        {
            "name": "Réponse Tech",
            "content": """🔧 **Recommandations Techniques**

📸 ![Python Programming for Beginners](https://books.google.com/books/content?id=2lI3EQAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api)

1. **Python Programming for Beginners** par Philip Robbins
   ⭐ Note: 4.8/5 | 💰 $23.72
   📊 Pertinence: 70.6%
   💡 Pertinent pour votre recherche"""
        }
    ]
    
    total_images = 0
    
    for response in sample_responses:
        print(f"\n🔍 Test: {response['name']}")
        print("=" * 30)
        
        # Simulation de l'extraction JavaScript
        images = extract_book_images(response['content'])
        
        print(f"📊 Images extraites: {len(images)}")
        total_images += len(images)
        
        for i, image in enumerate(images, 1):
            print(f"  {i}. {image['title']}")
            print(f"     URL: {image['image'][:60]}...")
            print(f"     Auteur: {image['author']}")
            print(f"     Note: {image['rating']}")
            print(f"     Type: {image['type']}")
            print()
        
        # Test de suppression des images
        clean_content = remove_image_tags(response['content'])
        print(f"📝 Contenu nettoyé (premiers 150 caractères):")
        print(clean_content[:150] + "...")
        print()
    
    print(f"✅ Test terminé! Total des images extraites: {total_images}")

def extract_book_images(content):
    """Simule la fonction extractBookImages du JavaScript"""
    # Regex identique au JavaScript
    image_regex = r'📸\s*!\[([^\]]*)\]\(([^)]+)\)'
    matches = re.findall(image_regex, content)
    
    images = []
    for title, image_url in matches:
        # Extraction des informations du contexte
        book_info = extract_book_info_from_context(content, title)
        
        image_data = {
            'title': title or 'Livre sans titre',
            'image': image_url,
            'author': book_info.get('author', ''),
            'rating': book_info.get('rating', ''),
            'type': book_info.get('type', ''),
            'id': len(images) + 1
        }
        images.append(image_data)
    
    return images

def extract_book_info_from_context(content, book_title):
    """Simule l'extraction d'informations du contexte"""
    lines = content.split('\n')
    book_info = {'author': '', 'rating': '', 'type': ''}
    
    for i, line in enumerate(lines):
        if book_title in line:
            # Chercher dans les 5 lignes suivantes
            for j in range(i, min(i + 5, len(lines))):
                context_line = lines[j]
                
                # Extraire l'auteur
                author_match = re.search(r'(?:par|de|by)\s+([^\n]+?)(?:\s|$)', context_line)
                if author_match and not book_info['author']:
                    book_info['author'] = author_match.group(1).strip().replace(',', '').split('|')[0].strip()
                
                # Extraire la note
                rating_match = re.search(r'⭐[^0-9]*([0-9.]+)\/5', context_line)
                if rating_match and not book_info['rating']:
                    book_info['rating'] = rating_match.group(1) + '/5'
                
                # Déterminer le type
                if '🎌' in context_line:
                    book_info['type'] = 'Manga'
                elif '🦸' in context_line:
                    book_info['type'] = 'Comics'
                elif '🔧' in context_line:
                    book_info['type'] = 'Tech'
                elif '📚' in context_line:
                    book_info['type'] = 'Littérature'
            break
    
    return book_info

def remove_image_tags(content):
    """Simule la fonction removeImageTags du JavaScript"""
    return re.sub(r'📸\s*!\[([^\]]*)\]\(([^)]+)\)\s*', '', content)

def test_error_handling():
    """Test de gestion des erreurs"""
    print("\n🔍 Test de gestion des erreurs")
    print("=" * 30)
    
    # Contenu sans images
    content_no_images = """🎌 **Recommandations Manga**

1. 🎌 **Naruto** par Masashi Kishimoto
   ⭐ Note: 4.5/5 | 📅 Année: 1999"""
   
    images = extract_book_images(content_no_images)
    print(f"📊 Images extraites (contenu sans images): {len(images)}")
    
    # Contenu avec images malformées
    content_malformed = """📸 ![Titre incomplet](
📸 ![](https://example.com/image.jpg)
📸 ![Titre correct](https://example.com/correct.jpg)"""
    
    images = extract_book_images(content_malformed)
    print(f"📊 Images extraites (contenu malformé): {len(images)}")
    
    for image in images:
        print(f"  - {image['title']}: {image['image'][:40]}...")

def main():
    print("🚀 Test d'extraction d'images JavaScript")
    print("=" * 60)
    
    test_javascript_extraction()
    test_error_handling()
    
    print("\n💡 Informations pour le debugging:")
    print("- Les images sont extraites avec la regex: 📸\\s*!\\[([^\\]]*)\\]\\(([^)]+)\\)")
    print("- Le contenu est nettoyé en supprimant les balises d'images")
    print("- Les métadonnées sont extraites du contexte autour du titre")
    print("- Le JavaScript utilise la même logique que ce test Python")

if __name__ == "__main__":
    main()