#!/usr/bin/env python3
"""
Simple vérification du prompt modifié
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

def check_prompt_modifications():
    """Vérifie que les modifications du prompt sont correctes"""
    print("📝 Vérification des modifications du prompt")
    print("=" * 50)
    
    # Lire le fichier directement
    agent_file = BASE_DIR / "agents/langchain_agents/nodes/agent_nodes.py"
    
    with open(agent_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifications clés
    checks = [
        ("Questions précises identifiées", "QUESTIONS PRÉCISES D'AUTEUR" in content),
        ("Pas de recommandations", "NE FAIS AUCUNE RECOMMANDATION" in content),
        ("Réponse courte", "RÉPONSE COURTE UNIQUEMENT" in content),
        ("Exemples exacts", "EXEMPLES EXACTS DE TRAITEMENT" in content),
        ("Règles absolues", "RÈGLES ABSOLUES" in content),
        ("Wikipedia direct", "wikipedia_search` DIRECTEMENT" in content),
        ("Format réponse auteur", "**[Auteur]** a écrit **[titre]**" in content),
        ("Workflow critique", "ANALYSE CRITIQUE" in content),
        ("Réponse stricte", "RÉPONSE STRICTE" in content),
        ("Dépasse jamais", "Ne dépasse JAMAIS le cadre" in content)
    ]
    
    all_good = True
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"{status} {check_name}")
        if not result:
            all_good = False
    
    if all_good:
        print("\n🎉 Toutes les modifications sont présentes !")
    else:
        print("\n⚠️ Certaines modifications manquent")
    
    # Afficher les sections modifiées
    print(f"\n📄 Extraits clés du prompt:")
    
    # Workflow
    if "WORKFLOW OBLIGATOIRE" in content:
        start = content.find("**WORKFLOW OBLIGATOIRE:**")
        end = content.find("**OUTILS DISPONIBLES:**")
        if start != -1 and end != -1:
            workflow = content[start:end].strip()
            print(f"\n🔧 WORKFLOW:")
            print(f"   {workflow[:300]}...")
    
    # Exemples
    if "EXEMPLES EXACTS" in content:
        start = content.find("**EXEMPLES EXACTS DE TRAITEMENT:**")
        end = content.find("**RÈGLES ABSOLUES:**")
        if start != -1 and end != -1:
            exemples = content[start:end].strip()
            print(f"\n📋 EXEMPLES:")
            print(f"   {exemples[:400]}...")
    
    # Règles
    if "RÈGLES ABSOLUES" in content:
        start = content.find("**RÈGLES ABSOLUES :**")
        end = content.find("N'hésite pas à utiliser")
        if start != -1 and end != -1:
            regles = content[start:end].strip()
            print(f"\n⚖️ RÈGLES:")
            print(f"   {regles}")

def main():
    check_prompt_modifications()

if __name__ == "__main__":
    main()