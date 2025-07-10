#!/usr/bin/env python3
"""
Debug du service d'images dans GemmaAgentManager
"""
import os
import sys
import django

# Ajouter le répertoire du projet au path
sys.path.insert(0, '/home/utilisateur/dual-book-advisor')

# Configurer Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from agents.ollama_gemma_manager import GemmaAgentManager, COVER_SERVICE_AVAILABLE

def debug_cover_service():
    print("=== DEBUG COVER SERVICE ===")
    
    print(f"COVER_SERVICE_AVAILABLE: {COVER_SERVICE_AVAILABLE}")
    
    # Test d'initialisation
    manager = GemmaAgentManager()
    print(f"Manager use_cover_images: {manager.use_cover_images}")
    
    # Test du service directement
    try:
        from agents.cover_image_service import cover_service
        print("✅ Import cover_service: OK")
        
        # Test d'une recherche simple
        test_url = cover_service.get_cover_image("Naruto", "", "manga")
        print(f"Test image Naruto: {test_url}")
        
    except Exception as e:
        print(f"❌ Erreur import cover_service: {e}")
    
    # Test de la méthode d'enrichissement
    print("\n=== TEST ENRICHISSEMENT ===")
    try:
        # Créer des données de test
        test_recs = [
            {'title': 'One Piece', 'author': 'Eiichiro Oda', 'type': 'manga'}
        ]
        
        result = manager._enrich_response_with_images(
            "Test response with One Piece recommendation", 
            test_recs, 
            'manga'
        )
        
        print(f"Résultat enrichi: {result[:200]}...")
        
        # Vérifier si des images sont présentes
        import re
        image_matches = re.findall(r'📸\s*!\[([^\]]*)\]\(([^)]+)\)', result)
        print(f"Images trouvées dans l'enrichissement: {len(image_matches)}")
        
    except Exception as e:
        print(f"❌ Erreur enrichissement: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_cover_service()