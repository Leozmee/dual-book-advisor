#!/usr/bin/env python3
"""
Fix minimal et sûr pour le RAG littéraire
"""
import os
from pathlib import Path

def apply_minimal_fix():
    """Applique le fix minimal sans risquer de casser la syntaxe"""
    
    rag_file = Path('rags/literature_rag/literature_rag_manager.py')
    
    if not rag_file.exists():
        print(f"❌ Fichier non trouvé: {rag_file}")
        return False
    
    print(f"🔧 Fix minimal du fichier: {rag_file}")
    
    # Lire le fichier
    with open(rag_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Créer une nouvelle sauvegarde
    backup_file = rag_file.with_suffix('.py.backup2')
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"💾 Sauvegarde créée: {backup_file}")
    
    # Fix 1 : Seuil de similarité
    if 'similarity_threshold = 0.58' in content:
        content = content.replace(
            'similarity_threshold = 0.58',
            'similarity_threshold = 0.25'
        )
        print("✅ Fix 1: Seuil réduit à 0.25")
    elif 'similarity_threshold =' in content:
        # Chercher n'importe quel seuil et le remplacer
        import re
        content = re.sub(
            r'similarity_threshold = [0-9.]+',
            'similarity_threshold = 0.25',
            content
        )
        print("✅ Fix 1: Seuil trouvé et réduit à 0.25")
    
    # Fix 2 : Filtrage de qualité (version sûre)
    if 'filtered_results = self._filter_quality_books(formatted_results)' in content:
        content = content.replace(
            'filtered_results = self._filter_quality_books(formatted_results)',
            'filtered_results = formatted_results  # Filtrage désactivé'
        )
        print("✅ Fix 2: Filtrage de qualité désactivé")
    
    # Écrire le fichier
    with open(rag_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fix minimal appliqué")
    return True

def test_syntax():
    """Test la syntaxe du fichier modifié"""
    try:
        import py_compile
        py_compile.compile('rags/literature_rag/literature_rag_manager.py', doraise=True)
        print("✅ Syntaxe correcte")
        return True
    except py_compile.PyCompileError as e:
        print(f"❌ Erreur de syntaxe: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Fix Minimal du RAG Littéraire")
    print("=" * 40)
    
    if apply_minimal_fix():
        if test_syntax():
            print("\n🎉 Fix appliqué avec succès !")
            print("💡 Testez avec: python test_agents.py")
        else:
            print("\n❌ Erreur de syntaxe détectée")
            print("💡 Restaurez avec: cp rags/literature_rag/literature_rag_manager.py.backup2 rags/literature_rag/literature_rag_manager.py")
    else:
        print("\n❌ Échec du fix")

if __name__ == "__main__":
    main()