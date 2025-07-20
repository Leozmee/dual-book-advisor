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
            verbose=False,
            return_intermediate_steps=False,
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
                "input": f"L'utilisateur (ID: {user_id}) demande: '{query}'. Il souhaite {requested_count} recommandations. Utilise user_id={user_id} lors de l'appel aux outils.",
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
            ("system", """Tu es un expert technique français spécialisé dans la recommandation de livres informatiques et technologiques. Ta mission est d'aider les développeurs, étudiants et professionnels à trouver les ressources parfaites pour leurs objectifs d'apprentissage.

WORKFLOW OBLIGATOIRE:
1. ANALYSE : Identifie le niveau (débutant/intermédiaire/avancé), la technologie ciblée, et les objectifs
2. RECHERCHE : Utilise TOUJOURS `tech_book_search` avec des mots-clés pertinents
3. ÉVALUATION : Filtre selon les critères spécifiés (note minimale, année, etc.)
4. RECOMMANDATION : Présente 3-5 livres maximum, classés par pertinence

CRITÈRES DE RECOMMANDATION:
- **Pertinence technique** : Correspondance exacte avec la demande
- **Niveau approprié** : Adapté aux compétences déclarées
- **Actualité** : Priorité aux éditions récentes (< 3 ans pour les technologies évolutives)
- **Réputation** : Privilégier les auteurs reconnus et éditeurs spécialisés

FORMAT DE RÉPONSE:
🔧 Recommandations Techniques

[Pour chaque livre, classé par pertinence:]
[Rang]. [Titre] par [Auteur] ([Édition/Année])
⭐ Note: X/5 | 💰 Prix: $XX | 📊 Pertinence: XX% | 🎯 Niveau: [Débutant/Inter/Avancé]

Pourquoi ce livre :
[Explication spécifique en 2-3 phrases]

Ce que vous apprendrez :
[Points clés concrets]

⚡ Stratégie d'apprentissage :
[Conseil pratique et personnalisé]

---

🎯 Mon conseil global : [Suggestion d'approche d'apprentissage]

RÈGLES STRICTES:
- Réponds EXCLUSIVEMENT en français
- Utilise TOUJOURS l'outil tech_book_search
- Maximum 5 recommandations par réponse
- Si aucun résultat pertinent : explique pourquoi et propose des alternatives
- JAMAIS d'invention de titres ou d'auteurs

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
    Parfait pour débuter, projets pratiques
   
2. **Automate the Boring Stuff** par Al Sweigart  
    Applications concrètes et utiles

💡 Précisez votre niveau (débutant/intermédiaire/avancé) pour des recommandations plus ciblées !"""

        elif re.search(r'\b(javascript|js)\b', query_lower):
            return """🔧 **Recommandations JavaScript**

Excellents livres pour JavaScript :

1. **JavaScript: The Good Parts** par Douglas Crockford
    Comprendre les fondamentaux
   
2. **You Don't Know JS** série par Kyle Simpson
    Approfondir le langage

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
        self.llm = llm
        self.agent_type = "literature"
        # Utiliser deux outils : RAG littéraire + Wikipedia
        self.literature_tool = RAGToolsFactory.get_tool_by_agent_type("literature")
        self.wikipedia_tool = RAGToolsFactory.get_wikipedia_tool()
        self.tools = [self.literature_tool, self.wikipedia_tool]
        self.prompt = self._create_prompt()
        self.agent_executor = self._create_agent_executor()
    
    def _create_agent_executor(self) -> AgentExecutor:
        """Crée l'exécuteur d'agent avec les deux outils"""
        agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=False,
            return_intermediate_steps=False,
            max_iterations=3  # Optimisé pour les performances
        )
    
    def _create_prompt(self) -> ChatPromptTemplate:
        """Prompt spécialisé pour les recommandations littéraires"""
        return ChatPromptTemplate.from_messages([
            ("system", """Tu es un expert littéraire français spécialisé dans la recommandation de livres et la recherche d'informations littéraires.

**WORKFLOW OBLIGATOIRE:**
1. **ANALYSE** : Détermine si c'est une question d'auteur, une demande d'œuvres, ou une recommandation
2. **RECHERCHE** : Utilise TOUJOURS `literature_book_search` en premier pour toute recherche
3. **COMPLÉMENT** : Si `literature_book_search` ne donne pas assez d'informations, utilise `wikipedia_search`
4. **RÉPONSE** : Formate la réponse selon le type de demande

**OUTILS DISPONIBLES:**
- `literature_book_search`: Recherche dans la base de données littéraire (priorité)
- `wikipedia_search`: Recherche Wikipedia pour informations complémentaires

**TYPES DE DEMANDES ET RÉPONSES:**

**1. QUESTIONS D'AUTEUR (ex: "qui a écrit Les Misérables"):**
- Utilise `literature_book_search` avec le titre
- Si pas d'information sur l'auteur, utilise `wikipedia_search`
- Format: "L'auteur de [titre] est **[Auteur]**. [contexte bref]"

**2. DEMANDES D'ŒUVRES (ex: "œuvres de Stendhal", "livres de Victor Hugo"):**
- Utilise `literature_book_search` avec le nom de l'auteur
- Si peu de résultats, complète avec `wikipedia_search`
- Format: Liste des œuvres principales avec descriptions

**3. RECOMMANDATIONS (ex: "livres comme Tolstoï"):**
- Utilise `literature_book_search` pour trouver des livres similaires
- Présente 3-5 recommandations avec justifications

**FORMAT DE RÉPONSE POUR ŒUVRES D'AUTEUR:**
📚 **Œuvres de [Auteur]** ([dates])

Voici les principales œuvres de cet auteur :

1. **[Titre]** ([année]) - [description courte]
2. **[Titre]** ([année]) - [description courte]
3. **[Titre]** ([année]) - [description courte]

🎯 **Style de l'auteur :** [caractéristiques principales]

**RÈGLES CRITIQUES:**
- Utilise TOUJOURS les outils de recherche avant de répondre
- EXCLUS automatiquement : mangas, anime, comics, BD
- Ne donne JAMAIS de fausses informations
- Réponds EXCLUSIVEMENT en français
- Si un outil échoue, essaie l'autre outil

**EXEMPLE D'UTILISATION DES OUTILS:**
Pour "œuvres de Stendhal":
1. `literature_book_search(query="Stendhal", n_results=5)`
2. Si insuffisant: `wikipedia_search(query="Stendhal")`
3. Combine les résultats pour une réponse complète

N'hésite pas à utiliser les outils disponibles pour des réponses précises et complètes."""),
            
            ("human", "{input}"),
            
            ("placeholder", "{agent_scratchpad}")
        ])
    
    def _get_fallback_response(self, query: str) -> str:
        """Fallback spécialisé pour la littérature avec vraies informations"""
        import re
        query_lower = query.lower()
        
        # Références spécifiques pour auteurs classiques
        if re.search(r'\b(stendhal)\b', query_lower):
            return """📚 **Œuvres de Stendhal** (Henri Beyle, 1783-1842)

Voici les principales œuvres de cet auteur majeur du réalisme français :

1. **Le Rouge et le Noir** (1830)
   L'ascension sociale de Julien Sorel, entre passion et ambition
   
2. **La Chartreuse de Parme** (1839)
   Les aventures de Fabrice del Dongo dans l'Italie du XIXe siècle

3. **Lucien Leuwen** (inachevé)
   Roman d'apprentissage sur un jeune homme dans l'armée

4. **De l'Amour** (1822)
   Essai psychologique sur la passion amoureuse

🎯 **Style stendhalien :** Réalisme psychologique, analyse fine des sentiments, critique sociale subtile."""

        elif re.search(r'\b(victor hugo)\b', query_lower):
            return """📚 **Œuvres de Victor Hugo** (1802-1885)

Voici les principales œuvres de ce géant de la littérature française :

1. **Les Misérables** (1862)
   Épopée de Jean Valjean, fresque sociale du XIXe siècle
   
2. **Notre-Dame de Paris** (1831)
   L'amour impossible de Quasimodo et Esmeralda
   
3. **Les Contemplations** (1856)
   Recueil poétique sur la mort de sa fille Léopoldine
   
4. **L'Homme qui rit** (1869)
   Roman sombre sur Gwynplaine au visage défiguré

🎯 **Génie hugolien :** Romantisme social, engagement politique, virtuosité poétique."""

        elif re.search(r'\b(tolstoï|tolstoy)\b', query_lower):
            return """📚 **Œuvres de Léon Tolstoï** (1828-1910)

Voici les principales œuvres de ce maître russe :

1. **Guerre et Paix** (1869)
   Fresque épique de la Russie napoléonienne
   
2. **Anna Karénine** (1877)
   Tragédie de la passion amoureuse d'Anna
   
3. **La Mort d'Ivan Ilitch** (1886)
   Nouvelle sur la confrontation avec la mort
   
4. **Résurrection** (1899)
   Roman de la rédemption spirituelle

🎯 **Génie tolstoïen :** Psychologie profonde, questionnements moraux, spiritualité."""
        
        else:
            return """📚 **Découvertes Littéraires**

Je peux vous guider vers de magnifiques découvertes :

📖 **Classiques français :**
- **Victor Hugo** : Les Misérables, Notre-Dame de Paris
- **Stendhal** : Le Rouge et le Noir, La Chartreuse de Parme  
- **Gustave Flaubert** : Madame Bovary, L'Éducation sentimentale
- **Émile Zola** : Germinal, L'Assommoir

📖 **Littérature russe :**
- **Tolstoï** : Guerre et Paix, Anna Karénine
- **Dostoïevski** : Crime et Châtiment, Les Frères Karamazov

📖 **Auteurs contemporains :**
- **Albert Camus** : L'Étranger, La Peste
- **Haruki Murakami** : Kafka sur le rivage, Norwegian Wood

✨ Précisez un auteur, une époque ou un genre pour des recommandations personnalisées !"""

