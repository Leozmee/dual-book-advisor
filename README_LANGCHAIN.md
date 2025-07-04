# Architecture LangChain - Dual Book Advisor

## 🏗️ Architecture Implémentée

### **Agents Disponibles**

1. **🤖 Agent de Routage** (`RouterAgent`)
   - Analyse les requêtes et dirige vers l'agent approprié
   - Classification automatique : TECH, LITERATURE, ou GENERAL

2. **🔧 Agent Technique** (`BookRecommendationAgent` - tech)
   - Spécialisé dans les livres de programmation et technologies
   - Utilise le `TechRAGManager` pour les recherches

3. **📚 Agent Littéraire** (`BookRecommendationAgent` - literature)
   - Spécialisé dans les romans et littérature
   - Utilise le `LiteratureRAGManager` pour les recherches

## 🚀 Endpoints API

### **Chat LangChain Général**
```
POST /api/chat/langchain/
{
    "message": "je veux apprendre le JavaScript",
    "agent_type": "router"  // optionnel: router, tech, literature
}
```

### **Agent Technique Direct**
```
POST /api/chat/langchain/tech/
{
    "message": "j'aimerais apprendre le javascript et je suis fan des fleurs"
}
```

### **Agent Littéraire Direct**
```
POST /api/chat/langchain/literature/
{
    "message": "j'ai fini harry potter, j'aimerais commencer un livre similaire"
}
```

### **Statut des Agents**
```
GET /api/chat/langchain/status/
```

## ⚙️ Configuration

### **Variables d'Environnement**
```bash
# Provider LLM (openai, anthropic, huggingface)
export LANGCHAIN_PROVIDER=openai
export LANGCHAIN_MODEL=gpt-3.5-turbo

# Clés API
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
```

### **Installation des Dépendances**
```bash
pip install -r requirements/requirements_langchain.txt
```

## 🔧 Corrections Apportées

### **1. Seuil de Similarité**
- **Avant**: 0.7 (trop élevé)
- **Après**: 0.5 (équilibré)
- **Impact**: Meilleure détection des livres pertinents

### **2. Amélioration des Requêtes**
- **Problème**: "j'aime la bolognaise" → mapping technique forcé
- **Solution**: Détection intelligente des intentions techniques vs mentions casual
- **Exemple**: "j'aime les fleurs" reste inchangé, "programmation web" → mapping technique

## 🧪 Tests

### **Test du Fix de Similarité**
```bash
python test_similarity_fix.py
```

### **Tests d'Exemple**

**Requêtes Techniques:**
- ✅ "j'aimerais apprendre le javascript" → Recommandations JavaScript
- ✅ "JavaScript" → Livres JavaScript pertinents
- ✅ "développement web" → Livres web development

**Requêtes Littéraires:**
- ✅ "j'ai fini harry potter" → Livres fantasy similaires
- ✅ "romans fantastiques" → Fiction fantasy
- ✅ "young adult fiction" → Littérature jeunesse

## 🎯 Utilisation des Agents

### **Agent de Routage (Recommandé)**
```python
from agents import LangChainAgentManager

manager = LangChainAgentManager()
response = manager.get_agent_response("je veux apprendre Python", "router")
```

### **Agent Spécifique**
```python
# Agent technique direct
tech_response = manager.get_agent_response("JavaScript pour débutants", "tech")

# Agent littéraire direct  
lit_response = manager.get_agent_response("romans comme Harry Potter", "literature")
```

## 📊 Flux de Traitement

```
Requête Utilisateur
      ↓
Agent de Routage (LLM)
      ↓
Classification: TECH | LITERATURE | GENERAL
      ↓
Agent Spécialisé
      ↓
RAG Manager (recherche sémantique)
      ↓
ChromaDB (similarité vectorielle)
      ↓
Réponse Structurée avec Recommandations
```

## ✨ Avantages de l'Architecture

1. **🎯 Routing Intelligent**: Détection automatique du type de requête
2. **🔧 Spécialisation**: Agents optimisés pour chaque domaine
3. **🧠 RAG Intégré**: Recherche sémantique dans les bases de livres
4. **⚡ Performance**: Seuil de similarité optimisé
5. **🔄 Extensible**: Facile d'ajouter de nouveaux agents
6. **🛡️ Robuste**: Gestion d'erreurs et fallbacks

## 🚧 Prochaines Étapes

1. **Interface Web**: Frontend pour interagir avec les agents
2. **Personnalisation**: Intégration des profils utilisateurs
3. **Mémorisation**: Historique des conversations
4. **Analytics**: Tracking des performances et feedback
5. **Multi-modal**: Support d'images et documents