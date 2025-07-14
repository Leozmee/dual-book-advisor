"""
Agent Nodes - Nœuds spécialisés pour LangGraph
Fichier: agents/langchain_agents/nodes/agent_nodes.py
"""
from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.messages import HumanMessage, AIMessage
import logging
import time

from ..tools.rag_tools import RAGToolsFactory, ResultFormatter

logger = logging.getLogger(__name__)

class BaseAgentNode:
    """Classe de base pour tous les nœuds d'agents"""
    
    def __init__(self, llm, agent_type: str):
        self.llm = llm
        self.agent_type = agent_type
        self.tool = RAGToolsFactory.get_tool_by_agent_type(agent_type)
        self.prompt = self._create_prompt()
        self.agent_executor = self._create_agent_executor()
    
    def _create_prompt(self) -> ChatPromptTemplate:
        """Crée le prompt pour cet agent (à override dans les sous-classes)"""
        raise NotImplementedError("Doit être implémenté dans les sous-classes")
    
    def _create_agent_executor(self) -> AgentExecutor:
        """Crée l'exécuteur d'agent avec les outils"""
        agent = create_openai_tools_agent(
            llm=self.llm,
            tools=[self.tool],
            prompt=self.prompt
        )
        
        return AgentExecutor(
            agent=agent,
            tools=[self.tool],
            verbose=True,
            return_intermediate_steps=True,
            max_iterations=3
        )
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Interface LangGraph - traite l'état et retourne la réponse"""
        try:
            start_time = time.time()
            
            # Extraire les informations de l'état
            query = state.get("expanded_query", state.get("query", ""))
            requested_count = state.get("requested_count", 3)
            user_id = state.get("user_id", 1)
            
            if not query:
                logger.warning(f"Requête vide pour agent {self.agent_type}")
                return self._create_error_response(state, "Requête vide")
            
            # Préparer les inputs pour l'agent
            agent_input = {
                "input": f"L'utilisateur demande: '{query}'. Il souhaite {requested_count} recommandations.",
                "query": query,
                "requested_count": requested_count,
                "user_id": user_id
            }
            
            # Exécuter l'agent
            logger.info(f"🤖 Agent {self.agent_type} traite: '{query}'")
            result = self.agent_executor.invoke(agent_input)
            
            processing_time = time.time() - start_time
            
            # Mettre à jour l'état avec la réponse
            state.update({
                "agent_response": result["output"],
                "agent_type_used": self.agent_type,
                "processing_time": processing_time,
                "intermediate_steps": result.get("intermediate_steps", []),
                "success": True
            })
            
            logger.info(f"✅ Agent {self.agent_type} terminé en {processing_time:.2f}s")
            return state
            
        except Exception as e:
            logger.error(f"❌ Erreur agent {self.agent_type}: {e}")
            return self._create_error_response(state, str(e))
    
    def _create_error_response(self, state: Dict[str, Any], error_message: str) -> Dict[str, Any]:
        """Crée une réponse d'erreur standardisée"""
        fallback_response = self._get_fallback_response(state.get("query", ""))
        
        state.update({
            "agent_response": fallback_response,
            "agent_type_used": self.agent_type,
            "processing_time": 0.0,
            "error": error_message,
            "success": False
        })
        
        return state
    
    def _get_fallback_response(self, query: str) -> str:
        """Génère une réponse de fallback (à override dans les sous-classes)"""
        return f"Désolé, je rencontre des difficultés pour traiter votre demande sur {self.agent_type}."

