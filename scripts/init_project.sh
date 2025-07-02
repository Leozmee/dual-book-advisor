#!/bin/bash
# scripts/init_project.sh - Script d'initialisation complète du projet

echo "🚀 Initialisation du projet Duo Book Advisor..."

# 1. Création de la structure de dossiers
echo "📁 Création de la structure de dossiers..."

# Dossiers principaux
mkdir -p agents/{prompts,config}
mkdir -p rags/{tech_rag/{data,chroma_db,embeddings,processors,scripts},literature_rag/{data,chroma_db,embeddings,processors,scripts},shared}
mkdir -p api/{models,routes,middleware,services,utils}
mkdir -p tests/{test_agents,test_rags,test_api,test_web}
mkdir -p scripts
mkdir -p docs
mkdir -p config
mkdir -p deployment/{docker,kubernetes,scripts}

# Dossiers RAG spécifiques
mkdir -p rags/tech_rag/data/tech_reviews
mkdir -p rags/literature_rag/data/{goodreads_reviews,additional_sources}

# 2. Création des fichiers __init__.py
echo "🐍 Création des fichiers __init__.py..."

find agents rags api tests -type d -exec touch {}/__init__.py \;

# 3. Installation de l'environnement virtuel
echo "🔧 Création de l'environnement virtuel..."

python -m venv venv

# Instructions d'activation selon l'OS
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "💡 Pour activer l'environnement virtuel (Windows): venv\\Scripts\\activate"
else
    echo "💡 Pour activer l'environnement virtuel (Linux/Mac): source venv/bin/activate"
fi

echo "📦 Activation de l'environnement virtuel et installation des dépendances..."

# Activation selon l'OS
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# 4. Installation des dépendances de base
echo "📦 Installation des dépendances Python..."

pip install --upgrade pip

# Dépendances principales
pip install django==4.2.7
pip install djangorestframework==3.14.0
pip install python-decouple==3.8
pip install psycopg2-binary==2.9.9

# Dépendances AI/ML
pip install transformers==4.35.2
pip install sentence-transformers==2.2.2
pip install torch==2.1.1
pip install chromadb==0.4.17
pip install datasets==2.14.6

# Dépendances API
pip install fastapi==0.104.1
pip install uvicorn==0.24.0
pip install pydantic==2.5.0

# Dépendances utilitaires
pip install pandas==2.1.3
pip install numpy==1.25.2
pip install python-dotenv==1.0.0
pip install celery==5.3.4

# Dépendances développement
pip install pytest==7.4.3
pip install pytest-django==4.7.0
pip install black==23.11.0
pip install flake8==6.1.0

# 5. Création du projet Django
echo "🌐 Création du projet Django..."

# Créer le projet Django dans le dossier web/
django-admin startproject config web
cd web

# Réorganiser pour avoir la structure souhaitée
mkdir -p apps
mv config/settings.py config/settings/base.py
mkdir -p config/settings
touch config/settings/__init__.py

# 6. Création des applications Django
echo "📱 Création des applications Django..."

python manage.py startapp accounts apps/accounts
python manage.py startapp chat apps/chat  
python manage.py startapp books apps/books
python manage.py startapp dashboard apps/dashboard

# Retour au répertoire racine
cd ..

# 7. Création des fichiers de configuration
echo "⚙️ Création des fichiers de configuration..."

# requirements.txt
cat > requirements.txt << EOL
# Django et Web
django==4.2.7
djangorestframework==3.14.0
python-decouple==3.8
psycopg2-binary==2.9.9
django-cors-headers==4.3.1
channels==4.0.0
redis==5.0.1

# AI/ML et RAG
transformers==4.35.2
sentence-transformers==2.2.2
torch==2.1.1
chromadb==0.4.17
datasets==2.14.6
numpy==1.25.2

# API
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0

# Utilitaires
pandas==2.1.3
python-dotenv==1.0.0
celery==5.3.4
requests==2.31.0

# Développement
pytest==7.4.3
pytest-django==4.7.0
black==23.11.0
flake8==6.1.0
EOL

# .env.example
cat > .env.example << EOL
# Configuration Django
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de données
DATABASE_URL=postgresql://user:password@localhost:5432/duo_book_advisor

# Configuration API
API_HOST=localhost
API_PORT=8001

# Configuration agents/modèles
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
LLM_MODEL=google/flan-t5-base
DEVICE=auto

# Configuration ChromaDB
CHROMA_DB_PATH=./rags/
TECH_COLLECTION_NAME=tech_books_collection
LITERATURE_COLLECTION_NAME=literature_books_collection

# Configuration Redis (pour Celery/WebSocket)
REDIS_URL=redis://localhost:6379/0

# Logging
LOG_LEVEL=INFO
EOL

# .gitignore
cat > .gitignore << EOL
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
media/
staticfiles/

# Environnement
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# AI/ML Models
models/
*.bin
*.safetensors
*.h5

# ChromaDB
rags/*/chroma_db/
rags/*/embeddings/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Docker
docker-compose.override.yml

# Logs
logs/
*.log

# Données sensibles
rags/*/data/*.csv
!rags/*/data/.gitkeep
EOL

# docker-compose.yml
cat > docker-compose.yml << EOL
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: duo_book_advisor
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  web:
    build: .
    command: python web/manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    environment:
      - DEBUG=1
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/duo_book_advisor
      - REDIS_URL=redis://redis:6379/0

  api:
    build: .
    command: uvicorn api.app:app --host 0.0.0.0 --port 8001 --reload
    volumes:
      - .:/app
    ports:
      - "8001:8001"
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
EOL

# 8. Création des fichiers .gitkeep pour les dossiers vides
echo "📝 Création des fichiers .gitkeep..."

touch rags/tech_rag/data/.gitkeep
touch rags/literature_rag/data/.gitkeep
touch rags/tech_rag/chroma_db/.gitkeep
touch rags/literature_rag/chroma_db/.gitkeep
touch web/static/.gitkeep
touch web/media/.gitkeep

# 9. Message final
echo ""
echo "✅ Projet initialisé avec succès !"
echo ""
echo "📋 Prochaines étapes :"
echo "1. Activer l'environnement virtuel :"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "   venv\\Scripts\\activate"
else
    echo "   source venv/bin/activate"
fi
echo "2. Installer les dépendances : pip install -r requirements.txt"
echo "3. Copier .env.example vers .env et configurer"
echo "4. Placer tes datasets CSV dans rags/tech_rag/data/ et rags/literature_rag/data/"
echo "5. Lancer les migrations Django : cd web && python manage.py migrate"
echo "6. Créer un superuser : python manage.py createsuperuser"
echo ""
echo "🎯 Structure du projet créée dans : $(pwd)"