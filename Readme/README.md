# 📚 Dual Book Advisor

**Système intelligent de recommandation de livres avec agents IA multiples**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.0+-green.svg)](https://djangoproject.com)
[![RAG](https://img.shields.io/badge/RAG-ChromaDB-purple.svg)](https://chromadb.com)
[![AI](https://img.shields.io/badge/AI-Multi--Model-orange.svg)](https://ollama.ai)

Dual Book Advisor est un système avancé de recommandation de livres utilisant l'IA et des techniques de RAG (Retrieval-Augmented Generation) pour fournir des conseils personnalisés dans trois domaines : littérature, livres techniques et manga/comics.

## 🌟 Fonctionnalités Principales

### 🤖 Deux Systèmes d'Agents IA

1. **Système Gemma** (Production) - *Simple et efficace*
   - ✅ Sélection automatique du meilleur modèle disponible  
   - ✅ Questions factuelles via Wikipedia universelle
   - ✅ Performance optimisée (5-15s de réponse)
   - ✅ Architecture simple et robuste

2. **Système LangGraph** (Avancé) - *Sophistiqué et extensible*
   - ✅ Graphe d'agents avec LangChain/LangGraph
   - ✅ Classification hybride (règles + LLM)
   - ✅ Workflows complexes et debugging avancé
   - ✅ Extensibilité maximale

### 📖 Domaines Couverts

- **📚 Littérature** : Romans, poésie, littérature classique et contemporaine
- **💻 Technique** : Livres de programmation, data science, DevOps, IA
- **🎌 Manga/Comics** : Manga japonais, BD françaises, comics américains

### 🔍 Types de Requêtes

- **Questions factuelles** : "Qui a écrit Les Fleurs du Mal ?"
- **Recommandations personnalisées** : "Livres comme Tolstoï pour débutant"
- **Exploration par domaine** : "Meilleurs livres Python 2024"

## 🚀 Installation Rapide

### 1. Prérequis

```bash
# Python 3.8+
python --version

# Ollama (pour les modèles locaux)
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve
ollama pull llama3.2:3b
ollama pull mistral:7b
ollama pull gemma2:2b
```

### 2. Installation du Projet

```bash
# Cloner le projet
git clone <url-repo>
cd dual-book-advisor

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements/requirements.txt

# Configuration optionnelle LangChain
pip install -r requirements/requirements_langchain.txt
```

### 3. Configuration Base de Données

```bash
# Setup automatique (recommandé)
python scripts/setup_database.py

# Ou setup manuel
python manage.py makemigrations
python manage.py migrate
```

### 4. Initialisation des Données RAG

```bash
# Import des données
python scripts/import_tech_books.py
python scripts/import_literature_books.py  
python scripts/import_and_index_comics.py

# Initialisation des systèmes RAG
python scripts/setup_rag.py

# Vérification
python scripts/check_books.py
```

### 5. Démarrage du Serveur

```bash
# Méthode recommandée
python start_server.py

# Ou Django standard
python manage.py runserver

# Serveur accessible sur http://127.0.0.1:8000
```

## 🌐 Endpoints et API

### Interface Web
- **🏠 Accueil** : `http://127.0.0.1:8000/`
- **👨‍💼 Admin Django** : `http://127.0.0.1:8000/admin/`
- **💬 Chat Interface** : `http://127.0.0.1:8000/chat/`

### API REST

```bash
# API de base
GET  /api/books/           # Liste des livres
POST /api/chat/            # Système Gemma (défaut)
GET  /api/chat/status/     # Statut des agents

# Système LangGraph (avancé)
POST /api/chat/langchain/              # Auto-routage intelligent
POST /api/chat/langchain/tech/         # Agent technique
POST /api/chat/langchain/literature/   # Agent littéraire  
POST /api/chat/langchain/manga/        # Agent manga/comics
GET  /api/chat/langchain/status/       # Statut LangGraph
```

### Exemples d'Utilisation

```bash
# Question factuelle
curl -X POST http://127.0.0.1:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Qui a écrit 1984?"}'

# Recommandation technique
curl -X POST http://127.0.0.1:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Livres Python pour débutant"}'

# LangGraph avancé
curl -X POST http://127.0.0.1:8000/api/chat/langchain/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN" \
  -d '{"message": "Romans similaires à Camus", "user_id": 1}'
```

## 🏗️ Architecture Technique

### Vue d'Ensemble

```
┌─────────────────────────────────────────────────┐
│                 WEB INTERFACE                   │
├─────────────────────────────────────────────────┤
│            Django REST Framework               │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌─────────────────┐    ┌─────────────────────┐ │
│  │  SYSTÈME GEMMA  │    │  SYSTÈME LANGGRAPH  │ │
│  │                 │    │                     │ │
│  │ • Simple        │    │ • Sophistiqué      │ │
│  │ • Performance   │    │ • Extensible       │ │
│  │ • Production    │    │ • Debugging        │ │
│  └─────────────────┘    └─────────────────────┘ │
│              │                      │           │
│              └──────────────────────┘           │
│                         │                       │
├─────────────────────────┼───────────────────────┤
│                         ▼                       │
│            Multi-Model Manager (Ollama)         │
│        llama3.2:3b • mistral:7b • gemma2:2b    │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│  │  Tech RAG   │ │Literature   │ │ Manga RAG   ││
│  │             │ │    RAG      │ │             ││
│  │ ChromaDB    │ │ ChromaDB +  │ │ ChromaDB    ││
│  │ Amazon Data │ │ Wikipedia   │ │ Comics Data ││
│  └─────────────┘ └─────────────┘ └─────────────┘│
└─────────────────────────────────────────────────┘
```

### Système Gemma vs LangGraph

| Aspect | Système Gemma | Système LangGraph |
|--------|---------------|-------------------|
| **Utilisation** | Production (défaut) | Développement/Avancé |
| **Complexité** | Simple (771 lignes) | Sophistiqué (2000+ lignes) |
| **Performance** | 5-15s | 10-30s |
| **LangChain** | ❌ Non | ✅ Oui |
| **LangGraph** | ❌ Non | ✅ Oui |
| **Wikipedia** | ✅ Universel | ✅ Outil dédié |
| **Extensibilité** | Limitée | Très élevée |

### Systèmes RAG

#### Tech RAG
- **Source** : Amazon Books Technical Data (10K+ livres)
- **Domaines** : Python, JavaScript, AI/ML, DevOps, etc.
- **Embeddings** : Sentence-BERT + ChromaDB
- **Métadonnées** : Prix, notes, niveau, éditeur

#### Literature RAG  
- **Source** : Books.csv + Wikipedia
- **Domaines** : Romans, poésie, littérature classique
- **Filtrage** : Exclusion automatique manga/comics
- **Questions factuelles** : Intégration Wikipedia universelle

#### Manga RAG
- **Source** : Données manga/anime/comics
- **Domaines** : Manga japonais, BD françaises, comics US
- **Métadonnées** : Genres, années, notes, statut

## 🔧 Configuration Avancée

### Variables d'Environnement

```bash
# Modèles Ollama (automatique)
PREFERRED_MODELS="llama3.2:3b,mistral:7b,gemma2:2b"

# LangChain (optionnel)
LANGCHAIN_PROVIDER=openai
LANGCHAIN_MODEL=gpt-3.5-turbo
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Base de données
DATABASE_URL=postgresql://user:pass@localhost/db

# RAG Configuration
RAG_SIMILARITY_THRESHOLD=0.5
RAG_MAX_RESULTS=5
```

### Sélection du Système d'Agents

```python
# Dans Django settings
AGENT_SYSTEM = "gemma"      # Production (défaut)
# AGENT_SYSTEM = "langgraph" # Développement avancé
```

### Performance Tuning

```bash
# Optimisation modèles Ollama
export OLLAMA_MAX_LOADED_MODELS=3
export OLLAMA_CACHE_SIZE=8GB

# Optimisation ChromaDB
export CHROMA_SERVER_CACHE_SIZE=1000
```

## 📊 Monitoring et Métriques

### Performance des Modèles

Le système track automatiquement :
- ⏱️ **Temps de réponse** moyen par modèle
- 🎯 **Score de qualité** basé sur la cohérence
- ✅ **Taux de succès** par type de requête
- 🔍 **Score de pertinence RAG**

Consultez les métriques : `agents/model_performances.json`

### Logs et Debugging

```bash
# Logs Django
tail -f logs/django.log

# Logs agents (verbose)
python manage.py runserver --debug-agents

# Tests des composants
python scripts/test_wikipedia_tool.py
python scripts/test_manga_rag.py
```

## 🧪 Tests et Vérification

### Tests des Données

```bash
# Vérifier l'import des données
python manage.py shell
>>> from apps.books.models import TechBook, LiteratureBook
>>> print(f"Livres tech: {TechBook.objects.count()}")
>>> print(f"Livres littéraires: {LiteratureBook.objects.count()}")
```

### Tests des Agents

```bash
# Test questions factuelles
python scripts/test_precise_questions.py

# Test Système Gemma
curl -X POST http://127.0.0.1:8000/api/chat/ \
  -d '{"message": "Qui a écrit Les Misérables?"}'

# Test Système LangGraph  
curl -X POST http://127.0.0.1:8000/api/chat/langchain/ \
  -d '{"message": "Livres comme Stendhal", "user_id": 1}'
```

### Tests RAG

```bash
# Vérification des index ChromaDB
python scripts/check_books.py
python scripts/verif_comics.py

# Réindexation si nécessaire
python scripts/setup_rag.py --reset
python scripts/reindex_literature_rag.py
```

## 🔧 Maintenance et Troubleshooting

### Problèmes Courants

#### 1. Modèles Ollama Non Disponibles
```bash
# Vérifier Ollama
ollama list

# Télécharger les modèles manquants
ollama pull llama3.2:3b
ollama pull mistral:7b
ollama pull gemma2:2b
```

#### 2. RAG Ne Retourne Pas de Résultats
```bash
# Vérifier les données
python scripts/check_books.py

# Réindexer si nécessaire
python scripts/setup_rag.py --reset
```

#### 3. Questions Factuelles Échouent
```bash
# Tester Wikipedia
python scripts/test_wikipedia_tool.py

# Vérifier la connexion internet pour Wikipedia
ping fr.wikipedia.org
```

#### 4. Performance Dégradée
```bash
# Nettoyer les caches
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()

# Redémarrer Ollama
pkill ollama
ollama serve
```

### Scripts de Maintenance

```bash
# Mise à jour complète des données
python scripts/setup_database.py --reset

# Optimisation des index RAG
python scripts/optimize_rag_indexes.py

# Nettoyage des logs
rm -f logs/django.log
```

## 📚 Documentation Détaillée

### Fichiers de Documentation

- **Architecture complète** : [`ARCHITECTURE_AGENTS.md`](ARCHITECTURE_AGENTS.md)
- **Configuration RAG** : [`Readme/README.md`](Readme/README.md)  
- **Setup détaillé** : [`Readme/SETUP.md`](Readme/SETUP.md)

### Structure du Projet

```
dual-book-advisor/
├── agents/                     # Systèmes d'agents IA
│   ├── ollama_gemma_manager.py    # Système Gemma (production)
│   ├── langchain_agents/          # Système LangGraph
│   └── multi_model_manager.py     # Gestion multi-modèles
├── apps/                       # Applications Django
│   ├── chat/                      # API de chat et agents
│   ├── books/                     # Modèles de données
│   └── accounts/                  # Authentification
├── rags/                       # Systèmes RAG
│   ├── tech_rag/                  # RAG technique
│   ├── literature_rag/            # RAG littéraire
│   └── manga_rag/                 # RAG manga/comics
├── scripts/                    # Scripts d'administration
└── templates/                  # Interface web
```

### Modèles de Données

```python
# Livre technique
class TechBook(models.Model):
    title = models.CharField(max_length=500)
    author = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.FloatField()
    description = models.TextField()
    
# Livre littéraire
class LiteratureBook(models.Model):
    title = models.CharField(max_length=500)
    authors = models.CharField(max_length=300)
    published_year = models.IntegerField()
    average_rating = models.FloatField()
    description = models.TextField()
```

## 🤝 Contribution

### Développement Local

```bash
# Fork et clone
git clone <your-fork>
cd dual-book-advisor

# Créer une branche feature  
git checkout -b feature/nouvelle-fonctionnalite

# Développer et tester
python manage.py test
python scripts/check_books.py

# Commit et push
git commit -m "feat: description de la fonctionnalité"
git push origin feature/nouvelle-fonctionnalite
```

### Guidelines de Développement

1. **Code Style** : Suivre PEP 8 pour Python
2. **Tests** : Ajouter des tests pour toute nouvelle fonctionnalité
3. **Documentation** : Mettre à jour la documentation si nécessaire
4. **Logs** : Utiliser le système de logging Django

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🙏 Remerciements

- **Ollama** pour les modèles LLM locaux
- **ChromaDB** pour le stockage vectoriel
- **LangChain/LangGraph** pour l'orchestration d'agents
- **Django** pour le framework web
- **Wikipedia API** pour les données factuelles

---

**🚀 Dual Book Advisor - Votre assistant IA pour découvrir votre prochain livre préféré !**