class TechAgentNode(BaseAgentNode):
    """Nœud agent pour les livres techniques"""
    
    def __init__(self, llm):
        super().__init__(llm, "tech")
    
    def _create_prompt(self) -> ChatPromptTemplate:
        """Prompt spécialisé pour les recommandations techniques"""
        return ChatPromptTemplate.from_messages([
            ("system", """Tu es un expert français en livres techniques et programmation. 

RÔLE:
- Recommander des livres techniques adaptés aux besoins de l'utilisateur
- Expliquer pourquoi ces livres correspondent à leur demande
- Donner des conseils pratiques sur l'apprentissage technique

OUTILS DISPONIBLES:
- tech_book_search: Recherche dans une base de livres techniques spécialisée

INSTRUCTIONS:
- Réponds EXCLUSIVEMENT en français
- Utilise des emojis techniques (🔧, 💻, 📚, ⭐, 💰)
- Sois précis sur les technologies, niveaux de difficulté, et bénéfices
- Adapte tes recommandations au niveau suggéré par la requête
- Mentionne les prix quand disponibles
- Donne des conseils d'apprentissage contextuels

STYLE DE RÉPONSE:
🔧 **Recommandations Techniques**

[Pour chaque livre:]
1. **Titre** par Auteur
   ⭐ Note: X/5 | 💰 Prix: $XX | 📊 Pertinence: XX%
   💡 Pourquoi ce livre: [Explication]
   📖 [Description courte]

⚡ Conseils d'apprentissage: [Suggestions pratiques]

N'hésite pas à chercher des livres avec l'outil disponible."""),
            
            ("human", "{input}"),
            
            ("placeholder", "{agent_scratchpad}")
        ])
    
    def _get_fallback_response(self, query: str) -> str:
        """Fallback spécialisé pour les livres techniques"""
        import re
        query_lower = query.lower()
        
        # Suggestions contextuelles
        if re.search(r'\b(python)\b', query_lower):
            return """🔧 **Recommandations Python**

Je recommande ces excellents livres pour Python :

1. **Python Crash Course** par Eric Matthes
   ⭐ Parfait pour débuter, projets pratiques
   
2. **Automate the Boring Stuff** par Al Sweigart  
   ⭐ Applications concrètes et utiles

💡 Précisez votre niveau (débutant/intermédiaire/avancé) pour des recommandations plus ciblées !"""

        elif re.search(r'\b(javascript|js)\b', query_lower):
            return """🔧 **Recommandations JavaScript**

Excellents livres pour JavaScript :

1. **JavaScript: The Good Parts** par Douglas Crockford
   ⭐ Comprendre les fondamentaux
   
2. **You Don't Know JS** série par Kyle Simpson
   ⭐ Approfondir le langage

💡 Intéressé par le frontend, backend, ou les deux ?"""
        
        else:
            return """🔧 **Recommandations Techniques**

Je peux vous aider avec des livres sur :

💻 **Langages populaires :**
- Python : Idéal pour débuter, data science, IA
- JavaScript : Développement web, applications
- Java : Applications entreprise, Android
- C# : Développement Windows, .NET

🎯 **Domaines spécialisés :**
- Développement web (HTML, CSS, frameworks)
- Data science et machine learning
- Développement mobile
- DevOps et cloud

💡 Précisez un langage ou domaine pour des recommandations personnalisées !"""

class LiteratureAgentNode(BaseAgentNode):
    """Nœud agent pour la littérature (sans manga)"""
    
    def __init__(self, llm):
        super().__init__(llm, "literature")
    
    def _create_prompt(self) -> ChatPromptTemplate:
        """Prompt spécialisé pour les recommandations littéraires"""
        return ChatPromptTemplate.from_messages([
            ("system", """Tu es un critique littéraire français passionné et cultivé.

RÔLE:
- Recommander des livres littéraires adaptés aux goûts de l'utilisateur
- Expliquer les thèmes, styles, et pourquoi ces œuvres plairont
- Partager des insights sur les auteurs et contextes historiques
- EXCLURE automatiquement tout manga, anime ou comics de tes recommandations

OUTILS DISPONIBLES:
- literature_book_search: Recherche dans une base littéraire (SANS manga/comics)

INSTRUCTIONS:
- Réponds EXCLUSIVEMENT en français
- Utilise des emojis littéraires (📚, ✨, 💫, 📖, 🎭)
- Sois empathique et personnalise selon les goûts exprimés
- Évoque l'émotion et l'expérience de lecture
- Utilise un français élégant et cultivé
- Contextualise historiquement et culturellement

STYLE DE RÉPONSE:
📚 **Recommandations Littéraires**

[Pour chaque livre:]
1. **Titre** de Auteur
   ⭐ Note: X/5 | 📅 Publié: XXXX | 📊 Pertinence: XX%
   💫 Pourquoi vous aimerez: [Explication émotionnelle/thématique]
   📖 [Description évocatrice]

✨ Mon conseil: [Suggestion de lecture ou contexte culturel]

N'hésite pas à chercher des livres avec l'outil disponible."""),
            
            ("human", "{input}"),
            
            ("placeholder", "{agent_scratchpad}")
        ])
    
    def _get_fallback_response(self, query: str) -> str:
        """Fallback spécialisé pour la littérature"""
        import re
        query_lower = query.lower()
        
        # Références spécifiques
        if re.search(r'\b(tolstoï|tolstoy)\b', query_lower):
            return """📚 **Recommandations inspirées de Tolstoï**

Si vous appréciez Tolstoï, je vous suggère :

1. **Crime et Châtiment** de Dostoïevski
   💫 Même profondeur psychologique, questionnements moraux
   
2. **Madame Bovary** de Flaubert  
   ✨ Réalisme minutieux, étude de caractère

💡 Qu'avez-vous particulièrement aimé chez Tolstoï ? Les grands fresques historiques ou l'analyse psychologique ?"""

        elif re.search(r'\b(murakami)\b', query_lower):
            return """📚 **Recommandations dans l'esprit de Murakami**

Pour prolonger l'univers Murakami :

1. **L'Étranger** de Camus
   💫 Même étrangeté existentielle
   
2. **Les Villes invisibles** de Calvino
   ✨ Poésie du quotidien, réalisme magique

✨ L'atmosphère onirique de Murakami vous fascine-t-elle particulièrement ?"""
        
        else:
            return """📚 **Découvertes Littéraires**

Je peux vous guider vers de magnifiques découvertes :

🎭 **Classiques intemporels :**
- Tolstoï, Dostoïevski : Grands romans russes
- Hugo, Balzac : Littérature française du XIXe
- Shakespeare : Théâtre universel

🌟 **Littérature contemporaine :**
- Murakami : Réalisme magique japonais
- Ferrante : Saga napolitaine intense
- Houellebecq : Regard acéré sur l'époque

💫 **Genres spécialisés :**
- Fantasy littéraire, science-fiction d'auteur
- Littérature de voyage, biographies

✨ Dites-moi quel type d'émotion ou de réflexion vous recherchez dans vos lectures !"""

