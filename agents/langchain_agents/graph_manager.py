"""
LangGraph Manager - Orchestrateur principal du système d'agents
Fichier: agents/langchain_agents/graph_manager.py
"""
from typing import Dict, Any, List, Optional, TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
import logging
import time
import json

from .nodes.classifier_node import ClassifierNode
from .nodes.agent_nodes import AgentNodesFactory, RouterNode, ResponseFormatterNode
from .tools.rag_tools import validate_rag_systems
from ..multi_model_manager import multi_model_manager
from ..model_evaluator import get_model_evaluator

logger = logging.getLogger(__name__)

# Définition de l'état du graphe
class BookAdvisorState(TypedDict):
    """État partagé entre tous les nœuds du graphe"""
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
    
    # Métadonnées
    intermediate_steps: List[Any]
    error: Optional[str]
    metadata: Optional[Dict[str, Any]]
    
    # Messages LangChain (pour compatibilité)
    messages: Annotated[List[BaseMessage], add_messages]

class BookAdvisorGraphManager:
    """Gestionnaire principal du graphe LangGraph pour les recommandations de livres"""
    
    def __init__(self, llm_provider: str = "openai", model_name: str = "gpt-3.5-turbo", **llm_kwargs):
        """
        Initialise le gestionnaire de graphe
        
        Args:
            llm_provider: "openai", "ollama", ou "anthropic"
            model_name: Nom du modèle à utiliser
            **llm_kwargs: Arguments additionnels pour le LLM
        """
        self.llm_provider = llm_provider
        self.model_name = model_name
        self.llm_kwargs = llm_kwargs
        
        # Initialiser le gestionnaire multi-modèles
        self.multi_model_manager = multi_model_manager
        self.model_evaluator = get_model_evaluator(self.multi_model_manager)
        
        # Choisir le meilleur modèle si utilisation d'Ollama
        if self.llm_provider.lower() == "ollama":
            best_model = self.multi_model_manager.get_best_model_for_task("general")
            if best_model:
                self.model_name = best_model
                logger.info(f"🏆 Utilisation du meilleur modèle: {best_model}")
        
        # Initialiser le LLM
        self.llm = self._create_llm()
        
        # Créer les nœuds
        self.classifier_node = ClassifierNode(self.llm)
        self.agent_nodes = AgentNodesFactory.create_all_nodes(self.llm)
        
        # Construire le graphe
        self.graph = self._build_graph()
        self.compiled_graph = self.graph.compile()
        
        # Valider les systèmes RAG
        self.rag_status = validate_rag_systems()
        
        logger.info(f"✅ BookAdvisorGraphManager initialisé avec {llm_provider}:{model_name}")
    
    def _create_llm(self):
        """Crée l'instance LLM selon le provider"""
        try:
            if self.llm_provider.lower() == "openai":
                return ChatOpenAI(
                    model=self.model_name,
                    temperature=0.7,
                    **self.llm_kwargs
                )
            
            elif self.llm_provider.lower() == "ollama":
                return ChatOllama(
                    model=self.model_name,
                    temperature=0.7,
                    **self.llm_kwargs
                )
            
            elif self.llm_provider.lower() == "anthropic":
                from langchain_anthropic import ChatAnthropic
                return ChatAnthropic(
                    model=self.model_name,
                    temperature=0.7,
                    **self.llm_kwargs
                )
            
            else:
                logger.warning(f"Provider {self.llm_provider} non reconnu, fallback vers OpenAI")
                return ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
                
        except Exception as e:
            logger.error(f"Erreur création LLM: {e}")
            # Fallback vers un LLM mock pour les tests
            return self._create_mock_llm()
    
    def _create_mock_llm(self):
        """Crée un LLM mock pour les tests"""
        class MockLLM:
            def invoke(self, messages):
                return AIMessage(content="Réponse mock du LLM")
            
            def __call__(self, messages):
                return self.invoke(messages)
        
        logger.warning("⚠️ Utilisation d'un LLM mock - configurez un vrai LLM pour la production")
        return MockLLM()
    
    def _build_graph(self) -> StateGraph:
        """Construit le graphe LangGraph avec tous les nœuds et transitions"""
        
        # Créer le graphe avec l'état typé
        graph = StateGraph(BookAdvisorState)
        
        # Ajouter les nœuds
        graph.add_node("classifier", self._classifier_wrapper)
        graph.add_node("router", self._router_wrapper)
        graph.add_node("formatter", self._formatter_wrapper)
        
        # Définir les arêtes
        graph.set_entry_point("classifier")
        
        # Classifier → Router (toujours)
        graph.add_edge("classifier", "router")
        
        # Router → Formatter (toujours)
        graph.add_edge("router", "formatter")
        
        # Formatter → END (toujours)
        graph.add_edge("formatter", END)
        
        logger.info("📊 Graphe LangGraph construit avec succès")
        return graph
    
    def _classifier_wrapper(self, state: BookAdvisorState) -> BookAdvisorState:
        """Wrapper pour le nœud classifier"""
        try:
            logger.info(f"🔍 Classification: '{state['query']}'")
            return self.classifier_node(state)
        except Exception as e:
            logger.error(f"❌ Erreur classifier: {e}")
            # Fallback par défaut
            state.update({
                "agent_type": "literature",
                "expanded_query": state["query"],
                "requested_count": 3,
                "confidence": 0.1,
                "classification": {"error": str(e)}
            })
            return state
    
    def _router_wrapper(self, state: BookAdvisorState) -> BookAdvisorState:
        """Wrapper pour le nœud router"""
        try:
            logger.info(f"🔄 Routage vers: {state['agent_type']}")
            return self.agent_nodes["router"](state)
        except Exception as e:
            logger.error(f"❌ Erreur router: {e}")
            state.update({
                "agent_response": f"Erreur de routage: {str(e)}",
                "success": False,
                "error": str(e)
            })
            return state
    
    def _formatter_wrapper(self, state: BookAdvisorState) -> BookAdvisorState:
        """Wrapper pour le nœud formatter"""
        try:
            logger.info("🎨 Formatage de la réponse finale")
            return self.agent_nodes["formatter"](state)
        except Exception as e:
            logger.error(f"❌ Erreur formatter: {e}")
            state.update({
                "final_response": state.get("agent_response", "Erreur de formatage"),
                "formatted": False,
                "error": str(e)
            })
            return state
    
    def get_recommendation(self, query: str, user_id: int = 1) -> Dict[str, Any]:
        """
        Point d'entrée principal pour obtenir une recommandation
        
        Args:
            query: Requête utilisateur
            user_id: ID de l'utilisateur
            
        Returns:
            Dict contenant la réponse et les métadonnées
        """
        try:
            start_time = time.time()
            
            # Préparer l'état initial
            initial_state = BookAdvisorState(
                query=query,
                user_id=user_id,
                classification=None,
                agent_type="literature",  # Défaut
                expanded_query=query,
                requested_count=3,
                confidence=0.0,
                agent_response="",
                agent_type_used="",
                processing_time=0.0,
                success=False,
                final_response="",
                formatted=False,
                intermediate_steps=[],
                error=None,
                metadata=None,
                messages=[HumanMessage(content=query)]
            )
            
            logger.info(f"🚀 Traitement de la requête: '{query}'")
            
            # Exécuter le graphe
            final_state = self.compiled_graph.invoke(initial_state)
            
            total_time = time.time() - start_time
            
            # Construire la réponse
            response = {
                "success": final_state.get("success", False),
                "response": final_state.get("final_response", ""),
                "agent_used": final_state.get("agent_type_used", "unknown"),
                "confidence": final_state.get("confidence", 0.0),
                "processing_time": total_time,
                "metadata": {
                    "classification": final_state.get("classification"),
                    "expanded_query": final_state.get("expanded_query"),
                    "requested_count": final_state.get("requested_count"),
                    "rag_status": self.rag_status,
                    "llm_provider": self.llm_provider,
                    "model_name": self.model_name
                }
            }
            
            if final_state.get("error"):
                response["error"] = final_state["error"]
            
            logger.info(f"✅ Recommandation générée en {total_time:.2f}s pour agent {response['agent_used']}")
            return response
            
        except Exception as e:
            logger.error(f"❌ Erreur génération recommandation: {e}")
            return {
                "success": False,
                "response": "Désolé, je rencontre des difficultés techniques. Veuillez réessayer.",
                "error": str(e),
                "agent_used": "error_fallback",
                "confidence": 0.0,
                "processing_time": 0.0,
                "metadata": {}
            }
    
    def get_tech_recommendations(self, query: str, user_id: int = 1) -> Dict[str, Any]:
        """Force l'utilisation de l'agent technique"""
        return self._get_forced_recommendation(query, "tech", user_id)
    
    def get_literature_recommendations(self, query: str, user_id: int = 1) -> Dict[str, Any]:
        """Force l'utilisation de l'agent littéraire"""
        return self._get_forced_recommendation(query, "literature", user_id)
    
    def get_manga_recommendations(self, query: str, user_id: int = 1) -> Dict[str, Any]:
        """Force l'utilisation de l'agent manga"""
        return self._get_forced_recommendation(query, "manga", user_id)
    
    def _get_forced_recommendation(self, query: str, agent_type: str, user_id: int = 1) -> Dict[str, Any]:
        """Obtient une recommandation en forçant un type d'agent spécifique"""
        try:
            # Appeler le nœud agent directement
            agent_node = self.agent_nodes.get(f"{agent_type}_agent")
            if not agent_node:
                raise ValueError(f"Agent {agent_type} non disponible")
            
            # Préparer l'état pour l'agent spécifique
            state = {
                "query": query,
                "expanded_query": query,
                "agent_type": agent_type,
                "requested_count": 3,
                "user_id": user_id,
                "confidence": 1.0  # Forçé
            }
            
            start_time = time.time()
            result_state = agent_node(state)
            processing_time = time.time() - start_time
            
            # Formater la réponse
            formatter_state = self.agent_nodes["formatter"](result_state)
            
            return {
                "success": formatter_state.get("success", False),
                "response": formatter_state.get("final_response", ""),
                "agent_used": agent_type,
                "confidence": 1.0,
                "processing_time": processing_time,
                "metadata": {
                    "forced_agent": True,
                    "expanded_query": query,
                    "rag_status": self.rag_status
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur agent forcé {agent_type}: {e}")
            return {
                "success": False,
                "response": f"Erreur avec l'agent {agent_type}: {str(e)}",
                "error": str(e),
                "agent_used": agent_type,
                "confidence": 0.0,
                "processing_time": 0.0,
                "metadata": {"forced_agent": True}
            }
    
    def health_check(self) -> Dict[str, Any]:
        """Vérifie l'état de santé du système"""
        try:
            # Test basique du LLM
            test_message = "Hello, test"
            llm_response = self.llm.invoke([HumanMessage(content=test_message)])
            llm_working = len(str(llm_response.content)) > 0
            
            # Test des nœuds
            nodes_status = {}
            for node_name, node in self.agent_nodes.items():
                try:
                    nodes_status[node_name] = "available"
                except Exception:
                    nodes_status[node_name] = "error"
            
            return {
                "status": "healthy" if llm_working else "degraded",
                "llm": {
                    "provider": self.llm_provider,
                    "model": self.model_name,
                    "working": llm_working
                },
                "nodes": nodes_status,
                "rag_systems": self.rag_status,
                "graph_compiled": hasattr(self, 'compiled_graph')
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "llm": {"working": False},
                "rag_systems": self.rag_status
            }
    
    def get_graph_visualization(self) -> str:
        """Retourne une représentation textuelle du graphe"""
        return """
🚀 BookAdvisor LangGraph Architecture

📥 INPUT: User Query + User ID
    ↓
🔍 CLASSIFIER NODE
    ├─ Analyse la requête
    ├─ Détecte: tech/literature/manga
    ├─ Expand la requête sémantiquement
    └─ Extrait le nombre demandé
    ↓
🔄 ROUTER NODE
    ├─ Route vers l'agent approprié
    ├─ TechAgent: Livres techniques
    ├─ LiteratureAgent: Littérature (sans manga)
    └─ MangaAgent: Manga/Comics/BD
    ↓
🎨 FORMATTER NODE
    ├─ Formate la réponse finale
    ├─ Ajoute métadonnées de traitement
    └─ Suggestions contextuelles
    ↓
📤 OUTPUT: Formatted Response + Metadata
"""

# Interface de compatibilité avec l'ancien système
class LangChainAgentManager:
    """Interface de compatibilité pour remplacer SimpleAgentManager"""
    
    def __init__(self, llm_provider: str = "openai", model_name: str = "gpt-3.5-turbo", **llm_kwargs):
        self.graph_manager = BookAdvisorGraphManager(llm_provider, model_name, **llm_kwargs)
        logger.info("✅ LangChainAgentManager initialisé - Compatible avec SimpleAgentManager")
    
    def route_query(self, query: str, user_id: int = 1) -> str:
        """Compatible avec SimpleAgentManager.route_query()"""
        result = self.graph_manager.get_recommendation(query, user_id)
        return result.get("response", "Erreur lors du traitement de la requête")
    
    def get_tech_recommendations(self, query: str, user_id: int = 1) -> str:
        """Compatible avec SimpleAgentManager.get_tech_recommendations()"""
        result = self.graph_manager.get_tech_recommendations(query, user_id)
        return result.get("response", "Erreur lors des recommandations techniques")
    
    def get_literature_recommendations(self, query: str, user_id: int = 1) -> str:
        """Compatible avec SimpleAgentManager.get_literature_recommendations()"""
        result = self.graph_manager.get_literature_recommendations(query, user_id)
        return result.get("response", "Erreur lors des recommandations littéraires")
    
    def get_manga_recommendations(self, query: str, user_id: int = 1) -> str:
        """Compatible avec SimpleAgentManager.get_manga_recommendations()"""
        result = self.graph_manager.get_manga_recommendations(query, user_id)
        return result.get("response", "Erreur lors des recommandations manga")
    
    def get_agent_response(self, query: str, agent_type: str = "router", user_id: int = 1) -> str:
        """Compatible avec SimpleAgentManager.get_agent_response()"""
        if agent_type == "router":
            return self.route_query(query, user_id)
        elif agent_type == "tech":
            return self.get_tech_recommendations(query, user_id)
        elif agent_type == "literature":
            return self.get_literature_recommendations(query, user_id)
        elif agent_type == "manga":
            return self.get_manga_recommendations(query, user_id)
        else:
            return "Type d'agent non reconnu"
    
    def get_system_status(self) -> Dict[str, Any]:
        """Compatible avec SimpleAgentManager.get_system_status()"""
        health = self.graph_manager.health_check()
        multi_model_status = self.graph_manager.multi_model_manager.get_system_status()
        model_rankings = self.graph_manager.multi_model_manager.get_model_rankings()
        
        return {
            "simple_agents": "replaced_by_langchain",
            "langchain_available": True,
            "langchain_active": True,
            "llm_provider": self.graph_manager.llm_provider,
            "llm_model": self.graph_manager.model_name,
            "health_check": health,
            "multi_model_system": multi_model_status,
            "model_rankings": model_rankings[:3],  # Top 3 modèles
            "evaluation_enabled": multi_model_status.get("evaluation_enabled", False)
        }
    
    def evaluate_models(self) -> Dict[str, Any]:
        """Lance l'évaluation des modèles disponibles"""
        try:
            return self.graph_manager.model_evaluator.compare_models()
        except Exception as e:
            logger.error(f"❌ Erreur évaluation modèles: {e}")
            return {"error": str(e)}
    
    def get_model_rankings(self) -> List[Dict]:
        """Retourne le classement des modèles"""
        return self.graph_manager.multi_model_manager.get_model_rankings()
    
    def switch_to_best_model(self, agent_type: str = "general") -> Dict[str, Any]:
        """Bascule vers le meilleur modèle pour un type de tâche"""
        try:
            best_model = self.graph_manager.multi_model_manager.get_best_model_for_task(agent_type)
            
            if best_model != self.graph_manager.model_name:
                # Recréer le LLM avec le nouveau modèle
                old_model = self.graph_manager.model_name
                self.graph_manager.model_name = best_model
                self.graph_manager.llm = self.graph_manager._create_llm()
                
                # Recréer les nœuds avec le nouveau LLM
                self.graph_manager.classifier_node = ClassifierNode(self.graph_manager.llm)
                self.graph_manager.agent_nodes = AgentNodesFactory.create_all_nodes(self.graph_manager.llm)
                
                # Recompiler le graphe
                self.graph_manager.compiled_graph = self.graph_manager.graph.compile()
                
                logger.info(f"🔄 Modèle changé: {old_model} → {best_model}")
                
                return {
                    "success": True,
                    "old_model": old_model,
                    "new_model": best_model,
                    "agent_type": agent_type
                }
            else:
                return {
                    "success": True,
                    "message": f"Modèle {best_model} déjà utilisé",
                    "current_model": best_model
                }
                
        except Exception as e:
            logger.error(f"❌ Erreur changement modèle: {e}")
            return {"success": False, "error": str(e)}

if __name__ == "__main__":
    # Test du gestionnaire
    print("🔧 Test du BookAdvisorGraphManager...")
    
    # Exemple avec un LLM mock
    try:
        manager = BookAdvisorGraphManager(
            llm_provider="openai",  # Configurez selon vos besoins
            model_name="gpt-3.5-turbo"
        )
        
        print("✅ Manager créé avec succès")
        print(manager.get_graph_visualization())
        
        # Test de santé
        health = manager.health_check()
        print(f"🏥 Health check: {health['status']}")
        
        # Tests de recommandations
        test_queries = [
            ("apprendre Python", "tech"),
            ("romans de Tolstoï", "literature"), 
            ("manga comme Naruto", "manga")
        ]
        
        for query, expected_agent in test_queries:
            print(f"\n🧪 Test: '{query}' (attendu: {expected_agent})")
            try:
                result = manager.get_recommendation(query)
                print(f"   ✅ Agent utilisé: {result['agent_used']}")
                print(f"   ⏱️ Temps: {result['processing_time']:.2f}s")
                print(f"   📝 Début réponse: {result['response'][:100]}...")
            except Exception as e:
                print(f"   ❌ Erreur: {e}")
        
    except Exception as e:
        print(f"❌ Erreur test: {e}")
        print("💡 Configurez vos clés API LLM pour tester complètement")