"""
LangChain-based agents for book recommendations
"""
from typing import List, Dict, Any, Optional
import logging
from langchain_core.tools import Tool
from langchain_core.prompts import PromptTemplate
from langchain_core.language_models import BaseLanguageModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.llms import HuggingFacePipeline
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain.agents import AgentExecutor, format_log_to_str
from langchain.memory import ConversationBufferMemory
from rags.tech_rag.tech_rag_manager import TechRAGManager
from rags.literature_rag.literature_rag_manager import LiteratureRAGManager

logger = logging.getLogger(__name__)


class BookRecommendationAgent:
    """Agent de base pour les recommandations de livres"""
    
    def __init__(self, llm: BaseLanguageModel, rag_manager, agent_type: str):
        self.llm = llm
        self.rag_manager = rag_manager
        self.agent_type = agent_type
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        
        # Créer les outils
        self.tools = self._create_tools()
        
        # Créer le prompt
        self.prompt = self._create_prompt()
        
        # Créer l'agent
        self.agent = self._create_agent()
    
    def _create_tools(self) -> List[Tool]:
        """Crée les outils pour l'agent"""
        return [
            Tool(
                name="search_books",
                description=f"Recherche des livres {self.agent_type} basé sur une requête utilisateur",
                func=self._search_books
            ),
            Tool(
                name="get_recommendations",
                description=f"Génère des recommandations de livres {self.agent_type} personnalisées",
                func=self._get_recommendations
            )
        ]
    
    def _search_books(self, query: str) -> str:
        """Recherche des livres via le RAG manager"""
        try:
            results = self.rag_manager.search_books(query, n_results=5)
            if not results:
                return "Aucun livre trouvé pour cette requête."
            
            formatted_results = []
            for result in results:
                formatted_results.append(
                    f"📚 {result['title']} - {result.get('author', result.get('authors', 'Auteur inconnu'))}\n"
                    f"   Score: {result['similarity_score']:.2f}\n"
                    f"   Note: {result.get('rating', result.get('average_rating', 'N/A'))}/5"
                )
            
            return "\n\n".join(formatted_results)
        except Exception as e:
            logger.error(f"Erreur lors de la recherche: {e}")
            return f"Erreur lors de la recherche: {str(e)}"
    
    def _get_recommendations(self, query: str) -> str:
        """Génère des recommandations personnalisées"""
        try:
            # Pour l'instant, on utilise un user_id par défaut
            recommendations = self.rag_manager.get_book_recommendations(
                user_id=1, 
                query=query, 
                n_recommendations=3
            )
            
            if not recommendations:
                return "Aucune recommandation trouvée pour cette requête."
            
            formatted_recs = []
            for rec in recommendations:
                book = rec['book']
                formatted_recs.append(
                    f"📖 **{book['title']}**\n"
                    f"   👤 Auteur: {book.get('author', book.get('authors', 'Auteur inconnu'))}\n"
                    f"   ⭐ Note: {book.get('rating', book.get('average_rating', 'N/A'))}/5\n"
                    f"   📊 Pertinence: {rec['similarity_score']:.0%}\n"
                    f"   💡 {rec['reason']}\n"
                    f"   📖 {book['description'][:150]}..."
                )
            
            return "\n\n".join(formatted_recs)
        except Exception as e:
            logger.error(f"Erreur lors de la génération des recommandations: {e}")
            return f"Erreur lors de la génération des recommandations: {str(e)}"
    
    def _create_prompt(self) -> PromptTemplate:
        """Crée le prompt pour l'agent"""
        if self.agent_type == "technique":
            template = """Tu es un agent spécialisé dans les recommandations de livres techniques et de programmation.
Tu aides les utilisateurs à trouver des livres sur les technologies, langages de programmation, développement web, mobile, data science, etc.

Tu as accès aux outils suivants:
{tools}

Utilise le format suivant pour répondre:

Question: la question d'entrée que tu dois répondre
Thought: tu dois toujours réfléchir à ce que tu dois faire
Action: l'action à prendre, doit être une de [{tool_names}]
Action Input: l'entrée pour l'action
Observation: le résultat de l'action
... (ce processus Thought/Action/Action Input/Observation peut être répété)
Thought: Je connais maintenant la réponse finale
Final Answer: la réponse finale à la question originale

🔧 Contexte: Spécialiste en livres techniques et programmation
📚 Mission: Recommander des livres techniques pertinents et de qualité

Historique de conversation:
{chat_history}

Question: {input}
{agent_scratchpad}"""
        else:
            template = """Tu es un agent spécialisé dans les recommandations de livres littéraires.
Tu aides les utilisateurs à trouver des romans, nouvelles, essais, et autres œuvres littéraires selon leurs goûts.

Tu as accès aux outils suivants:
{tools}

Utilise le format suivant pour répondre:

Question: la question d'entrée que tu dois répondre
Thought: tu dois toujours réfléchir à ce que tu dois faire
Action: l'action à prendre, doit être une de [{tool_names}]
Action Input: l'entrée pour l'action
Observation: le résultat de l'action
... (ce processus Thought/Action/Action Input/Observation peut être répété)
Thought: Je connais maintenant la réponse finale
Final Answer: la réponse finale à la question originale

📚 Contexte: Spécialiste en littérature et fiction
💖 Mission: Recommander des livres littéraires selon les goûts et préférences

Historique de conversation:
{chat_history}

Question: {input}
{agent_scratchpad}"""
        
        return PromptTemplate(
            template=template,
            input_variables=["input", "agent_scratchpad", "chat_history"],
            partial_variables={
                "tools": "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools]),
                "tool_names": ", ".join([tool.name for tool in self.tools])
            }
        )
    
    def _create_agent(self) -> AgentExecutor:
        """Crée l'agent executor"""
        llm_with_stop = self.llm.bind(stop=["\nObservation"])
        
        agent = (
            {
                "input": lambda x: x["input"],
                "agent_scratchpad": lambda x: format_log_to_str(x["intermediate_steps"]),
                "chat_history": lambda x: x["chat_history"]
            }
            | self.prompt
            | llm_with_stop
            | ReActSingleInputOutputParser()
        )
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3
        )
    
    def run(self, query: str) -> str:
        """Exécute l'agent avec une requête"""
        try:
            result = self.agent.invoke({"input": query})
            return result["output"]
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de l'agent: {e}")
            return f"Désolé, une erreur s'est produite: {str(e)}"


