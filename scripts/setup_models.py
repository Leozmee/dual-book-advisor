#!/usr/bin/env python3
"""
Script de configuration automatique des modèles
Fichier: scripts/setup_models.py

Configure automatiquement les modèles Llama, Mistral et Gemma
"""
import os
import sys
import subprocess
import time
import requests
from typing import List, Dict

def check_ollama_service():
    """Vérifie si Ollama est installé et démarré"""
    print("🔍 Vérification du service Ollama...")
    
    try:
        # Vérifier si Ollama est installé
        result = subprocess.run(['which', 'ollama'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Ollama n'est pas installé")
            print("💡 Installez Ollama: https://ollama.ai/")
            return False
        
        print("✅ Ollama est installé")
        
        # Vérifier si le service est démarré
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=5)
            if response.status_code == 200:
                print("✅ Service Ollama démarré")
                return True
            else:
                print("❌ Service Ollama non accessible")
                return False
        except requests.exceptions.RequestException:
            print("❌ Service Ollama non démarré")
            print("💡 Démarrez le service: ollama serve")
            return False
            
    except Exception as e:
        print(f"❌ Erreur vérification Ollama: {e}")
        return False

def get_installed_models() -> List[str]:
    """Obtient la liste des modèles installés"""
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=10)
        if response.status_code == 200:
            data = response.json()
            models = [model['name'] for model in data.get('models', [])]
            return models
        return []
    except Exception as e:
        print(f"❌ Erreur obtention modèles: {e}")
        return []

