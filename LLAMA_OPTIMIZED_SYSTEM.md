# 🦙 Système Optimisé Llama 3.2 3B

Application simplifiée utilisant **uniquement Llama 3.2 3B** comme modèle de recommandation, avec statistiques détaillées et monitoring des performances.

## 🎯 Pourquoi Llama 3.2 3B ?

D'après les tests, **Llama 3.2 3B** s'est révélé être le meilleur modèle pour votre application :

- ✅ **Disponible** et **stable** (contrairement à Mistral 7B)
- 🚀 **Équilibre parfait** entre performance et vitesse
- 🧠 **Excellent pour RAG** et recommandations
- 🇫🇷 **Optimisé pour le français**
- 💾 **Consommation RAM raisonnable** (~6GB)

## 📊 Caractéristiques du Modèle

| Propriété | Valeur |
|-----------|--------|
| **Nom** | Llama 3.2 3B |
| **Taille** | 3 milliards de paramètres |
| **RAM** | ~6GB |
| **Contexte** | 4096 tokens |
| **Forces** | RAG, Raisonnement, Multilingue |
| **Optimal pour** | Recommandations, Analyse, Conversations |

## 🚀 Installation et Utilisation

### 1. Installation

```bash
# Installer Ollama (si pas déjà fait)
curl -fsSL https://ollama.com/install.sh | sh

# Démarrer Ollama
ollama serve

# Installer Llama 3.2 3B
ollama pull llama3.2:3b
```

### 2. Test du Système

```bash
# Test complet du système optimisé
python scripts/test_llama_optimized.py
```

### 3. Démarrage de l'Application

```bash
# Démarrer Django
python manage.py runserver
```

## 🔧 APIs Disponibles

### 🤖 Agents Spécialisés

```bash
# Agent technique
POST /api/chat/llama/tech/
{
    "message": "Recommande-moi des livres sur Python"
}

# Agent littéraire
POST /api/chat/llama/literature/
{
    "message": "Quels romans français classiques me conseilles-tu ?"
}

# Agent manga/comics
POST /api/chat/llama/manga/
{
    "message": "Suggère-moi des manga comme Naruto"
}

# Agent routeur intelligent
POST /api/chat/llama/router/
{
    "message": "Que peux-tu me recommander ?"
}
```

### 📊 Monitoring et Statistiques

```bash
# Statut système complet
GET /api/chat/llama/status/

# Statistiques détaillées
GET /api/chat/llama/stats/

# Santé du modèle
GET /api/chat/llama/health/

# Tableau de bord complet
GET /api/chat/llama/dashboard/

# Test du modèle
POST /api/chat/llama/test/
{
    "test_type": "quick",
    "agent_type": "tech",
    "prompt": "Test personnalisé"
}
```

### ⚙️ Configuration

```bash
# Configuration actuelle
GET /api/chat/llama/config/

# Réinitialiser les statistiques
POST /api/chat/llama/reset-stats/
{
    "confirm": true
}
```

## 📈 Statistiques Collectées

Le système collecte automatiquement :

### 📊 Métriques de Performance
- **Requêtes totales** et **taux de succès**
- **Temps de réponse** (moyen, min, max)
- **Tokens générés** par requête
- **Note de performance** (A+ à D)

### 📋 Utilisation
- **Requêtes par type** d'agent (tech, literature, manga, general)
- **Usage quotidien** (30 derniers jours)
- **Tendances** d'utilisation

### 🏥 Santé du Système
- **Statut** du modèle (healthy/unhealthy)
- **Temps de réponse** aux tests
- **Recommandations** d'optimisation

## 🎯 Configuration Optimisée

### Par Type d'Agent

```python
# Configuration technique (plus déterministe)
{
    "temperature": 0.6,
    "num_predict": 600,
    "top_k": 50
}

# Configuration littéraire (plus créative)
{
    "temperature": 0.8,
    "num_predict": 500,
    "top_p": 0.95
}

# Configuration manga (équilibrée)
{
    "temperature": 0.75,
    "num_predict": 400,
    "top_k": 45
}
```

