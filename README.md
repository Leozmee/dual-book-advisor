Ordre d'exécution pour l'initialisation RAG

  1. Prérequis (une seule fois)

  # Installer les dépendances
  pip install chromadb
  sentence-transformers

  2. Import des données CSV

  # Agent Literature (1 CSV)
  python scripts/import_literatu
  re_books.py

  # Agent Tech (1 CSV) 
  python
  scripts/import_tech_books.py

  # Agent Manga/Comics (2 CSV)
  python scripts/import_and_inde
  x_comics.py

  3. Initialisation des RAG

  # Initialisation complète 
  (tous les agents)
  python scripts/setup_rag.py

  # OU par agent 
  individuellement :
  python scripts/setup_rag.py
  --tech-only
  python scripts/setup_rag.py
  --literature-only

  4. Vérification (optionnel)

  # Vérifier l'état des RAG
  python scripts/check_books.py
  python scripts/verif_comics.py

  5. Maintenance (si nécessaire)

  # Réindexation complète
  python scripts/setup_rag.py
  --reset

  # Réindexation littérature 
  uniquement
  python scripts/reindex_literat
  ure_rag.py