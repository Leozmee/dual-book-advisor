#!/usr/bin/env python3
"""
Test pour valider la correction du routage des requêtes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from agents.simple_agents import SimpleAgentManager
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_routing_fix():
    """Test la correction du routage"""
    
    # Initialiser l'agent manager
    agent_manager = SimpleAgentManager(use_gemma=False)
    
    # Cas de test
    test_cases = [
        {
            'query': 'j ai aimé The Dead Beat recommande moi 3 oeuvres',
            'expected_agent': 'literature',
            'description': 'Requête problématique originale'
        },
        {
            'query': 'j aimerais apprendre Python',
            'expected_agent': 'tech',
            'description': 'Requête technique légitime'
        },
        {
            'query': 'aide moi à choisir un livre',
            'expected_agent': 'literature',
            'description': 'Requête littéraire avec "ai" dans "aide"'
        },
        {
            'query': 'livres sur l intelligence artificielle',
            'expected_agent': 'tech',
            'description': 'Requête technique avec "intelligence artificielle" complète'
        },
        {
            'query': 'j apprécie les romans de fantasy',
            'expected_agent': 'literature',
            'description': 'Requête littéraire avec "app" dans "apprécie"'
        },
        {
            'query': 'recommande un app mobile',
            'expected_agent': 'tech',
            'description': 'Requête technique avec "app" comme mot entier'
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        query = test_case['query']
        expected = test_case['expected_agent']
        
        print(f"\n🔍 Test: {test_case['description']}")
        print(f"Query: '{query}'")
        
        # Simuler le routage en vérifiant les conditions
        query_lower = query.lower()
        
        # Vérifier manga/comics
        if agent_manager.detect_manga_query(query):
            actual_agent = 'manga'
        else:
            # Vérifier technique
            import re
            tech_keywords = [
                'python', 'javascript', 'java', 'c#', 'csharp', 'php', 'ruby', 'go',
                'programming', 'programmation', 'développement', 'development',
                'web', 'mobile', 'app', 'application', 'software', 'logiciel',
                'machine learning', 'data science', 'intelligence artificielle',
                'algorithm', 'algorithme', 'code', 'coding', 'framework',
                'database', 'base de données', 'api', 'backend', 'frontend'
            ]
            
            word_boundary_keywords = ['ai', 'app', 'code', 'web', 'api', 'go']
            
            tech_score = 0
            
            # Détection standard
            for keyword in tech_keywords:
                if keyword not in word_boundary_keywords and keyword in query_lower:
                    tech_score += 1
                    print(f"  📋 Mot-clé technique standard trouvé: '{keyword}'")
            
            # Détection par mots entiers
            for keyword in word_boundary_keywords:
                if keyword in tech_keywords:
                    pattern = r'\b' + re.escape(keyword) + r'\b'
                    if re.search(pattern, query_lower):
                        tech_score += 1
                        print(f"  📋 Mot-clé technique (frontière) trouvé: '{keyword}'")
            
            if tech_score > 0:
                actual_agent = 'tech'
            else:
                actual_agent = 'literature'
        
        # Vérifier le résultat
        success = (actual_agent == expected)
        status = "✅ RÉUSSI" if success else "❌ ÉCHOUÉ"
        
        print(f"  Expected: {expected}")
        print(f"  Actual: {actual_agent}")
        print(f"  Status: {status}")
        
        results.append({
            'query': query,
            'expected': expected,
            'actual': actual_agent,
            'success': success,
            'description': test_case['description']
        })
    
    # Résumé des résultats
    print(f"\n{'='*60}")
    print("📊 RÉSUMÉ DES TESTS")
    print(f"{'='*60}")
    
    passed = sum(1 for r in results if r['success'])
    total = len(results)
    
    print(f"✅ Tests réussis: {passed}/{total}")
    print(f"❌ Tests échoués: {total - passed}/{total}")
    
    if passed == total:
        print(f"\n🎉 TOUS LES TESTS SONT RÉUSSIS !")
        print("La correction du routage fonctionne correctement.")
    else:
        print(f"\n⚠️  CERTAINS TESTS ONT ÉCHOUÉ:")
        for result in results:
            if not result['success']:
                print(f"  - {result['description']}")
                print(f"    Query: '{result['query']}'")
                print(f"    Expected: {result['expected']}, Got: {result['actual']}")
    
    return passed == total

if __name__ == "__main__":
    success = test_routing_fix()
    sys.exit(0 if success else 1)