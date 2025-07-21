# Architecture des Systèmes d'Agents - Dual Book Advisor

## Vue d'ensemble

Ce document détaille les deux architectures d'agents coexistant dans le système Dual Book Advisor :

1. **Système Gemma** - Architecture simple avec sélection automatique du meilleur modèle
2. **Système LangGraph/LangChain** - Architecture sophistiquée avec graphe d'agents

---

## 1. SYSTÈME GEMMA 

### 1.1 Architecture Générale

```
┌─────────────────────────────────────────────────────────┐
│                SYSTÈME GEMMA                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────┐    ┌──────────────────────────────┐│
│  │ MultiModelManager│    │     OllamaGemmaManager      ││
│  │                 │    │                              ││
│  │ • Performance   │────▶│ • Routage Simple             ││
│  │   Tracking      │    │ • RAG Direct                 ││
│  │ • Model         │    │ • Wikipedia Integration      ││
│  │   Selection     │    │ • Cover Images               ││
│  └─────────────────┘    └──────────────────────────────┘│
│           │                          │                  │
│           ▼                          ▼                  │
│  ┌─────────────────┐    ┌──────────────────────────────┐│
│  │ Best Model      │    │        Ollama Client         ││
│  │ llama3.2:3b     │    │                              ││
│  │ mistral:7b      │    │ • Direct Model Calls         ││
│  │ gemma2:2b       │    │ • Simple Prompt Engineering  ││
│  └─────────────────┘    └──────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

### 1.2 Composants Principaux

#### 1.2.1 MultiModelManager
**Fichier :** `agents/multi_model_manager.py`
**Responsabilités :**
- Gestion de plusieurs modèles Ollama simultanément
- Tracking des performances en temps réel
- Sélection automatique du meilleur modèle basée sur les métriques
- Configuration optimale par type de tâche

**Modèles supportés :**
```python
OPTIMAL_MODELS = {
    "llama3.2:3b": {"temperature": 0.7, "num_predict": 500, "top_p": 0.9},
    "mistral:7b": {"temperature": 0.6, "num_predict": 600, "top_k": 50},
    "gemma2:2b": {"temperature": 0.8, "num_predict": 400, "top_p": 0.95}
}
```

**Métriques trackées :**
- Temps de réponse moyen
- Score de qualité (basé sur la longueur et cohérence)
- Taux de succès
- Score de pertinence RAG

#### 1.2.2 OllamaGemmaManager
**Fichier :** `agents/ollama_gemma_manager.py`
**Responsabilités :**
- Interface principale du système Gemma
- Routage intelligent des requêtes
- Intégration RAG pour les trois domaines
- Gestion des questions factuelles via Wikipedia

**Workflow de routage :**
```python
def route_query(self, query: str) -> str:
    # 1. Détection factuelle (questions "qui a écrit", etc.)
    if self._detect_factual_query(query_lower):
        return self._handle_factual_query_with_gemma(query)
    
    # 2. Calcul des scores par domaine
    manga_score = sum(1 for keyword in manga_comics_keywords if keyword in query_lower)
    tech_score = sum(1 for keyword in tech_keywords if keyword in query_lower)
    literature_score = sum(1 for keyword in literature_indicators if keyword in query_lower)
    
    # 3. Routage basé sur les scores
    if manga_score > tech_score and manga_score > literature_score:
        return self.get_manga_recommendations(query)
    elif tech_score > literature_score and tech_score > manga_score:
        return self.get_tech_recommendations(query)
    else:
        return self.get_literature_recommendations(query)
```

### 1.3 Intégrations RAG

Le système Gemma intègre directement trois systèmes RAG :

#### Tech RAG
- **Source :** Amazon Books Technical Data
- **Embeddings :** Sentence-BERT
- **Index :** ChromaDB
- **Spécialités :** Livres de programmation, data science, IA

#### Literature RAG  
- **Source :** Books.csv (littérature générale)
- **Filtrages :** Exclusion automatique manga/comics
- **Spécialités :** Romans, littérature classique et contemporaine

#### Manga RAG
- **Source :** Données manga/anime/comics
- **Spécialités :** Manga japonais, BD françaises, comics américains

### 1.4 Système de Questions Factuelles

**Innovation majeure :** Intégration Wikipedia universelle

```python
def _handle_factual_query_with_gemma(self, query: str) -> str:
    # 1. RAG littéraire d'abord
    if self.literature_rag:
        results = self.literature_rag.search_books(query=title, n_results=1)
        if results:
            return self.get_factual_response(query, book_info)
    
    # 2. Wikipedia (UNIVERSEL) 
    wiki_result = self._search_wikipedia(query)
    if wiki_result and wiki_result.get('author'):
        return f"**{wiki_result['author']}** a écrit {wiki_result['title']}."
    
    # 3. Fallback intelligent
    return "📚 Je n'ai pas trouvé d'information spécifique..."
