#!/usr/bin/env python3
"""
Test des agents avec configuration Django correcte
"""
import os
import sys
import django

# Ajouter le répertoire du projet au path
sys.path.insert(0, '/home/utilisateur/dual-book-advisor')

# Configurer Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from agents.ollama_gemma_manager import GemmaAgentManager
from agents.cover_image_service import cover_service

def test_agent_with_images():
    print("=== TEST AGENT MANGA AVEC DJANGO ===")
    
    try:
        manager = GemmaAgentManager()
        
        # Test avec une requête manga simple
        response = manager.get_manga_recommendations('Je cherche des mangas comme Naruto')
        
        print(f"Longueur réponse: {len(response)}")
        print("Contenu:")
        print(response[:2000] if len(response) > 2000 else response)
        print()
        
        # Vérifier si des images sont présentes
        import re
        image_matches = re.findall(r'📸\s*!\[([^\]]*)\]\(([^)]+)\)', response)
        print(f"Images trouvées: {len(image_matches)}")
        for i, (title, url) in enumerate(image_matches):
            print(f"  {i+1}. {title}: {url}")
        
        if len(image_matches) == 0:
            print("\n❌ PROBLÈME: Aucune image trouvée dans la réponse")
            print("Vérifions si l'enrichissement fonctionne...")
            
            # Test direct du service d'images
            test_image = cover_service.get_cover_image("Naruto", "", "manga")
            print(f"Test direct service d'images: {test_image}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

def test_literature_agent():
    print("\n=== TEST AGENT LITTÉRATURE ===")
    
    try:
        manager = GemmaAgentManager()
        response = manager.get_literature_recommendations('Je cherche des livres comme Harry Potter')
        
        print(f"Longueur réponse: {len(response)}")
        print("Contenu:")
        print(response[:1500] if len(response) > 1500 else response)
        
        # Vérifier images
        import re
        image_matches = re.findall(r'📸\s*!\[([^\]]*)\]\(([^)]+)\)', response)
        print(f"\nImages trouvées: {len(image_matches)}")
        for i, (title, url) in enumerate(image_matches):
            print(f"  {i+1}. {title}: {url}")
            
    except Exception as e:
        print(f"❌ Erreur littérature: {e}")

if __name__ == "__main__":
    test_agent_with_images()
    test_literature_agent()