class MangaAgentNode(BaseAgentNode):
    """Nœud agent pour les mangas et comics"""
    
    def __init__(self, llm):
        super().__init__(llm, "manga")
    
    def _create_prompt(self) -> ChatPromptTemplate:
        """Prompt spécialisé pour les recommandations manga/comics"""
        return ChatPromptTemplate.from_messages([
            ("system", """Tu es un expert français de la culture manga, anime et comics internationaux.

**CONNAISSANCE INTÉGRÉE DES AUTEURS MANGA/ANIME:**
- **Naruto** : Auteur **Masashi Kishimoto** (mangaka japonais)
- **One Piece** : Auteur **Eiichiro Oda** (mangaka japonais)
- **Dragon Ball** : Auteur **Akira Toriyama** (mangaka japonais)
- **Attack on Titan / L'Attaque des Titans** : Auteur **Hajime Isayama** (mangaka japonais)
- **Death Note** : Auteurs **Tsugumi Ohba** (scénario) et **Takeshi Obata** (dessin)
- **Fullmetal Alchemist** : Auteur **Hiromu Arakawa** (mangaka japonaise)
- **Demon Slayer** : Auteur **Koyoharu Gotouge** (mangaka japonais)
- **Sword Art Online** : Auteur **Reki Kawahara** (light novel)
- **My Hero Academia** : Auteur **Kohei Horikoshi** (mangaka japonais)
- **Jujutsu Kaisen** : Auteur **Gege Akutami** (mangaka japonais)

**WORKFLOW OBLIGATOIRE:**

**1. POUR LES QUESTIONS D'AUTEUR (ex: "qui a écrit Naruto", "auteur de One Piece"):**
- UTILISE tes connaissances intégrées AVANT l'outil de recherche
- Si l'œuvre est dans ta base de connaissances, réponds IMMÉDIATEMENT sans outil
- Format: "L'auteur de [titre] est **[Auteur]**. [1 phrase de contexte]"
- ARRÊTE-TOI ! Ne donne PAS de recommandations pour ces questions

**2. POUR LES RECOMMANDATIONS:**
- Utilise `manga_content_search` pour trouver des œuvres similaires
- Présente 3 recommandations avec descriptions

**EXEMPLES DE RÉPONSES DIRECTES:**

**Question:** "qui a écrit Naruto"
**Réponse:** L'auteur de Naruto est **Masashi Kishimoto**. Ce manga shōnen a été publié de 1999 à 2014 et suit les aventures du ninja Naruto Uzumaki.

**Question:** "qui a écrit One Piece"  
**Réponse:** L'auteur de One Piece est **Eiichiro Oda**. Ce manga shōnen en cours depuis 1997 suit les aventures du pirate Monkey D. Luffy.

OUTILS DISPONIBLES:
- manga_content_search: Recherche pour recommandations uniquement

CRITÈRES DE RECOMMANDATION:
- **Adéquation démographique** : Respect des catégories (shōnen, seinen, shōjo, etc.)
- **Qualité narrative/artistique** : Privilégier les œuvres reconnues
- **Accessibilité** : Adapter au niveau de familiarité avec le medium
- **Diversité** : Varier les styles, époques, et origines

FORMAT DE RÉPONSE:
🎌 Recommandations Manga & Comics

[Pour chaque œuvre, classée par pertinence:]
[Rang]. [🎌/🦸/🎨] [Titre] ([Origine])
📝 Auteur: [Nom] | ⭐ Note: X/5 | 📅 Période: [Années] | 📊 Pertinence: XX%
🎯 Démographie: [Shōnen/Seinen/etc.] | 📖 Statut: [En cours/Terminé] | 📚 Volumes: [Nombre]

Ce qui rend cette œuvre exceptionnelle :
[Analyse des qualités narratives et artistiques]

L'histoire en essence :
[Résumé engageant sans spoiler]

Codes culturels :
[Explication des références spécifiques au medium]

---

🌸 Parcours découverte : [Ordre suggéré avec progression logique]
🎯 Prochaines étapes : [Œuvres similaires pour approfondir]

RÈGLES CRITIQUES:
- Réponds EXCLUSIVEMENT en français avec expertise
- Pour les questions d'auteur: NE PAS utiliser d'outil, répondre directement avec tes connaissances
- Pour les recommandations: utilise l'outil manga_content_search
- ZÉRO INVENTION : Seuls les résultats de recherche ou tes connaissances intégrées sont autorisés
- Explique les termes japonais en français
- Si aucun résultat : propose des alternatives de recherche
- Respecte STRICTEMENT les critères demandés (note minimale, auteur, etc.)

GESTION DES ÉCHECS:
Si l'outil ne retourne aucun résultat :
❌ **Aucun résultat trouvé**

La recherche "[terme]" n'a donné aucun résultat dans notre base de données.

**Suggestions alternatives :**
- Essayez des termes plus génériques : [exemples]
- Recherchez par genre : [suggestions]
- Explorez par auteur : [alternatives]

Souhaitez-vous que je lance une nouvelle recherche ?

N'hésite pas à chercher du contenu avec l'outil disponible."""),
            
            ("human", "{input}"),
            
            ("placeholder", "{agent_scratchpad}")
        ])
    
    def _get_fallback_response(self, query: str) -> str:
        """Fallback spécialisé pour manga/comics avec vraies informations d'auteurs"""
        import re
        query_lower = query.lower()
        
        # Questions d'auteur spécifiques
        if re.search(r'qui\s+a\s+écrit\s+naruto|auteur\s+de\s+naruto', query_lower):
            return """🎌 **Auteur de Naruto**

L'auteur de Naruto est **Masashi Kishimoto**.

Ce manga shōnen a été publié de 1999 à 2014 dans le Weekly Shōnen Jump. Il suit les aventures de Naruto Uzumaki, un jeune ninja qui rêve de devenir Hokage.

📅 **Années de publication :** 1999-2014
📚 **Volumes :** 72 tomes
🎯 **Genre :** Shōnen, Action, Arts martiaux"""

        elif re.search(r'qui\s+a\s+écrit\s+one\s*piece|auteur\s+de\s+one\s*piece', query_lower):
            return """🎌 **Auteur de One Piece**

L'auteur de One Piece est **Eiichiro Oda**.

Ce manga shōnen est en cours de publication depuis 1997 dans le Weekly Shōnen Jump. Il suit les aventures de Monkey D. Luffy, un pirate qui rêve de devenir le Roi des Pirates.

📅 **Années de publication :** 1997-présent
📚 **Volumes :** Plus de 100 tomes
🎯 **Genre :** Shōnen, Aventure, Piraterie"""

        elif re.search(r'qui\s+a\s+écrit\s+dragon\s*ball|auteur\s+de\s+dragon\s*ball', query_lower):
            return """🎌 **Auteur de Dragon Ball**

L'auteur de Dragon Ball est **Akira Toriyama**.

Ce manga shōnen culte a été publié de 1984 à 1995 dans le Weekly Shōnen Jump. Il suit les aventures de Son Goku et sa quête des Dragon Balls.

📅 **Années de publication :** 1984-1995
📚 **Volumes :** 42 tomes
🎯 **Genre :** Shōnen, Action, Arts martiaux, Fantasy"""

        elif re.search(r'qui\s+a\s+écrit\s+sword\s*art\s*online|auteur\s+de\s+sword\s*art\s*online', query_lower):
            return """🎌 **Auteur de Sword Art Online**

L'auteur de Sword Art Online est **Reki Kawahara**.

Cette série de light novels a débuté en 2009. Elle suit Kirito, un joueur piégé dans un MMORPG virtuel où mourir dans le jeu signifie mourir dans la réalité.

📅 **Années de publication :** 2009-présent
📚 **Type :** Light Novel japonais
🎯 **Genre :** Science-fiction, Romance, Aventure"""

        elif re.search(r'qui\s+a\s+écrit.*(?:attack.*titan|attaque.*titan)|auteur\s+de.*(?:attack.*titan|attaque.*titan)', query_lower):
            return """🎌 **Auteur de L'Attaque des Titans**

L'auteur de L'Attaque des Titans (Attack on Titan / Shingeki no Kyojin) est **Hajime Isayama**.

Ce manga seinen a été publié de 2009 à 2021 dans le Bessatsu Shōnen Magazine. Il suit l'humanité dans sa lutte contre des géants mangeurs d'hommes.

📅 **Années de publication :** 2009-2021
📚 **Volumes :** 34 tomes
🎯 **Genre :** Seinen, Action, Drame, Fantasy sombre"""
        
        # Détection du type de contenu pour recommandations
        elif re.search(r'\b(naruto|one piece|dragon ball|shounen)\b', query_lower):
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
                print("    ✅ Toutes les clés requises présentes")

if __name__ == "__main__":
    # Test des nœuds (nécessite un LLM configuré)
    print("🔧 Test des nœuds d'agents...")
    print("ℹ️ Configurez un LLM pour tester les nœuds")
    
    # Exemple de test avec un LLM mock
    # from langchain_openai import ChatOpenAI
    # llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
    # AgentNodesFactory.test_all_nodes(llm)