#!/usr/bin/env python3
"""
Script de debug pour analyser le fichier manga_data.csv
"""
import pandas as pd
import os
from pathlib import Path

def debug_manga_csv():
    """Analyse le fichier manga pour comprendre sa structure"""
    
    manga_file = Path('rags/literature_rag/data/manga_data.csv')
    
    if not manga_file.exists():
        print(f"❌ Fichier non trouvé: {manga_file}")
        return
    
    print("🔍 Analyse du fichier manga_data.csv")
    print("=" * 50)
    
    # Tentative 1: Lecture basique
    try:
        df_basic = pd.read_csv(manga_file, nrows=3)
        print(f"✅ Lecture basique réussie")
        print(f"📊 Colonnes: {list(df_basic.columns)}")
        print(f"📏 Taille: {len(df_basic)} lignes")
    except Exception as e:
        print(f"❌ Lecture basique échouée: {e}")
    
    # Tentative 2: Lecture avec paramètres robustes
    try:
        df_robust = pd.read_csv(
            manga_file, 
            nrows=5,
            encoding='utf-8',
            quotechar='"',
            escapechar='\\',
            on_bad_lines='skip'
        )
        print(f"\n✅ Lecture robuste réussie")
        print(f"📊 Colonnes: {list(df_robust.columns)}")
        
        print(f"\n📝 Échantillon de données:")
        for i, row in df_robust.iterrows():
            print(f"\nLigne {i}:")
            for col in df_robust.columns:
                value = str(row[col])[:50]
                print(f"   {col}: {value}")
                
    except Exception as e:
        print(f"❌ Lecture robuste échouée: {e}")
    
    # Tentative 3: Lecture ligne par ligne
    print(f"\n🔍 Analyse ligne par ligne des 5 premières:")
    try:
        with open(manga_file, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i >= 5:  # Arrêter après 5 lignes
                    break
                print(f"Ligne {i}: {line.strip()[:100]}...")
    except Exception as e:
        print(f"❌ Lecture ligne par ligne échouée: {e}")
    
    # Suggestions
    print(f"\n💡 Suggestions:")
    print("1. Vérifiez l'encodage du fichier (UTF-8, Latin-1, etc.)")
    print("2. Identifiez les colonnes exactes dans votre CSV")
    print("3. Nettoyez le fichier CSV manuellement si nécessaire")
    print("4. Utilisez le script d'import corrigé")

if __name__ == "__main__":
    debug_manga_csv()