```

**Avantages :**
- ✅ Fonctionne pour toutes les œuvres sur Wikipedia
- ✅ Pas de hardcoding nécessaire
- ✅ Extraction automatique des auteurs via regex
- ✅ Support multilingue (français/anglais)

### 1.5 Sélection de Modèles

**Principe :** Le système choisit automatiquement le meilleur modèle disponible

```python
task_preferences = {
    'tech': ['mistral:7b', 'llama3.2:3b', 'gemma2:2b'],
    'literature': ['llama3.2:3b', 'mistral:7b', 'gemma2:2b'], 
    'manga': ['llama3.2:3b', 'gemma2:2b', 'mistral:7b'],
    'general': ['llama3.2:3b', 'mistral:7b', 'gemma2:2b']
}
```

**En pratique :** Actuellement `llama3.2:3b` est le plus performant avec :
- Temps de réponse : 14.3s
- Score de qualité : 93.75%
- Taux de succès : 100%

---

## 2. SYSTÈME LANGGRAPH/LANGCHAIN

### 2.1 Architecture Générale

```
┌─────────────────────────────────────────────────────────────┐
│                  SYSTÈME LANGGRAPH                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌────────────────────────────────────┐  │
│  │ User Query  │────▶│        ClassifierNode              │  │
│  └─────────────┘    │ • Rule-based classification        │  │
│                      │ • LLM-enhanced analysis           │  │
│                      │ • Confidence scoring              │  │
│                      └─────────────┬──────────────────────┘  │
│                                    │                         │
│                                    ▼                         │
│                      ┌────────────────────────────────────┐  │
│                      │          Router Node               │  │
│                      │ • Agent type selection            │  │
│                      │ • State management                 │  │
│                      └─────────────┬──────────────────────┘  │
│                                    │                         │
│                   ┌────────────────┼────────────────┐        │
│                   │                │                │        │
│                   ▼                ▼                ▼        │
│        ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│        │ TechAgent    │  │LiteratureAgent│  │ MangaAgent   │ │
│        │              │  │              │  │              │ │
│        │• tech_book_  │  │• literature_ │  │• manga_      │ │
│        │  search      │  │  book_search │  │  content_    │ │
│        │              │  │• wikipedia_  │  │  search      │ │
│        │              │  │  search      │  │              │ │
│        └──────────────┘  └──────────────┘  └──────────────┘ │
│                   │                │                │        │
│                   └────────────────┼────────────────┘        │
│                                    ▼                         │
│                      ┌────────────────────────────────────┐  │
│                      │    ResponseFormatterNode           │  │
│                      │ • Format standardization           │  │
│                      │ • Error handling                   │  │
│                      │ • Performance tracking             │  │
│                      └────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 État du Graphe (BookAdvisorState)

**Type de données partagées :**
```python
class BookAdvisorState(TypedDict):
    # Entrée utilisateur
    query: str
    user_id: int
    
    # Classification  
    classification: Optional[Dict[str, Any]]
    agent_type: str
    expanded_query: str
    requested_count: int
    confidence: float
    
    # Traitement
    agent_response: str
    agent_type_used: str
    processing_time: float
    success: bool
    
    # Sortie formatée
    final_response: str
    formatted: bool
    
    # Métadonnées et messages LangChain
    intermediate_steps: List[Any]
    error: Optional[str]
    metadata: Optional[Dict[str, Any]]
    messages: Annotated[List[BaseMessage], add_messages]
```

### 2.3 Nœuds du Graphe

#### 2.3.1 ClassifierNode
**Fichier :** `agents/langchain_agents/nodes/classifier_node.py`
**Intelligence hybride :** Règles + LLM

