#!/usr/bin/env python3
"""
Fix pour le problème de télémétrie ChromaDB
"""
import os
import sys
import django
from pathlib import Path

# Configuration Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# DÉSACTIVER LA TÉLÉMÉTRIE CHROMADB AVANT L'IMPORT
os.environ['ANONYMIZED_TELEMETRY'] = 'False'
os.environ['CHROMA_SERVER_TELEMETRY'] = 'False'

django.setup()

import pandas as pd
import ast
from apps.books.models import LiteratureBook


def clean_tags_column(tags_str):
    """Nettoie la colonne tags qui contient des listes Python"""
    if not tags_str or tags_str == '':
        return 'Manga'
    
    try:
        # Si c'est déjà une liste Python en string, l'évaluer
        if tags_str.startswith('[') and tags_str.endswith(']'):
            # Utiliser ast.literal_eval pour sécurité
            tags_list = ast.literal_eval(tags_str)
            return ', '.join(tags_list)
        else:
            # Si c'est déjà une string simple
            return str(tags_str)
    except:
        # En cas d'erreur, nettoyer manuellement
        clean_tags = tags_str.replace('[', '').replace(']', '').replace("'", "").replace('"', '')
        return clean_tags


def import_manga_simple():
    """Import manga simplifié sans réindexation automatique"""
    print("📚 Import manga simplifié (sans ChromaDB)...")
    
    manga_file = BASE_DIR / 'rags' / 'literature_rag' / 'data' / 'manga_data.csv'
    
    if not manga_file.exists():
        print(f"❌ Fichier non trouvé: {manga_file}")
        return False
    
    imported_count = 0
    errors = []
    
    try:
        # Lire le CSV
        manga_df = pd.read_csv(
            manga_file,
            encoding='utf-8',
            quotechar='"',
            escapechar='\\',
            on_bad_lines='skip'
        )
        
        print(f"📊 {len(manga_df)} mangas à traiter")
        
        # Nettoyer les données
        manga_df = manga_df.fillna('')
        
        for index, row in manga_df.iterrows():
            try:
                # Extraction basique et sûre
                title = str(row['title']).strip().replace('"', "'")[:500]
                description = str(row['description']).strip().replace('"', "'")[:1000]
                
                if len(title) < 2:
                    title = f"Manga {index + 1}"
                
                # Rating simple
                rating = None
                try:
                    if row['rating']:
                        rating_val = float(row['rating'])
                        rating = min(rating_val, 5.0)  # Max 5
                except:
                    pass
                
                # Année simple
                year = None
                try:
                    if row['year']:
                        year = int(float(row['year']))
                        if not (1900 <= year <= 2024):
                            year = None
                except:
                    pass
                
                # Tags nettoyés
                tags_clean = clean_tags_column(str(row['tags']))
                categories = f"Manga, {tags_clean}"[:200]
                
                # ISBN unique
                fake_isbn = f"978-M-{str(index).zfill(6)}-{abs(hash(title)) % 1000:03d}"
                
                # Vérifier existence
                if LiteratureBook.objects.filter(title__iexact=title).exists():
                    continue
                
                # Créer l'entrée
                manga_book = LiteratureBook(
                    isbn13=fake_isbn,
                    title=title,
                    authors='Auteur Manga',
                    description=description or "Description non disponible",
                    categories=categories,
                    average_rating=rating,
                    published_year=year,
                    themes=f"Manga, Japanese",
                    reading_difficulty='moderate',
                    booktitle_alt=f"Manga: {title[:100]}",
                    author_alt='Manga Author',
                )
                
                manga_book.save()
                imported_count += 1
                
                if imported_count % 20 == 0:
                    print(f"📚 {imported_count} mangas importés...")
                    
            except Exception as e:
                errors.append(f"Ligne {index}: {str(e)[:100]}")
                continue
        
        print(f"\n✅ Import terminé:")
        print(f"   📚 Mangas importés: {imported_count}")
        print(f"   ❌ Erreurs: {len(errors)}")
        
        # Stats finales
        total_manga = LiteratureBook.objects.filter(categories__icontains='Manga').count()
        print(f"   📊 Total mangas en base: {total_manga}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        return False


def reindex_manually():
    """Réindexation manuelle après import"""
    print("\n🔄 Réindexation manuelle du RAG...")
    
    try:
        # Importer ChromaDB avec télémétrie désactivée
        from rags.literature_rag.literature_rag_manager import LiteratureRAGManager
        
        lit_rag = LiteratureRAGManager()
        
        print("📋 Suppression de l'ancien index...")
        # Force reset
        lit_rag.index_all_books(reset=True)
        
        # Vérifier les stats
        stats = lit_rag.get_stats()
        print(f"📊 Statistiques après réindexation:")
        print(f"   📚 Livres indexés: {stats.get('indexed_books', 0)}")
        print(f"   🗄️ Total en base: {stats.get('total_books_in_db', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur réindexation: {e}")
        print("💡 Vous pouvez réindexer plus tard avec: python scripts/setup_rag.py")
        return False


def main():
    """Fonction principale"""
    print("🚀 Import Manga avec Fix ChromaDB")
    print("=" * 45)
    
    # Étape 1: Import simple
    if import_manga_simple():
        print("\n✅ Import manga réussi !")
        
        # Étape 2: Demander si on veut réindexer maintenant
        reindex_choice = input("\n🔄 Voulez-vous réindexer le RAG maintenant ? (y/n): ").lower()
        
        if reindex_choice in ['y', 'yes', 'o', 'oui']:
            reindex_manually()
        else:
            print("💡 Vous pouvez réindexer plus tard avec:")
            print("   python scripts/setup_rag.py --literature-only")
        
        print("\n🎉 Processus terminé !")
        print("💡 Prochaines étapes:")
        print("1. Corriger l'agent technique (modification manuelle)")
        print("2. Optimiser le RAG littéraire")
        print("3. Tester les agents")
        
    else:
        print("\n❌ Échec de l'import")


if __name__ == "__main__":
    main()