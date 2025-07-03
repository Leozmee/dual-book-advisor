# 🚀 Guide de Démarrage - Dual Book Advisor

## 📋 Installation

### 1. **Dépendances Principales**
```bash
pip install django djangorestframework django-cors-headers
pip install chromadb sentence-transformers pandas
```

### 2. **Dépendances LangChain (Optionnel)**
```bash
pip install -r requirements/requirements_langchain.txt
```

### 3. **Configuration de la Base de Données**
```bash
# PostgreSQL (recommandé)
pip install psycopg2-binary

# Ou SQLite (par défaut)
# Aucune installation supplémentaire nécessaire
```

## 🗄️ Configuration Base de Données

### **Option 1: Setup Automatique**
```bash
python scripts/setup_database.py
```

### **Option 2: Setup Manuel**
```bash
python manage.py makemigrations
python manage.py migrate
python scripts/import_tech_books.py
python scripts/import_literature_books.py
python scripts/setup_rag.py
```

## 🚀 Démarrage du Serveur

### **Option 1: Script Personnalisé (Recommandé)**
```bash
python start_server.py [host:port]

# Exemples
python start_server.py              # 127.0.0.1:8000
python start_server.py 8080         # 127.0.0.1:8080  
python start_server.py 0.0.0.0:8000 # Accessible depuis le réseau
```

### **Option 2: Django Standard**
```bash
python manage.py runserver [host:port]
```

## 🌐 URLs Disponibles

Une fois le serveur lancé, vous aurez accès à :

### **Interface Web**
- **Accueil** : http://127.0.0.1:8000/
- **Admin Django** : http://127.0.0.1:8000/admin/

### **API REST**
- **Books API** : http://127.0.0.1:8000/api/books/
- **Chat API** : http://127.0.0.1:8000/api/chat/
- **Auth API** : http://127.0.0.1:8000/api/auth/

### **LangChain Agents** 🤖
- **Routage Auto** : `POST /api/chat/langchain/`
- **Agent Tech** : `POST /api/chat/langchain/tech/`
- **Agent Littéraire** : `POST /api/chat/langchain/literature/`
- **Statut** : `GET /api/chat/langchain/status/`

## 🔑 Configuration LangChain

### **Variables d'Environnement**
```bash
# Provider (openai, anthropic, huggingface)
export LANGCHAIN_PROVIDER=openai
export LANGCHAIN_MODEL=gpt-3.5-turbo

# Clés API
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
```

### **Test des Agents**
```bash
# Test avec curl
curl -X POST http://127.0.0.1:8000/api/chat/langchain/tech/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN" \
  -d '{"message": "je veux apprendre JavaScript"}'
```

## 🧪 Tests et Vérification

### **Test des Données**
```bash
python manage.py shell
>>> from apps.books.models import TechBook, LiteratureBook
>>> print(f"Livres tech: {TechBook.objects.count()}")
>>> print(f"Livres littéraires: {LiteratureBook.objects.count()}")
```

### **Test RAG**
```bash
python scripts/setup_rag.py
```

## 🔧 Résolution de Problèmes

### **Erreur: Module Django Non Trouvé**
```bash
pip install django
# Ou activer votre environnement virtuel
source venv/bin/activate
```

### **Erreur: Base de Données**
```bash
python manage.py migrate
```

### **Agents LangChain Non Disponibles**
- Vérifiez que les clés API sont configurées
- Installez les dépendances LangChain
- Vérifiez les logs du serveur

### **Aucune Recommandation Trouvée**
- Exécutez `python scripts/setup_rag.py`
- Vérifiez que les données sont importées
- Le seuil de similarité est configuré à 0.5

## 📚 Documentation

- **Architecture LangChain** : `README_LANGCHAIN.md`
- **Configuration RAG** : `config/settings/base.py`
- **Modèles Django** : `apps/*/models.py`

## 🎯 Premiers Pas

1. **Lancez le serveur** : `python start_server.py`
2. **Créez un superuser** : `python manage.py createsuperuser`
3. **Accédez à l'admin** : http://127.0.0.1:8000/admin/
4. **Testez les agents** : Utilisez l'API LangChain
5. **Consultez la doc** : `README_LANGCHAIN.md`