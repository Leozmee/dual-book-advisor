#!/usr/bin/env python3
"""
Test de l'indicateur d'agent séparé
"""

import os
import sys
import django
from pathlib import Path

# Configuration Django
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.chat.views import CoordinatorAgentChatView

def test_clean_agent_indicators():
    """Test la fonction de nettoyage des indicateurs d'agent"""
    
    view = CoordinatorAgentChatView()
    
    # Test avec indicateur technique
    content_tech = "🔧 **Réponse du Tech Agent** 🔧 **Recommandations Techniques (Gemma-2-2b)** Voici des livres Python..."
    cleaned = view._clean_agent_indicators(content_tech)
    print(f"✅ Tech original : {content_tech[:50]}...")
    print(f"✅ Tech nettoyé  : {cleaned[:50]}...")
    assert "🔧 **Réponse du Tech Agent**" not in cleaned
    assert "🔧 **Recommandations Techniques" not in cleaned
    
    # Test avec indicateur littéraire
    content_lit = "📚 **Réponse du Literature Agent** 📚 **Recommandations Littéraires** Voici des livres similaires..."
    cleaned = view._clean_agent_indicators(content_lit)
    print(f"✅ Lit original : {content_lit[:50]}...")
    print(f"✅ Lit nettoyé  : {cleaned[:50]}...")
    assert "📚 **Réponse du Literature Agent**" not in cleaned
    assert "📚 **Recommandations Littéraires" not in cleaned
    
    # Test avec indicateur manga
    content_manga = "🎌 **Réponse du Manga/Comics Agent** 🎌 **Recommandations Manga** Voici des mangas..."
    cleaned = view._clean_agent_indicators(content_manga)
    print(f"✅ Manga original : {content_manga[:50]}...")
    print(f"✅ Manga nettoyé  : {cleaned[:50]}...")
    assert "🎌 **Réponse du Manga/Comics Agent**" not in cleaned
    assert "🎌 **Recommandations Manga" not in cleaned
    
    print("\n🎉 Tous les tests de nettoyage ont réussi !")

def test_agent_detection():
    """Test la détection d'agent à partir de la réponse"""
    
    view = CoordinatorAgentChatView()
    
    # Test détection technique
    tech_response = "🔧 **Recommandations Techniques** Voici des livres Python..."
    agent_type = view._determine_agent_from_response(tech_response)
    print(f"✅ Détection tech : {agent_type}")
    assert agent_type == "tech"
    
    # Test détection littéraire
    lit_response = "📚 **Recommandations Littéraires** Voici des romans..."
    agent_type = view._determine_agent_from_response(lit_response)
    print(f"✅ Détection littéraire : {agent_type}")
    assert agent_type == "literature"
    
    # Test détection manga
    manga_response = "🎌 **Recommandations Manga** Voici des mangas..."
    agent_type = view._determine_agent_from_response(manga_response)
    print(f"✅ Détection manga : {agent_type}")
    assert agent_type == "manga"
    
    print("\n🎉 Tous les tests de détection ont réussi !")

if __name__ == "__main__":
    print("=" * 70)
    print("🧪 TEST DE L'INDICATEUR D'AGENT SÉPARÉ")
    print("=" * 70)
    
    test_clean_agent_indicators()
    test_agent_detection()
    
    print("\n" + "=" * 70)
    print("✅ TOUS LES TESTS ONT RÉUSSI !")
    print("=" * 70)
    print("\n📝 Résumé des améliorations :")
    print("   • Indicateur d'agent séparé au-dessus de la barre de recherche")
    print("   • Animation de chargement avec 3 points qui bougent")
    print("   • Nettoyage automatique des indicateurs dans le contenu")
    print("   • Détection automatique de l'agent qui répond")
    print("   • Affichage temporaire de l'indicateur (2 secondes)")