class MangaAgentNode(BaseAgentNode):
    """Nœud agent pour les mangas et comics"""
    
    def __init__(self, llm):
        super().__init__(llm, "manga")
    
    def _create_prompt(self) -> ChatPromptTemplate:
        """Prompt spécialisé pour les recommandations manga/comics"""
        return ChatPromptTemplate.from_messages([
            ("system", """Tu es un expert français passionné de manga, anime et bandes dessinées.

RÔLE:
- Recommander des mangas japonais, anime et comics/BD
- Expliquer les genres, histoires, et styles artistiques
- Faire des parallèles entre différentes œuvres
- Conseiller selon les préférences de l'utilisateur

OUTILS DISPONIBLES:
- manga_content_search: Recherche dans une base unifiée manga/comics/BD

INSTRUCTIONS:
- Réponds EXCLUSIVEMENT en français
- Tu es un expert français de la culture manga/BD, pas un "otaku anglophone"
- Utilise des emojis manga/anime (🎌, 🗾, ⚔️, 🌸, 🔥, 🦸)
- Explique les termes japonais (shounen, seinen, etc.) en français
- Compare avec d'autres œuvres connues
- Reste professionnel et informatif

STYLE DE RÉPONSE:
🎌 **Recommandations Manga & Comics**

[Pour chaque œuvre:]
1. 🎌/🦸 **Titre** 
   ⭐ Note: X/5 | 📅 Année: XXXX | 📊 Pertinence: XX%
   🔥 Pourquoi c'est génial: [Explication des qualités]
   📖 [Description de l'histoire et du style]

🌸 Mon conseil: [Suggestion de découverte ou comparaison]

N'hésite pas à chercher du contenu avec l'outil disponible."""),
            
            ("human", "{input}"),
            
            ("placeholder", "{agent_scratchpad}")
        ])
    
    def _get_fallback_response(self, query: str) -> str:
        """Fallback spécialisé pour manga/comics"""
        import re
        query_lower = query.lower()
        
        # Détection du type de contenu
        if re.search(r'\b(naruto|one piece|dragon ball|shounen)\b', query_lower):
            return """🎌 **Recommandations Manga Shounen**

Si vous aimez l'action et l'aventure :

1. 🔥 **Attack on Titan** (L'Attaque des Titans)
   ⚔️ Intense, sombre, mystérieux
   
2. 🌸 **Demon Slayer** (Kimetsu no Yaiba)
   🔥 Magnifique animation, émotions fortes

🎌 Préférez-vous l'action pure ou aussi des moments d'émotion ?"""

        elif re.search(r'\b(comics|superman|batman|marvel|dc)\b', query_lower):
            return """🦸 **Recommandations Comics & Superhéros**

Pour les amateurs de super-héros :

1. 🦸‍♂️ **All-Star Superman** de Grant Morrison
   ⭐ Le Superman parfait, touchant et héroïque
   
2. 🌃 **Batman: Year One** de Frank Miller
   🔥 Origine réaliste et noir

🦸 Plutôt univers Marvel ou DC ? Plutôt sombre ou optimiste ?"""
        
        else:
            return """🎌🦸 **Découvertes Manga & Comics**

Je peux vous orienter selon vos goûts :

🎌 **Manga japonais :**
- Shounen : Action, aventure (Naruto, One Piece)
- Seinen : Plus mature (Death Note, Tokyo Ghoul)  
- Shoujo : Romance, émotion (Fruits Basket)

🦸 **Comics occidentaux :**
- Super-héros : Marvel, DC (Spider-Man, Batman)
- BD française : Tintin, Astérix, albums d'auteur
- Graphic novels : Récits adultes et artistiques

🌸 **Que recherchez-vous ?**
- Action et combats épiques ?
- Histoires touchantes et personnages ?
- Univers sombres et psychologiques ?
- Humour et aventure ?

🔥 Décrivez-moi vos goûts pour des recommandations précises !"""