**Classification par règles :**
```python
def _rule_based_classification(self, query: str) -> Dict[str, Any]:
    # 1. Détection auteurs littéraires classiques (priorité haute)
    for author in self.known_authors:
        if author in query_lower:
            return {"agent_type": "literature", "confidence": 0.95}
    
    # 2. Détection manga/comics (priorité absolue)
    manga_score = sum(1 for keyword in self.manga_keywords if keyword in query_lower)
    if manga_score > 0:
        return {"agent_type": "manga", "confidence": 0.9}
    
    # 3. Détection technique
    tech_score = sum(1 for keyword in self.tech_keywords if keyword in query_lower)
    if tech_score > 0:
        return {"agent_type": "tech", "confidence": 0.8}
```

**Expansion sémantique :**
```python
semantic_expansions = {
    'tolstoy': 'Leo Tolstoy War Peace Anna Karenina Russian literature classic',
    'python': 'Python programming language development beginner advanced',
    'naruto': 'Naruto ninja village hidden leaf Uzumaki Sasuke Sakura action'
}
```

#### 2.3.2 Agent Nodes

**Structure commune :**
```python
class BaseAgentNode:
    def __init__(self, llm, agent_type: str):
        self.llm = llm
        self.agent_type = agent_type
        self.tool = RAGToolsFactory.get_tool_by_agent_type(agent_type)
        self.prompt = self._create_prompt()
        self.agent_executor = self._create_agent_executor()
```

**TechAgentNode :**
- **Outil :** `tech_book_search` (Amazon Books RAG)
- **Spécialité :** Livres techniques, programmation
- **Format de sortie :** Recommandations avec notes, prix, niveau

**LiteratureAgentNode :**
- **Outils :** `literature_book_search` + `wikipedia_search`
- **Spécialité :** Questions d'auteur + recommandations littéraires
- **Innovation :** Dual-tool approach (RAG + Wikipedia)

**MangaAgentNode :**
- **Outil :** `manga_content_search` 
- **Base de connaissances intégrée :** Auteurs manga populaires
- **Spécialité :** Manga, anime, comics, BD

### 2.4 Système d'Outils (RAG Tools)

**Architecture modulaire :**
```python
class RAGToolsFactory:
    @staticmethod
    def get_tool_by_agent_type(agent_type: str) -> BaseTool:
        if agent_type == "tech":
            return RAGToolsFactory.get_tech_tool()
        elif agent_type == "literature": 
            return RAGToolsFactory.get_literature_tool()
        elif agent_type == "manga":
            return RAGToolsFactory.get_manga_tool()
```

**WikipediaSearchTool (spécial) :**
```python
class WikipediaSearchTool(BaseTool):
    name: str = "wikipedia_search"
    description: str = """
    Recherche des informations sur Wikipedia pour des auteurs, œuvres littéraires.
    Utilise cet outil UNIQUEMENT quand :
    - Le RAG littéraire ne trouve pas d'information sur un auteur
    - L'utilisateur demande des informations biographiques
    - Il faut du contexte historique ou culturel
    """
```

### 2.5 LLM et Intégrations

**Providers supportés :**
- OpenAI (GPT-3.5-turbo, GPT-4)
- Ollama (modèles locaux)
- Anthropic (Claude)

**Auto-sélection pour Ollama :**
```python
if self.llm_provider.lower() == "ollama":
    best_model = self.multi_model_manager.get_best_model_for_task("general")
    if best_model:
        self.model_name = best_model
```

---

## 3. COMPARAISON DES DEUX SYSTÈMES

### 3.1 Philosophie de Design

| Aspect | Système Gemma | Système LangGraph |
|--------|---------------|-------------------|
| **Approche** | Simple, direct, efficace | Sophistiqué, modulaire, extensible |
| **Complexité** | Faible (771 lignes) | Élevée (2000+ lignes) |
| **Maintenance** | Simple | Complexe |
| **Extensibilité** | Limitée | Très élevée |

### 3.2 Performance 

| Métrique | Système Gemma | Système LangGraph |
|----------|---------------|-------------------|
| **Temps de réponse** | 5-15s (optimisé) | 10-30s (overhead) |
| **Consommation mémoire** | Faible | Élevée (framework) |
| **Précision routage** | 85-90% | 90-95% |
| **Gestion erreurs** | Basique | Sophistiquée |

### 3.3 Fonctionnalités

#### Questions Factuelles
- **Gemma :** Wikipedia universelle + RAG fallback
- **LangGraph :** Dual-tool (RAG + Wikipedia) avec prompts sophistiqués