def install_model(model_name: str) -> bool:
    """Installe un modèle via Ollama"""
    print(f"📥 Installation du modèle {model_name}...")
    
    try:
        # Lancer l'installation
        process = subprocess.Popen(
            ['ollama', 'pull', model_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Attendre et afficher le progrès
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(f"   📊 {output.strip()}")
        
        return_code = process.poll()
        
        if return_code == 0:
            print(f"✅ Modèle {model_name} installé avec succès")
            return True
        else:
            stderr = process.stderr.read()
            print(f"❌ Erreur installation {model_name}: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur installation {model_name}: {e}")
        return False

def setup_optimal_models():
    """Configure les modèles optimaux pour le RAG"""
    print("🚀 Configuration des modèles optimaux pour RAG...")
    print("=" * 60)
    
    # Modèles recommandés par ordre de priorité
    recommended_models = [
        {
            'name': 'llama3.2:3b',
            'description': 'Llama 3.2 3B - Équilibre performance/vitesse',
            'size': '~6GB',
            'priority': 'high'
        },
        {
            'name': 'mistral:7b',
            'description': 'Mistral 7B - Excellent pour RAG',
            'size': '~8GB',
            'priority': 'high'
        },
        {
            'name': 'gemma2:2b',
            'description': 'Gemma 2B - Rapide et efficace',
            'size': '~4GB',
            'priority': 'medium'
        },
        {
            'name': 'llama3.2:1b',
            'description': 'Llama 3.2 1B - Ultra-rapide',
            'size': '~2GB',
            'priority': 'low'
        }
    ]
    
    # Vérifier les modèles installés
    installed = get_installed_models()
    print(f"📊 Modèles déjà installés: {installed}")
    
    # Installer les modèles manquants
    for model in recommended_models:
        if model['name'] not in installed:
            print(f"\n🎯 Modèle manquant: {model['name']}")
            print(f"   📝 Description: {model['description']}")
            print(f"   💾 Taille: {model['size']}")
            print(f"   🔥 Priorité: {model['priority']}")
            
            if model['priority'] == 'high':
                install_model(model['name'])
            else:
                user_input = input(f"   ❓ Installer {model['name']} ? (y/n): ").lower()
                if user_input == 'y':
                    install_model(model['name'])
                else:
                    print(f"   ⏭️ Installation de {model['name']} ignorée")
        else:
            print(f"✅ {model['name']} déjà installé")

def test_installed_models():
    """Test les modèles installés"""
    print("\n🧪 Test des modèles installés...")
    print("=" * 60)
    
    installed = get_installed_models()
    test_prompt = "Bonjour, peux-tu me recommander un bon livre de programmation Python ?"
    
    for model in installed:
        print(f"\n🔬 Test du modèle {model}...")
        
        try:
            # Faire une requête de test
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": test_prompt}],
                "options": {"temperature": 0.7, "num_predict": 100}
            }
            
            response = requests.post(
                'http://localhost:11434/api/chat',
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                # Traiter la réponse streaming
                lines = response.text.strip().split('\n')
                full_response = ""
                
                for line in lines:
                    if line:
                        try:
                            import json
                            data = json.loads(line)
                            if 'message' in data and 'content' in data['message']:
                                full_response += data['message']['content']
                        except:
                            pass
                
                print(f"   ✅ Réponse reçue: {len(full_response)} caractères")
                print(f"   📝 Début: {full_response[:100]}...")
                
            else:
                print(f"   ❌ Erreur HTTP: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Erreur test: {e}")

def configure_environment():
    """Configure l'environnement pour les modèles"""
    print("\n⚙️ Configuration de l'environnement...")
    print("=" * 60)
    
    # Vérifier le fichier .env
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    
    if os.path.exists(env_file):
        print("✅ Fichier .env trouvé")
        
        # Lire le contenu actuel
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Vérifier les variables importantes
        required_vars = [
            'OLLAMA_BASE_URL',
            'PREFERRED_MODELS',
            'MODEL_EVALUATION_ENABLED'
        ]
        
        missing_vars = []
        for var in required_vars:
            if var not in content:
                missing_vars.append(var)
        
        if missing_vars:
            print(f"⚠️ Variables manquantes: {missing_vars}")
            
            # Ajouter les variables manquantes
            additional_config = """
# Configuration automatique des modèles
export OLLAMA_BASE_URL="http://localhost:11434"
export PREFERRED_MODELS="llama3.2:3b,mistral:7b,gemma2:2b"
export MODEL_EVALUATION_ENABLED="true"
"""
            
            with open(env_file, 'a') as f:
                f.write(additional_config)
            
            print("✅ Variables ajoutées au fichier .env")
        else:
            print("✅ Toutes les variables sont configurées")
    
    else:
        print("❌ Fichier .env non trouvé")
        print("💡 Créez le fichier .env avec la configuration recommandée")

def get_system_info():
    """Affiche les informations système"""
    print("\n💻 Informations système...")
    print("=" * 60)
    
    try:
        # RAM disponible
        import psutil
        memory = psutil.virtual_memory()
        print(f"💾 RAM totale: {memory.total / (1024**3):.1f} GB")
        print(f"💾 RAM disponible: {memory.available / (1024**3):.1f} GB")
        
        # Espace disque
        disk = psutil.disk_usage('/')
        print(f"💿 Espace disque libre: {disk.free / (1024**3):.1f} GB")
        
        # Recommandations
        if memory.total < 8 * (1024**3):  # Moins de 8GB
            print("⚠️ Recommandation: Utilisez uniquement gemma2:2b et llama3.2:1b")
        elif memory.total < 16 * (1024**3):  # Moins de 16GB
            print("💡 Recommandation: llama3.2:3b + gemma2:2b recommandés")
        else:
            print("🚀 Recommandation: Tous les modèles peuvent être utilisés")
            
    except ImportError:
        print("❌ psutil non disponible, impossible d'obtenir les infos système")
    except Exception as e:
        print(f"❌ Erreur infos système: {e}")

def main():
    """Fonction principale"""
    print("🚀 Configuration Automatique des Modèles Multi-LLM")
    print("=" * 80)
    
    # 1. Informations système
    get_system_info()
    
    # 2. Vérifier Ollama
    if not check_ollama_service():
        print("\n❌ Configuration impossible sans Ollama")
        sys.exit(1)
    
    # 3. Configurer l'environnement
    configure_environment()
    
    # 4. Installer les modèles
    setup_optimal_models()
    
    # 5. Tester les modèles
    test_installed_models()
    
    print("\n" + "=" * 80)
    print("✅ Configuration terminée!")
    
    # Afficher les prochaines étapes
    print("\n🎯 Prochaines étapes:")
    print("   1. Lancez le test d'évaluation: python scripts/test_model_evaluation.py")
    print("   2. Démarrez l'application Django")
    print("   3. Testez les différents agents via l'interface web")
    
    print("\n💡 Commandes utiles:")
    print("   - ollama list : Liste les modèles installés")
    print("   - ollama rm <model> : Supprime un modèle")
    print("   - ollama pull <model> : Installe un modèle")

if __name__ == "__main__":
    main()