### Prompts Optimisés

Chaque agent a des prompts spécialisés :

- **Tech** : Expert français en livres techniques
- **Literature** : Critique littéraire passionné
- **Manga** : Expert français en manga/BD
- **General** : Bibliothécaire expert

## 📊 Exemple de Réponse

```json
{
    "success": true,
    "conversation_id": 123,
    "user_message": { ... },
    "agent_response": { ... },
    "llama_metrics": {
        "model_name": "llama3.2:3b",
        "success": true,
        "response_time": 12.34,
        "tokens_generated": 150,
        "agent_type": "tech"
    },
    "system_info": {
        "model": "llama3.2:3b",
        "agent_type": "tech",
        "processing_time": 12.34,
        "performance_grade": "A",
        "total_queries": 1337
    }
}
```

## 🔄 Monitoring en Temps Réel

### Tableau de Bord

Le dashboard `/api/chat/llama/dashboard/` fournit :

- **Vue d'ensemble** : Statut, note, statistiques clés
- **Statistiques détaillées** : Toutes les métriques
- **Vérification santé** : État du modèle
- **Recommandations** : Suggestions d'optimisation
- **Actions rapides** : Liens vers les tests et configurations

### Alertes Performance

Le système génère automatiquement des recommandations :

- 📈 **Taux de succès < 90%** : "Vérifiez la stabilité d'Ollama"
- ⏱️ **Temps > 30s** : "Considérez réduire num_predict"
- 🚀 **Temps < 5s** : "Très bonnes performances"
- 📊 **Peu de données** : "Effectuez plus de tests"

## 🛠️ Dépannage

### Problèmes Courants

1. **Ollama non démarré**
   ```bash
   # Vérifier
   curl http://localhost:11434/api/tags
   
   # Démarrer
   ollama serve
   ```

2. **Modèle non installé**
   ```bash
   # Installer
   ollama pull llama3.2:3b
   
   # Vérifier
   ollama list
   ```

3. **Performances lentes**
   - Réduire `num_predict` dans la configuration
   - Vérifier la charge CPU/RAM
   - Redémarrer Ollama

4. **Erreurs de mémoire**
   - Fermer les autres applications
   - Redémarrer Ollama
   - Vérifier l'espace disque

## 🔧 Développement

### Structure du Code

```
agents/
├── optimized_llama_manager.py     # Gestionnaire principal
└── langchain_agents/
    └── django_integration.py      # Intégration Django

apps/chat/
├── views_llama_agents.py          # Vues des agents
├── views_llama_stats.py           # Vues des statistiques
└── urls.py                        # URLs configurées

scripts/
└── test_llama_optimized.py        # Tests complets
```

### Configuration Django

```python
# settings/development.py
LANGCHAIN_CONFIG = {
    'provider': 'ollama',
    'model': 'llama3.2:3b',
    'llama_optimized': True,
    'collect_stats': True,
    'auto_performance_monitoring': True
}
```

## 🎯 Prochaines Étapes

1. **Démarrer l'application** : `python manage.py runserver`
2. **Tester les agents** : Utilisez les endpoints `/api/chat/llama/`
3. **Monitorer les performances** : Consultez `/api/chat/llama/dashboard/`
4. **Optimiser selon vos besoins** : Ajustez les configurations

## 📞 Support

- **Test système** : `python scripts/test_llama_optimized.py`
- **Logs** : Vérifiez les logs Django pour les erreurs
- **Santé** : `GET /api/chat/llama/health/`
- **Statistiques** : `GET /api/chat/llama/stats/`

---

**🎉 Système Llama 3.2 3B prêt à l'emploi !**

Utilisez `python scripts/test_llama_optimized.py` pour vérifier que tout fonctionne parfaitement.