class RouterNode:
    """Nœud de routage qui dirige vers l'agent approprié"""
    
    def __init__(self):
        self.agent_nodes = {}
    
    def register_agents(self, tech_node: TechAgentNode, literature_node: LiteratureAgentNode, manga_node: MangaAgentNode):
        """Enregistre les nœuds d'agents"""
        self.agent_nodes = {
            "tech": tech_node,
            "literature": literature_node,
            "manga": manga_node
        }
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Route vers l'agent approprié selon la classification"""
        try:
            agent_type = state.get("agent_type", "literature")
            confidence = state.get("confidence", 0.5)
            
            logger.info(f"🔄 Routage vers agent {agent_type} (confiance: {confidence})")
            
            # Sélectionner l'agent approprié
            selected_agent = self.agent_nodes.get(agent_type)
            
            if not selected_agent:
                logger.error(f"Agent {agent_type} non trouvé, fallback vers literature")
                selected_agent = self.agent_nodes["literature"]
                state["agent_type"] = "literature"
            
            # Déléguer à l'agent sélectionné
            return selected_agent(state)
            
        except Exception as e:
            logger.error(f"❌ Erreur routage: {e}")
            # Fallback vers agent littérature
            fallback_agent = self.agent_nodes.get("literature")
            if fallback_agent:
                return fallback_agent(state)
            else:
                return self._create_emergency_fallback(state, str(e))
    
    def _create_emergency_fallback(self, state: Dict[str, Any], error_message: str) -> Dict[str, Any]:
        """Fallback d'urgence si aucun agent n'est disponible"""
        state.update({
            "agent_response": "🤖 Désolé, je rencontre des difficultés techniques. Veuillez réessayer dans quelques instants.",
            "agent_type_used": "emergency_fallback",
            "processing_time": 0.0,
            "error": error_message,
            "success": False
        })
        return state

class ResponseFormatterNode:
    """Nœud de formatage final des réponses"""
    
    def __init__(self):
        pass
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Formate la réponse finale pour l'utilisateur"""
        try:
            agent_response = state.get("agent_response", "")
            agent_type = state.get("agent_type_used", "unknown")
            processing_time = state.get("processing_time", 0.0)
            success = state.get("success", True)
            
            # Ajouter les métadonnées de traitement
            if success and processing_time > 0:
                formatted_response = f"{agent_response}\n\n⚡ Traitement en {processing_time:.1f}s"
            else:
                formatted_response = agent_response
            
            # Ajouter des suggestions contextuelles si nécessaire
            if not success or len(agent_response) < 100:
                formatted_response += self._add_contextual_suggestions(state)
            
            # Mettre à jour l'état final
            state.update({
                "final_response": formatted_response,
                "formatted": True,
                "metadata": {
                    "agent_used": agent_type,
                    "processing_time": processing_time,
                    "success": success,
                    "timestamp": time.time()
                }
            })
            
            logger.info(f"✅ Réponse formatée pour agent {agent_type}")
            return state
            
        except Exception as e:
            logger.error(f"❌ Erreur formatage: {e}")
            state.update({
                "final_response": state.get("agent_response", "Erreur de formatage"),
                "formatted": False,
                "error": str(e)
            })
            return state
    
    def _add_contextual_suggestions(self, state: Dict[str, Any]) -> str:
        """Ajoute des suggestions contextuelles"""
        agent_type = state.get("agent_type_used", "")
        
        suggestions = {
            "tech": "\n\n💡 **Suggestions :**\n- Précisez votre niveau (débutant/intermédiaire/avancé)\n- Mentionnez un langage ou domaine spécifique\n- Indiquez votre objectif (travail, loisir, reconversion)",
            
            "literature": "\n\n💡 **Suggestions :**\n- Mentionnez un auteur ou genre que vous aimez\n- Précisez l'époque qui vous intéresse\n- Indiquez le type d'émotion recherchée",
            
            "manga": "\n\n💡 **Suggestions :**\n- Précisez si vous préférez manga japonais ou comics occidentaux\n- Mentionnez des œuvres que vous avez aimées\n- Indiquez vos genres préférés (action, romance, mystère)"
        }
        
        return suggestions.get(agent_type, "\n\n💡 Précisez votre demande pour de meilleures recommandations !")

