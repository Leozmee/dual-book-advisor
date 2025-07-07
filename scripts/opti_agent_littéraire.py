"""
Script complet pour optimiser le RAG littéraire
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

def optimize_literature_rag():
    """Optimise le gestionnaire RAG littéraire"""
    
    rag_file = BASE_DIR / 'rags' / 'literature_rag' / 'literature_rag_manager.py'
    
    if not rag_file.exists():
        print(f"❌ Fichier non trouvé: {rag_file}")
        return False
    
    print(f"🔧 Optimisation de {rag_file}")
    
    # Lire le fichier
    with open(rag_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Créer une sauvegarde
    backup_file = rag_file.with_suffix('.py.backup_complete')
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"💾 Sauvegarde: {backup_file}")
    
    # Optimisations simples et efficaces
    modifications = [
        ('similarity_threshold = 0.25', 'similarity_threshold = 0.15  # Optimisé'),
        ('similarity_threshold = 0.58', 'similarity_threshold = 0.15  # Optimisé'),
        ('n_results * 2', 'n_results * 3  # Plus de candidats'),
        ('similarity_threshold=0.7', 'similarity_threshold=0.15'),
    ]
    
    changed = False
    for old, new in modifications:
        if old in content:
            content = content.replace(old, new)
            print(f"✅ Modifié: {old} → {new}")
            changed = True
    
    if changed:
        # Sauvegarder les modifications
        with open(rag_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Optimisations appliquées avec succès")
        return True
    else:
        print("⚠️ Aucune modification nécessaire (déjà optimisé)")
        return True

def test_optimization():
    """Test les optimisations"""
    print("\n🧪 Test des optimisations...")
    
    try:
        # Recharger le module modifié
        import importlib
        if 'agents.simple_agents' in sys.modules:
            importlib.reload(sys.modules['agents.simple_agents'])
        
        from agents.simple_agents import SimpleAgentManager
        agent = SimpleAgentManager()
        
        # Test avec Harry Potter
        print("🔍 Test: 'j'ai aimé harry potter, donne moi 2 oeuvres similaires'")
        result = agent.get_literature_recommendations("j'ai aimé harry potter, donne moi 2 oeuvres similaires")
        
        # Analyser le résultat
        if len(result) > 100:
            print("✅ Réponse générée")
            if any(word in result.lower() for word in ['fantasy', 'magic', 'adventure', 'young']):
                print("✅ Contenu pertinent détecté")
            else:
                print("⚠️ Contenu possiblement non pertinent")
        else:
            print("❌ Réponse trop courte")
        
        # Test agent technique
        print("\n🔧 Test agent technique:")
        tech_result = agent.get_tech_recommendations("donne moi 2 livres pour apprendre Python")
        
        import re
        recs = re.findall(r'\n\d+\.', tech_result)
        print(f"📊 Nombre de recommandations: {len(recs)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Optimisation Complète du RAG Littéraire")
    print("=" * 50)
    
    # Étape 1: Optimiser le RAG
    if optimize_literature_rag():
        print("✅ RAG littéraire optimisé")
        
        # Étape 2: Tester
        test_optimization()
        
        print("\n🎉 Optimisation terminée !")
        print("💡 Redémarrez le serveur Django pour appliquer les changements")
        print("💡 Testez avec: python test_agents.py")
    else:
        print("❌ Échec de l'optimisation")

if __name__ == "__main__":
    main()