class RouterAgent:
    """Agent de routage général qui dirige vers l'agent approprié"""
    
    def __init__(self, llm: BaseLanguageModel, tech_agent: BookRecommendationAgent, literature_agent: BookRecommendationAgent):
        self.llm = llm
        self.tech_agent = tech_agent
        self.literature_agent = literature_agent
        
        # Prompt pour le routage
        self.routing_prompt = PromptTemplate(
            template="""Tu es un assistant de routage pour des recommandations de livres.
Analyse la requête utilisateur et détermine si elle concerne:
- TECH: Programmation, technologies, développement, data science, informatique
- LITERATURE: Romans, fiction, littérature, histoires, genres littéraires
- GENERAL: Questions générales ou ambiguës

Requête: {query}

Réponds uniquement par: TECH, LITERATURE, ou GENERAL

Classification:""",
            input_variables=["query"]
        )
    
    def route_query(self, query: str) -> str:
        """Détermine l'agent approprié et exécute la requête"""
        try:
            # Déterminer le type de requête
            routing_result = self.llm.invoke(self.routing_prompt.format(query=query))
            classification = routing_result.content.strip().upper()
            
            if classification == "TECH":
                return f"🔧 **Agent Technique**\n\n{self.tech_agent.run(query)}"
            elif classification == "LITERATURE":
                return f"📚 **Agent Littéraire**\n\n{self.literature_agent.run(query)}"
            else:
                return self._handle_general_query(query)
        
        except Exception as e:
            logger.error(f"Erreur lors du routage: {e}")
            return f"Erreur lors du routage: {str(e)}"
    
    def _handle_general_query(self, query: str) -> str:
        """Gère les requêtes générales"""
        return f"""🤖 **Agent Général**

Je peux vous aider avec des recommandations de livres ! 

**Spécialisations disponibles:**
- 🔧 **Livres techniques**: Programmation, développement, data science, technologies
- 📚 **Livres littéraires**: Romans, fiction, genres littéraires, auteurs

**Exemples de requêtes:**
- "Je veux apprendre Python" → Agent technique
- "J'ai adoré Harry Potter, que me conseillez-vous ?" → Agent littéraire
- "Un livre sur le JavaScript" → Agent technique
- "Des romans fantastiques" → Agent littéraire

**Votre requête**: "{query}"

Pourriez-vous préciser si vous cherchez des livres techniques ou littéraires ?"""


class LangChainAgentManager:
    """Gestionnaire pour les agents LangChain"""
    
    def __init__(self, llm_provider: str = "openai", model_name: str = "gpt-3.5-turbo"):
        self.llm_provider = llm_provider
        self.model_name = model_name
        
        # Initialiser le LLM
        self.llm = self._create_llm()
        
        # Initialiser les RAG managers
        self.tech_rag = TechRAGManager()
        self.literature_rag = LiteratureRAGManager()
        
        # Créer les agents
        self.tech_agent = BookRecommendationAgent(self.llm, self.tech_rag, "technique")
        self.literature_agent = BookRecommendationAgent(self.llm, self.literature_rag, "littéraire")
        self.router_agent = RouterAgent(self.llm, self.tech_agent, self.literature_agent)
    
    def _create_llm(self) -> BaseLanguageModel:
        """Crée le modèle de langage selon le provider"""
        if self.llm_provider == "openai":
            return ChatOpenAI(model_name=self.model_name, temperature=0.7)
        elif self.llm_provider == "anthropic":
            return ChatAnthropic(model_name=self.model_name, temperature=0.7)
        elif self.llm_provider == "huggingface":
            return HuggingFacePipeline.from_model_id(
                model_id=self.model_name,
                task="text-generation",
                model_kwargs={"temperature": 0.7}
            )
        else:
            raise ValueError(f"Provider non supporté: {self.llm_provider}")
    
    def get_agent_response(self, query: str, agent_type: str = "router") -> str:
        """Obtient une réponse de l'agent spécifié"""
        try:
            if agent_type == "router":
                return self.router_agent.route_query(query)
            elif agent_type == "tech":
                return f"🔧 **Agent Technique**\n\n{self.tech_agent.run(query)}"
            elif agent_type == "literature":
                return f"📚 **Agent Littéraire**\n\n{self.literature_agent.run(query)}"
            else:
                return "Agent non reconnu. Utilisez: 'router', 'tech', ou 'literature'"
        
        except Exception as e:
            logger.error(f"Erreur lors de l'obtention de la réponse: {e}")
            return f"Erreur: {str(e)}"