#### Sélection de Modèles
- **Gemma :** Automatique basée sur performance tracking
- **LangGraph :** Manuelle ou héritée du MultiModelManager

#### Intégration RAG
- **Gemma :** Directe, trois systèmes séparés
- **LangGraph :** Via outils LangChain, abstraction complète

### 3.4 Architecture Technique

#### Dépendances
**Système Gemma :**
```python
# Dépendances minimales
import ollama
import requests  
import wikipedia
from typing import List, Dict, Any
```

**Système LangGraph :**
```python
# Écosystème LangChain complet
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain.agents import create_openai_tools_agent, AgentExecutor
```

#### Patterns de Code

**Gemma - Pattern Direct :**
```python
def get_recommendations(self, query: str) -> str:
    # 1. Route directly
    if self._detect_factual_query(query):
        return self._handle_factual_query_with_gemma(query)
    
    # 2. Simple scoring
    scores = self._calculate_domain_scores(query)
    
    # 3. Direct execution
    return self._execute_domain_logic(query, best_domain)
```

**LangGraph - Pattern State Machine :**
```python
def build_graph(self) -> StateGraph:
    graph = StateGraph(BookAdvisorState)
    
    # Nodes
    graph.add_node("classifier", self.classifier_node)
    graph.add_node("router", RouterNode())
    graph.add_node("tech_agent", self.agent_nodes["tech"])
    graph.add_node("literature_agent", self.agent_nodes["literature"]) 
    graph.add_node("manga_agent", self.agent_nodes["manga"])
    graph.add_node("formatter", ResponseFormatterNode())
    
    # Edges with conditional logic
    graph.add_conditional_edges("router", self._route_to_agent)
    
    return graph
```

---

## 4. UTILISATION ACTUELLE

### 4.1 Interface Web

**Découverte importante :** L'interface web utilise actuellement le **Système Gemma**

**Evidence dans les logs :**
```
🎯 Agent Coordinateur
🤖 **Recommandations General (Llama 3.2 3B)**
⚡ Traitement: 10.62s | Agent: general | Tokens: 168 | Grade: A
⚡ LangChain Auto-Router - 34.31s
```

### 4.2 Points d'Entrée

**Système Gemma :**
- `apps/chat/views.py` → `SimpleAgentManager` → `OllamaGemmaManager`

**Système LangGraph :**
- `apps/chat/views_langchain.py` → `BookAdvisorGraphManager`

### 4.3 Configuration Active

**Modèle utilisé :** `llama3.2:3b` (sélectionné automatiquement)
**Raison :** Meilleures performances globales selon les métriques

---

## 5. RECOMMANDATIONS

### 5.1 Pour l'Utilisateur Final

**Utiliser Système Gemma quand :**
- ✅ Performance prime sur sophistication
- ✅ Questions factuelles simples
- ✅ Recommandations directes
- ✅ Déploiement simple

**Utiliser Système LangGraph quand :**
- ✅ Workflows complexes nécessaires
- ✅ Extensibilité future importante
- ✅ Intégration avec écosystème LangChain
- ✅ Debugging approfondi requis

### 5.2 Migration Strategy

**Pour passage complet à LangGraph :**
1. Migrer la logique Wikipedia du système Gemma
2. Implémenter le multi-model management
3. Optimiser les prompts pour réduire la latence
4. Tester les performances end-to-end

**Pour optimisation système Gemma :**
1. Ajouter plus de métriques de performance
2. Implémenter le caching intelligent
3. Améliorer la détection contextuelle
4. Ajouter support pour plus de providers LLM

---

## 6. CONCLUSION

Les deux systèmes représentent deux philosophies différentes :

- **Système Gemma** : "Simple mais efficace" - Optimal pour la production
- **Système LangGraph** : "Sophistiqué et extensible" - Optimal pour l'évolution

**Actuellement**, le système Gemma domine grâce à sa performance et simplicité, mais le système LangGraph offre des possibilités d'extension bien supérieures pour l'avenir.

**Paradoxe actuel :** Le "système Gemma" utilise en réalité le modèle `llama3.2:3b` car il s'avère plus performant que `gemma2:2b` - démonstration parfaite de l'intelligence du système de sélection automatique !

---

*Document généré le $(date) - Architecture Dual Book Advisor*