# Factory pour créer tous les nœuds
class AgentNodesFactory:
    """Factory pour créer et configurer tous les nœuds d'agents"""
    
    @staticmethod
    def create_all_nodes(llm):
        """Crée tous les nœuds nécessaires"""
        # Créer les agents spécialisés
        tech_node = TechAgentNode(llm)
        literature_node = LiteratureAgentNode(llm)
        manga_node = MangaAgentNode(llm)
        
        # Créer le routeur et l'enregistrer
        router_node = RouterNode()
        router_node.register_agents(tech_node, literature_node, manga_node)
        
        # Créer le formateur
        formatter_node = ResponseFormatterNode()
        
        return {
            "tech_agent": tech_node,
            "literature_agent": literature_node,
            "manga_agent": manga_node,
            "router": router_node,
            "formatter": formatter_node
        }
    
    @staticmethod
    def test_all_nodes(llm, test_queries: Dict[str, str] = None):
        """Test basique de tous les nœuds"""
        if test_queries is None:
            test_queries = {
                "tech": "livres pour apprendre Python",
                "literature": "romans de Tolstoï",
                "manga": "manga comme Naruto"
            }
        
        nodes = AgentNodesFactory.create_all_nodes(llm)
        
        for agent_type, query in test_queries.items():
            try:
                # Simuler un état LangGraph
                test_state = {
                    "query": query,
                    "expanded_query": query,
                    "agent_type": agent_type,
                    "requested_count": 3,
                    "user_id": 1,
                    "confidence": 0.8
                }
                
                # Tester l'agent direct
                agent_node = nodes[f"{agent_type}_agent"]
                result_state = agent_node(test_state.copy())
                
                success = result_state.get("success", False)
                response_length = len(result_state.get("agent_response", ""))
                
                print(f"✅ {agent_type}_agent: {'Succès' if success else 'Échec'} - {response_length} caractères")
                
                if success and response_length > 0:
                    print(f"   Début: {result_state['agent_response'][:100]}...")
                
            except Exception as e:
                print(f"❌ {agent_type}_agent: Erreur - {e}")

# Utilitaires de debugging
class NodeDebugger:
    """Utilitaires pour déboguer les nœuds"""
    
    @staticmethod
    def trace_node_execution(node, state: Dict[str, Any], node_name: str = "Unknown"):
        """Trace l'exécution d'un nœud avec détails"""
        print(f"\n🔍 DEBUG: Exécution du nœud {node_name}")
        print(f"📥 État d'entrée: {list(state.keys())}")
        
        if "query" in state:
            print(f"   Query: {state['query']}")
        if "agent_type" in state:
            print(f"   Agent type: {state['agent_type']}")
        
        try:
            start_time = time.time()
            result_state = node(state)
            execution_time = time.time() - start_time
            
            print(f"📤 État de sortie: {list(result_state.keys())}")
            print(f"⏱️ Temps d'exécution: {execution_time:.2f}s")
            
            if "success" in result_state:
                print(f"✅ Succès: {result_state['success']}")
            
            if "agent_response" in result_state:
                response_length = len(result_state["agent_response"])
                print(f"📝 Longueur réponse: {response_length} caractères")
                if response_length > 0:
                    print(f"   Début: {result_state['agent_response'][:150]}...")
            
            return result_state
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            import traceback
            traceback.print_exc()
            return state
    
    @staticmethod
    def validate_state_transitions(states: List[Dict[str, Any]], expected_keys: List[str]):
        """Valide les transitions d'état entre nœuds"""
        print("\n🔍 Validation des transitions d'état:")
        
        for i, state in enumerate(states):
            print(f"  État {i}: {list(state.keys())}")
            
            missing_keys = [key for key in expected_keys if key not in state]
            if missing_keys:
                print(f"    ⚠️ Clés manquantes: {missing_keys}")
            else:
                print(f"    ✅ Toutes les clés requises présentes")

if __name__ == "__main__":
    # Test des nœuds (nécessite un LLM configuré)
    print("🔧 Test des nœuds d'agents...")
    print("ℹ️ Configurez un LLM pour tester les nœuds")
    
    # Exemple de test avec un LLM mock
    # from langchain_openai import ChatOpenAI
    # llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
    # AgentNodesFactory.test_all_nodes(llm)