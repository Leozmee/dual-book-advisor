#!/usr/bin/env python3
"""
Test direct d'une réponse avec image pour le frontend
"""
import requests
import json

def test_with_manual_image():
    """Test avec une image forcée pour voir si le JavaScript fonctionne"""
    
    # URL de l'API
    url = "http://localhost:8000/api/chat/literature-agent/"
    
    # Préparer les headers
    headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': 'dummy'
    }
    
    # Cookie
    cookies = {'csrftoken': 'dummy'}
    
    # Message de test
    data = {
        "message": "Test image frontend"
    }
    
    print("=== TEST FRONTEND AVEC IMAGE ===")
    print("Envoi requête à l'API...")
    
    try:
        response = requests.post(url, headers=headers, cookies=cookies, json=data)
        
        if response.status_code == 200:
            result = response.json()
            content = result['agent_response']['content']
            
            print(f"Status: {response.status_code}")
            print(f"Taille réponse: {len(content)}")
            
            # Vérifier si des images sont présentes
            import re
            image_matches = re.findall(r'📸\s*!\[([^\]]*)\]\(([^)]+)\)', content)
            print(f"Images trouvées: {len(image_matches)}")
            
            for i, (title, url) in enumerate(image_matches):
                print(f"  {i+1}. {title}: {url}")
            
            # Afficher la réponse complète
            print("\n=== RÉPONSE COMPLÈTE ===")
            print(content)
            
            return content
            
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        
    return None

if __name__ == "__main__":
    test_with_manual_image()