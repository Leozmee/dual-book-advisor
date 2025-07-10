#!/usr/bin/env python3
"""
Script pour tester les réponses des agents avec images
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

from agents.simple_agents import SimpleAgentManager
import re

def test_manga_agent():
    """Test l'agent manga avec images"""
    print("🎌 Test Agent Manga avec images")
    print("=" * 50)
    
    agent_manager = SimpleAgentManager(use_cover_images=True)
    
    query = "manga comme naruto"
    print(f"Requête: {query}")
    
    try:
        response = agent_manager.get_manga_recommendations(query, user_id=1)
        
        # Compter les images
        image_count = response.count('📸 ![')
        print(f"📊 Images trouvées: {image_count}")
        
        # Extraire les URLs d'images
        image_regex = r'📸\s*!\[([^\]]*)\]\(([^)]+)\)'
        matches = re.findall(image_regex, response)
        
        print(f"🖼️ Images extraites: {len(matches)}")
        for i, (title, url) in enumerate(matches[:3], 1):
            print(f"  {i}. {title}: {url[:60]}...")
        
        # Afficher un extrait de la réponse
        print(f"\n📝 Extrait de la réponse:")
        print(response[:300] + "..." if len(response) > 300 else response)
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

def test_literature_agent():
    """Test l'agent littérature avec images"""
    print("\n\n📚 Test Agent Littérature avec images")
    print("=" * 50)
    
    agent_manager = SimpleAgentManager(use_cover_images=True)
    
    query = "livres comme Harry Potter"
    print(f"Requête: {query}")
    
    try:
        response = agent_manager.get_literature_recommendations(query, user_id=1)
        
        # Compter les images
        image_count = response.count('📸 ![')
        print(f"📊 Images trouvées: {image_count}")
        
        # Extraire les URLs d'images
        image_regex = r'📸\s*!\[([^\]]*)\]\(([^)]+)\)'
        matches = re.findall(image_regex, response)
        
        print(f"🖼️ Images extraites: {len(matches)}")
        for i, (title, url) in enumerate(matches[:3], 1):
            print(f"  {i}. {title}: {url[:60]}...")
        
        # Afficher un extrait de la réponse
        print(f"\n📝 Extrait de la réponse:")
        print(response[:300] + "..." if len(response) > 300 else response)
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

def test_tech_agent():
    """Test l'agent technique avec images"""
    print("\n\n🔧 Test Agent Technique avec images")
    print("=" * 50)
    
    agent_manager = SimpleAgentManager(use_cover_images=True)
    
    query = "Python pour débutants"
    print(f"Requête: {query}")
    
    try:
        response = agent_manager.get_tech_recommendations(query, user_id=1)
        
        # Compter les images
        image_count = response.count('📸 ![')
        print(f"📊 Images trouvées: {image_count}")
        
        # Extraire les URLs d'images
        image_regex = r'📸\s*!\[([^\]]*)\]\(([^)]+)\)'
        matches = re.findall(image_regex, response)
        
        print(f"🖼️ Images extraites: {len(matches)}")
        for i, (title, url) in enumerate(matches[:3], 1):
            print(f"  {i}. {title}: {url[:60]}...")
        
        # Afficher un extrait de la réponse
        print(f"\n📝 Extrait de la réponse:")
        print(response[:300] + "..." if len(response) > 300 else response)
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

def test_coordinator_agent():
    """Test l'agent coordinateur avec images"""
    print("\n\n🧭 Test Agent Coordinateur avec images")
    print("=" * 50)
    
    agent_manager = SimpleAgentManager(use_cover_images=True)
    
    query = "recommande moi des manga d'action"
    print(f"Requête: {query}")
    
    try:
        response = agent_manager.route_query(query)
        
        # Compter les images
        image_count = response.count('📸 ![')
        print(f"📊 Images trouvées: {image_count}")
        
        # Extraire les URLs d'images
        image_regex = r'📸\s*!\[([^\]]*)\]\(([^)]+)\)'
        matches = re.findall(image_regex, response)
        
        print(f"🖼️ Images extraites: {len(matches)}")
        for i, (title, url) in enumerate(matches[:3], 1):
            print(f"  {i}. {title}: {url[:60]}...")
        
        # Afficher un extrait de la réponse
        print(f"\n📝 Extrait de la réponse:")
        print(response[:300] + "..." if len(response) > 300 else response)
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

def test_without_images():
    """Test sans images pour comparaison"""
    print("\n\n🚫 Test sans images (pour comparaison)")
    print("=" * 50)
    
    agent_manager = SimpleAgentManager(use_cover_images=False)
    
    query = "manga comme naruto"
    print(f"Requête: {query}")
    
    try:
        response = agent_manager.get_manga_recommendations(query, user_id=1)
        
        # Compter les images
        image_count = response.count('📸 ![')
        print(f"📊 Images trouvées: {image_count}")
        
        # Afficher un extrait de la réponse
        print(f"\n📝 Extrait de la réponse:")
        print(response[:300] + "..." if len(response) > 300 else response)
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("🚀 Test des réponses des agents avec images")
    print("=" * 70)
    
    # Test des différents agents
    test_manga_agent()
    test_literature_agent()
    test_tech_agent()
    test_coordinator_agent()
    test_without_images()
    
    print("\n✅ Tests terminés!")
    print("\n💡 Points clés:")
    print("- Les agents avec use_cover_images=True devraient inclure des images")
    print("- Le format des images est: 📸 ![titre](url)")
    print("- Les images apparaissent avant chaque recommandation")
    print("- L'agent coordinateur route vers l'agent approprié avec images")

if __name__ == "__main__":
    main()