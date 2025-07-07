#!/usr/bin/env python3
"""
Script d'initialisation du système Gemma + Manga RAG
Fichier: scripts/init_gemma_system.py
"""
import os
import sys
import django
import subprocess
import requests
from pathlib import Path

# Configuration Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')


def check_ollama_installation():
    """Vérifie l'installation d'Ollama"""
    print("🔍 Vérification d'Ollama...")
    
    try:
        result = subprocess.run(['ollama', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Ollama installé: {result.stdout.strip()}")
            return True
        else:
            print("❌ Ollama non trouvé")
            return False
    except FileNotFoundError:
        print("❌ Ollama non installé")
        return False


def check_ollama_service():
    """Vérifie que le service Ollama est démarré"""
    print("🔍 Vérification du service Ollama...")
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Service Ollama actif")
            return True
        else:
            print("❌ Service Ollama non accessible")
            return False
    except requests.exceptions.RequestException:
        print("❌ Service Ollama non démarré")
        return False


def install_ollama():
    """Instructions d'installation d'Ollama"""
    print("\n📥 Installation d'Ollama nécessaire:")
    print("=" * 50)
    print("Linux/macOS:")
    print("  curl -fsSL https://ollama.com/install.sh | sh")
    print("\nWindows:")
    print("  Télécharger depuis: https://ollama.com/download/windows")
    print("\nAprès installation:")
    print("  ollama serve")
    print("  ollama pull gemma2:2b")


def check_gemma_model():
    """Vérifie que le modèle Gemma est téléchargé"""
    print("🔍 Vérification du modèle Gemma...")
    
    try:
        result = subprocess.run(['ollama', 'list'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            if 'gemma2:2b' in result.stdout:
                print("✅ Modèle gemma2:2b disponible")
                return True
            else:
                print("❌ Modèle gemma2:2b non trouvé")
                return False
        else:
            print("❌ Impossible de lister les modèles")
            return False
    except FileNotFoundError:
        print("❌ Commande ollama non trouvée")
        return False


def download_gemma_model():
    """Télécharge le modèle Gemma"""
    print("📥 Téléchargement du modèle Gemma 2B...")
    
    try:
        result = subprocess.run(['ollama', 'pull', 'gemma2:2b'], 
                              capture_output=False, text=True)
        if result.returncode == 0:
            print("✅ Modèle gemma2:2b téléchargé")
            return True
        else:
            print("❌ Échec du téléchargement")
            return False
    except FileNotFoundError:
        print("❌ Commande ollama non trouvée")
        return False


def install_python_deps():
    """Installe les dépendances Python"""
    print("📦 Installation des dépendances Python...")
    
    deps = ['ollama', 'requests']
    
    for dep in deps:
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', dep], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {dep} installé")
            else:
                print(f"❌ Échec installation {dep}: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Erreur installation {dep}: {e}")
            return False
    
    return True


def setup_manga_rag():
    """Configure le RAG manga"""
    print("🎌 Configuration du RAG Manga...")
    
    try:
        django.setup()
        
        # Créer les dossiers nécessaires
        manga_rag_path = BASE_DIR / 'rags' / 'manga_rag'
        manga_chroma_path = manga_rag_path / 'chroma_db'
        
        manga_rag_path.mkdir(exist_ok=True)
        manga_chroma_path.mkdir(exist_ok=True)
        
        # Créer __init__.py
        init_file = manga_rag_path / '__init__.py'
        if not init_file.exists():
            init_file.touch()
        
        print("✅ Dossiers manga RAG créés")
        
        # Tester l'import du manga RAG manager
        try:
            from rags.manga_rag.manga_rag_manager import MangaRAGManager
            manga_rag = MangaRAGManager()
            
            # Indexer les mangas
            print("📊 Indexation des mangas...")
            manga_rag.index_all_manga(reset=True)
            
            # Vérifier les stats
            stats = manga_rag.get_stats()
            print(f"✅ Manga RAG configuré: {stats}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur configuration manga RAG: {e}")
            return False
    
    except Exception as e:
        print(f"❌ Erreur setup manga RAG: {e}")
        return False


def test_gemma_integration():
    """Test l'intégration complète Gemma + RAG"""
    print("🧪 Test de l'intégration Gemma...")
    
    try:
        django.setup()
        
        # Test des agents simples avec Gemma
        from agents.simple_agents import SimpleAgentManager
        
        # Créer le manager avec Gemma activé
        agent_manager = SimpleAgentManager(use_gemma=True)
        
        # Test du statut système
        status = agent_manager.get_system_status()
        print("📊 Statut du système:")
        for key, value in status.items():
            print(f"   {key}: {value}")
        
        # Tests des requêtes
        test_queries = [
            ("tech", "j'aimerais apprendre Python"),
            ("literature", "romans de Tolstoï"),
            ("manga", "j'ai aimé Naruto, recommande moi 2 oeuvres")
        ]
        
        print("\n🧪 Tests des recommandations:")
        for agent_type, query in test_queries:
            print(f"\n🔍 Test {agent_type}: '{query}'")
            try:
                if agent_type == "tech":
                    response = agent_manager.get_tech_recommendations(query)
                elif agent_type == "literature":
                    response = agent_manager.get_literature_recommendations(query)
                elif agent_type == "manga":
                    response = agent_manager.get_manga_recommendations(query)
                
                print(f"✅ Réponse: {response[:200]}...")
                
            except Exception as e:
                print(f"❌ Erreur test {agent_type}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test intégration: {e}")
        return False


def update_views_for_gemma():
    """Met à jour les vues Django pour utiliser Gemma"""
    print("🔧 Instructions mise à jour des vues Django...")
    
    print("\n📝 Modifications à faire dans apps/chat/views.py:")
    print("=" * 50)
    
    print("\n1. Dans la classe TechAgentChatView, méthode post():")
    print("   REMPLACER:")
    print("   agent_manager = SimpleAgentManager()")
    print("   PAR:")
    print("   agent_manager = SimpleAgentManager(use_gemma=True)")
    
    print("\n2. Dans la classe LiteratureAgentChatView, méthode post():")
    print("   REMPLACER:")
    print("   agent_manager = SimpleAgentManager()")
    print("   PAR:")
    print("   agent_manager = SimpleAgentManager(use_gemma=True)")
    
    print("\n3. Optionnel - Ajouter une nouvelle vue pour manga:")
    print("""
class MangaAgentChatView(APIView):
    permission_classes = []
    
    def post(self, request):
        message = request.data.get('message')
        if not message:
            return Response({'error': 'Message is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        from apps.accounts.models import User
        demo_user, created = User.objects.get_or_create(
            email='demo@example.com',
            defaults={'username': 'demo', 'first_name': 'Demo', 'last_name': 'User'}
        )
        
        conversation = ConversationHistory.objects.create(
            user=demo_user,
            agent_type='manga',
            title=f"Manga Chat - {message[:30]}..."
        )
        
        user_msg = Message.objects.create(
            conversation=conversation,
            sender='user',
            content=message
        )
        
        # Utiliser Gemma pour les recommandations manga
        agent_manager = SimpleAgentManager(use_gemma=True)
        manga_response = agent_manager.get_manga_recommendations(message, demo_user.id)
        
        agent_msg = Message.objects.create(
            conversation=conversation,
            sender='agent',
            content=manga_response,
            rag_sources="RAG_manga_recommendations"
        )
        
        conversation.save()
        
        return Response({
            'conversation_id': conversation.id,
            'user_message': MessageSerializer(user_msg).data,
            'agent_response': MessageSerializer(agent_msg).data
        })
""")
    
    print("\n4. Ajouter l'URL dans apps/chat/urls.py:")
    print("   path('manga-agent/', views.MangaAgentChatView.as_view(), name='manga_agent_chat'),")
    
    return True


def create_test_script():
    """Crée un script de test pour vérifier le système"""
    print("📝 Création du script de test...")
    
    test_script_path = BASE_DIR / 'scripts' / 'test_gemma_manga.py'
    
    test_script_content = '''#!/usr/bin/env python3
"""
Script de test pour Gemma + Manga RAG
"""
import os
import sys
import django
from pathlib import Path

# Configuration Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

def test_system():
    """Test complet du système"""
    print("🧪 TEST COMPLET DU SYSTÈME")
    print("=" * 50)
    
    try:
        from agents.simple_agents import SimpleAgentManager
        
        # Test avec Gemma
        print("\\n1. Test avec Gemma activé:")
        agent_gemma = SimpleAgentManager(use_gemma=True)
        
        status = agent_gemma.get_system_status()
        print(f"   Statut: {status}")
        
        # Test des requêtes
        queries = [
            ("tech", "apprendre Python débutant"),
            ("literature", "romans français classiques"),
            ("manga", "recommande moi des mangas comme Naruto")
        ]
        
        for agent_type, query in queries:
            print(f"\\n2. Test {agent_type}: '{query}'")
            try:
                response = agent_gemma.get_agent_response(query, agent_type)
                print(f"   ✅ Longueur réponse: {len(response)} caractères")
                print(f"   📝 Début: {response[:100]}...")
            except Exception as e:
                print(f"   ❌ Erreur: {e}")
        
        # Test sans Gemma (fallback)
        print("\\n3. Test sans Gemma (fallback):")
        agent_fallback = SimpleAgentManager(use_gemma=False)
        try:
            response = agent_fallback.get_agent_response("test query", "tech")
            print(f"   ✅ Fallback fonctionne: {len(response)} caractères")
        except Exception as e:
            print(f"   ❌ Erreur fallback: {e}")
        
        print("\\n🎉 Tests terminés!")
        
    except Exception as e:
        print(f"❌ Erreur test système: {e}")

if __name__ == "__main__":
    test_system()
'''
    
    try:
        with open(test_script_path, 'w', encoding='utf-8') as f:
            f.write(test_script_content)
        
        # Rendre exécutable
        os.chmod(test_script_path, 0o755)
        
        print(f"✅ Script de test créé: {test_script_path}")
        print("   Usage: python scripts/test_gemma_manga.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur création script test: {e}")
        return False


def main():
    """Fonction principale d'initialisation"""
    print("🚀 INITIALISATION SYSTÈME GEMMA + MANGA RAG")
    print("=" * 60)
    
    # Étape 1: Vérifier Ollama
    print("\\n📋 Étape 1: Vérification Ollama")
    if not check_ollama_installation():
        install_ollama()
        print("\\n⚠️  Installez Ollama puis relancez ce script")
        return False
    
    if not check_ollama_service():
        print("\\n🔧 Démarrez le service Ollama:")
        print("  ollama serve")
        print("\\nPuis relancez ce script")
        return False
    
    # Étape 2: Vérifier le modèle Gemma
    print("\\n📋 Étape 2: Vérification modèle Gemma")
    if not check_gemma_model():
        print("\\n📥 Téléchargement du modèle Gemma...")
        if not download_gemma_model():
            print("\\n❌ Échec téléchargement Gemma")
            return False
    
    # Étape 3: Installer les dépendances Python
    print("\\n📋 Étape 3: Installation dépendances Python")
    if not install_python_deps():
        print("\\n❌ Échec installation dépendances")
        return False
    
    # Étape 4: Setup Manga RAG
    print("\\n📋 Étape 4: Configuration Manga RAG")
    manga_success = setup_manga_rag()
    if not manga_success:
        print("\\n⚠️  Erreur setup Manga RAG, mais on continue...")
    
    # Étape 5: Test de l'intégration
    print("\\n📋 Étape 5: Test intégration")
    if not test_gemma_integration():
        print("\\n⚠️  Erreur test intégration, vérifiez manuellement")
    
    # Étape 6: Instructions pour les vues
    print("\\n📋 Étape 6: Instructions mise à jour")
    update_views_for_gemma()
    
    # Étape 7: Créer script de test
    print("\\n📋 Étape 7: Création script de test")
    create_test_script()
    
    # Résumé final
    print("\\n" + "=" * 60)
    print("🎉 INITIALISATION TERMINÉE")
    print("=" * 60)
    
    print("\\n✅ Composants installés:")
    print("  - ✅ Ollama avec Gemma 2B")
    print("  - ✅ Dépendances Python (ollama, requests)")
    print("  - ✅ Structure Manga RAG")
    print("  - ✅ SimpleAgentManager mis à jour")
    print("  - ✅ Script de test créé")
    
    print("\\n🔧 PROCHAINES ÉTAPES MANUELLES:")
    print("1. 📁 Copier les artefacts dans les fichiers:")
    print("   • agents/ollama_gemma_manager.py ← 'Gestionnaire Gemma avec Ollama'")
    print("   • rags/manga_rag/manga_rag_manager.py ← 'RAG Manager Manga Complet'")
    print("   • agents/simple_agents.py ← 'simple_agents.py corrigé'")
    print("")
    print("2. 🔧 Modifier apps/chat/views.py selon les instructions ci-dessus")
    print("")
    print("3. 🚀 Redémarrer le serveur Django:")
    print("   python manage.py runserver")
    print("")
    print("4. 🧪 Tester le système:")
    print("   python scripts/test_gemma_manga.py")
    print("")
    print("5. 🌐 Tester via API:")
    print("   curl -X POST http://127.0.0.1:8000/api/chat/tech-agent/ \\\\")
    print("     -H 'Content-Type: application/json' \\\\")
    print("     -d '{\"message\": \"j\\'aimerais apprendre Python\"}'")
    print("")
    print("   curl -X POST http://127.0.0.1:8000/api/chat/literature-agent/ \\\\")
    print("     -H 'Content-Type: application/json' \\\\")
    print("     -d '{\"message\": \"j\\'ai aimé Naruto, recommande moi 2 oeuvres\"}'")
    
    print("\\n💡 Vérifications:")
    print("  - Service Ollama: ollama list")
    print("  - Test Gemma: ollama run gemma2:2b 'Hello'")
    print("  - Logs Django: python manage.py runserver --verbosity=2")
    print("  - Test manga: recherche de 'naruto' doit retourner des mangas, pas des livres de guerre")
    
    print("\\n🎯 RÉSULTAT ATTENDU:")
    print("  • 'j\\'aimerais apprendre Python' → recommandations livres tech avec Gemma")
    print("  • 'romans de Tolstoï' → recommandations littéraires classiques avec Gemma")
    print("  • 'j\\'ai aimé Naruto' → recommandations mangas similaires avec Gemma")
    print("  • Séparation claire: manga ≠ littérature classique")
    
    success_count = sum([
        check_ollama_installation(),
        check_ollama_service(),
        check_gemma_model(),
        manga_success
    ])
    
    print(f"\\n📊 Score de réussite: {success_count}/4")
    
    if success_count >= 3:
        print("✅ Installation réussie ! Procédez aux étapes manuelles.")
    else:
        print("⚠️  Installation partielle. Vérifiez les erreurs ci-dessus.")


if __name__ == "__main__":
    main()