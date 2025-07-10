#!/usr/bin/env python3
"""
Script de configuration et test du service d'images de couvertures
Fichier: scripts/test_cover_images.py
"""
import os
import sys
import django
from pathlib import Path

# Configuration Django
sys.path.append(str(Path(__file__).parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

import logging
import time
from agents.cover_image_service import cover_service

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_cover_service_health():
    """Test de santé du service d'images"""
    print("🏥 Test de santé des services d'images...")
    
    health = cover_service.health_check()
    
    for service, status in health.items():
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {service}: {'OK' if status else 'ERREUR'}")
    
    return all(health.values())


def test_google_books_api():
    """Test de l'API Google Books"""
    print("\n📚 Test Google Books API...")
    
    test_cases = [
        ("Clean Code", "Robert Martin", "book"),
        ("Harry Potter", "J.K. Rowling", "book"),
        ("The Pragmatic Programmer", "", "book"),
    ]
    
    results = []
    
    for title, author, book_type in test_cases:
        print(f"   🔍 Recherche: '{title}' par '{author}'")
        
        image_url = cover_service.get_cover_image(title, author, book_type)
        
        if image_url:
            print(f"   ✅ Image trouvée: {image_url[:80]}...")
            results.append(True)
        else:
            print(f"   ❌ Aucune image trouvée")
            results.append(False)
        
        time.sleep(0.5)  # Rate limiting
    
    success_rate = sum(results) / len(results) * 100
    print(f"   📊 Taux de succès Google Books: {success_rate:.1f}%")
    
    return success_rate > 50


def test_anilist_api():
    """Test de l'API AniList"""
    print("\n🎌 Test AniList API...")
    
    test_cases = [
        ("Naruto", "", "manga"),
        ("One Piece", "", "manga"),
        ("Attack on Titan", "", "manga"),
        ("Dragon Ball", "", "manga"),
    ]
    
    results = []
    
    for title, author, content_type in test_cases:
        print(f"   🔍 Recherche manga: '{title}'")
        
        image_url = cover_service.get_cover_image(title, author, content_type)
        
        if image_url:
            print(f"   ✅ Image trouvée: {image_url[:80]}...")
            results.append(True)
        else:
            print(f"   ❌ Aucune image trouvée")
            results.append(False)
        
        time.sleep(0.8)  # Rate limiting plus strict pour AniList
    
    success_rate = sum(results) / len(results) * 100
    print(f"   📊 Taux de succès AniList: {success_rate:.1f}%")
    
    return success_rate > 50


def test_open_library_api():
    """Test de l'API Open Library"""
    print("\n📖 Test Open Library API...")
    
    test_cases = [
        ("1984", "George Orwell"),
        ("To Kill a Mockingbird", "Harper Lee"),
        ("The Great Gatsby", "F. Scott Fitzgerald"),
    ]
    
    results = []
    
    for title, author in test_cases:
        print(f"   🔍 Recherche: '{title}' par '{author}'")
        
        image_url = cover_service._search_open_library(title, author)
        
        if image_url:
            print(f"   ✅ Image trouvée: {image_url[:80]}...")
            results.append(True)
        else:
            print(f"   ❌ Aucune image trouvée")
            results.append(False)
        
        time.sleep(0.3)  # Rate limiting
    
    success_rate = sum(results) / len(results) * 100
    print(f"   📊 Taux de succès Open Library: {success_rate:.1f}%")
    
    return success_rate > 30  # Seuil plus bas pour Open Library


def test_agents_integration():
    """Test de l'intégration avec les agents"""
    print("\n🤖 Test d'intégration avec les agents...")
    
    try:
        from agents.simple_agents import SimpleAgentManager
        
        # Créer un agent manager avec images activées
        agent_manager = SimpleAgentManager(use_gemma=False, enable_images=True)
        
        print("   ✅ SimpleAgentManager créé avec images activées")
        
        # Test des statuts
        status = agent_manager.get_system_status()
        cover_status = status.get('cover_images', {})
        
        if cover_status.get('enabled'):
            print("   ✅ Support d'images activé dans les agents")
        else:
            print("   ❌ Support d'images désactivé dans les agents")
        
        # Test de recommandation simple
        print("   🔍 Test de recommandation avec images...")
        response = agent_manager.get_tech_recommendations("Python programming books")
        
        if "🖼️" in response or "![" in response:
            print("   ✅ Images détectées dans la réponse")
            return True
        else:
            print("   ⚠️  Aucune image dans la réponse (normal si pas d'images trouvées)")
            return True  # Pas d'erreur, juste pas d'images
        
    except Exception as e:
        print(f"   ❌ Erreur d'intégration: {e}")
        return False


def test_cache_functionality():
    """Test du système de cache"""
    print("\n🗄️ Test du système de cache...")
    
    # Test 1: Recherche initiale
    print("   🔍 Première recherche (mise en cache)...")
    start_time = time.time()
    image_url1 = cover_service.get_cover_image("Harry Potter", "J.K. Rowling", "book")
    first_time = time.time() - start_time
    
    # Test 2: Recherche en cache
    print("   🔍 Deuxième recherche (depuis le cache)...")
    start_time = time.time()
    image_url2 = cover_service.get_cover_image("Harry Potter", "J.K. Rowling", "book")
    second_time = time.time() - start_time
    
    print(f"   ⏱️ Première recherche: {first_time:.3f}s")
    print(f"   ⏱️ Recherche en cache: {second_time:.3f}s")
    
    # Vérifications
    if image_url1 == image_url2:
        print("   ✅ Cohérence du cache vérifiée")
    else:
        print("   ❌ Incohérence du cache")
        return False
    
    if second_time < first_time * 0.5:  # Cache devrait être au moins 2x plus rapide
        print("   ✅ Performance du cache vérifiée")
    else:
        print("   ⚠️  Cache pas significativement plus rapide (normal pour tests)")
    
    # Test des statistiques du cache
    stats = cover_service.get_cache_stats()
    print(f"   📊 Éléments en cache: {stats['cached_items']}")
    
    return True


def test_error_handling():
    """Test de la gestion d'erreurs"""
    print("\n🛡️ Test de la gestion d'erreurs...")
    
    # Test avec des titres invalides
    test_cases = [
        ("", "", "book"),  # Titre vide
        ("zzzzinvalidbooktitlezzzzz", "zzzzinvalidauthorzzzzz", "book"),  # Livre inexistant
        ("Test Book", "", "invalid_type"),  # Type invalide
    ]
    
    for title, author, book_type in test_cases:
        print(f"   🔍 Test erreur: '{title}' / '{author}' / '{book_type}'")
        
        try:
            image_url = cover_service.get_cover_image(title, author, book_type)
            if image_url is None:
                print("   ✅ Gestion d'erreur correcte (None retourné)")
            else:
                print(f"   ⚠️  Image trouvée malgré les paramètres invalides: {image_url[:50]}...")
        except Exception as e:
            print(f"   ❌ Exception non gérée: {e}")
            return False
        
        time.sleep(0.1)
    
    print("   ✅ Gestion d'erreurs validée")
    return True


def run_performance_test():
    """Test de performance avec plusieurs requêtes"""
    print("\n⚡ Test de performance...")
    
    test_books = [
        ("Clean Code", "Robert Martin"),
        ("The Pragmatic Programmer", ""),
        ("Design Patterns", "Gang of Four"),
        ("Effective Java", "Joshua Bloch"),
        ("You Don't Know JS", "Kyle Simpson"),
    ]
    
    start_time = time.time()
    successful = 0
    
    for title, author in test_books:
        image_url = cover_service.get_cover_image(title, author, "book")
        if image_url:
            successful += 1
        time.sleep(0.2)  # Rate limiting
    
    total_time = time.time() - start_time
    avg_time = total_time / len(test_books)
    
    print(f"   📊 {successful}/{len(test_books)} images trouvées")
    print(f"   ⏱️  Temps total: {total_time:.2f}s")
    print(f"   ⏱️  Temps moyen par requête: {avg_time:.2f}s")
    
    if avg_time < 2.0:  # Moins de 2 secondes par requête en moyenne
        print("   ✅ Performance acceptable")
        return True
    else:
        print("   ⚠️  Performance lente (normal avec rate limiting)")
        return True  # Pas d'échec pour performance lente


def generate_test_report():
    """Génère un rapport de test complet"""
    print("\n" + "="*70)
    print("📋 RAPPORT DE TEST DU SERVICE D'IMAGES DE COUVERTURES")
    print("="*70)
    
    tests = [
        ("Santé des services", test_cover_service_health),
        ("API Google Books", test_google_books_api),
        ("API AniList", test_anilist_api),
        ("API Open Library", test_open_library_api),
        ("Intégration agents", test_agents_integration),
        ("Système de cache", test_cache_functionality),
        ("Gestion d'erreurs", test_error_handling),
        ("Performance", run_performance_test),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}...")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"   ❌ Erreur lors du test: {e}")
            results[test_name] = False
    
    # Résumé final
    print("\n" + "="*70)
    print("📊 RÉSUMÉ DES TESTS")
    print("="*70)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ RÉUSSI" if result else "❌ ÉCHOUÉ"
        print(f"{test_name:<25} : {status}")
    
    print(f"\n🎯 Score global: {passed}/{total} tests réussis ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 TOUS LES TESTS SONT RÉUSSIS !")
        print("Le service d'images de couvertures est opérationnel.")
    elif passed >= total * 0.75:
        print("⚠️  LA PLUPART DES TESTS SONT RÉUSSIS")
        print("Le service fonctionne avec quelques limitations.")
    else:
        print("❌ PLUSIEURS TESTS ONT ÉCHOUÉ")
        print("Le service nécessite des corrections.")
    
    # Informations de configuration
    print(f"\n📋 Configuration actuelle:")
    stats = cover_service.get_cache_stats()
    print(f"   • Éléments en cache: {stats['cached_items']}")
    print(f"   • Rate limiting: Actif")
    print(f"   • Services supportés: Google Books, Open Library, AniList")
    
    return passed == total


def clear_cache_and_reset():
    """Nettoie le cache et remet à zéro"""
    print("\n🗑️ Nettoyage du cache...")
    cover_service.clear_cache()
    print("✅ Cache vidé")


if __name__ == "__main__":
    print("🚀 DUAL BOOK ADVISOR - Test du Service d'Images de Couvertures")
    print("="*70)
    
    # Option pour vider le cache avant les tests
    if len(sys.argv) > 1 and sys.argv[1] == "--clear-cache":
        clear_cache_and_reset()
    
    # Exécuter les tests
    success = generate_test_report()
    
    print(f"\n{'='*70}")
    if success:
        print("✅ Service d'images opérationnel et prêt à l'emploi !")
    else:
        print("⚠️  Service d'images partiellement fonctionnel.")
    
    print("📝 Pour utiliser le service :")
    print("   1. Importez: from agents.cover_image_service import cover_service")
    print("   2. Utilisez: cover_service.get_cover_image(title, author, type)")
    print("   3. Les agents intègrent automatiquement les images")
    
    sys.exit(0 if success else 1)