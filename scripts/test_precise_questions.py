#!/usr/bin/env python3
"""
Test des réponses précises sans recommandations non sollicitées
"""
import os
import sys
import django
from pathlib import Path

# Configuration Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

django.setup()

def test_agent_response_types():
    """Test que l'agent distingue les types de questions"""
    from agents.langchain_agents.nodes.agent_nodes import LiteratureAgentNode
    from langchain_community.llms import Ollama
    
    print("🎯 Test des types de réponses")
    print("=" * 50)
    
    try:
        # Utiliser un LLM factice pour tester le prompt
        class MockLLM:
            def invoke(self, messages, **kwargs):
                # Analyser le prompt pour voir s'il contient les bonnes instructions
                if isinstance(messages, list):
                    system_msg = messages[0].content if messages else ""
                    user_msg = messages[-1].content if len(messages) > 1 else ""
                elif hasattr(messages, 'to_messages'):
                    msgs = messages.to_messages()
                    system_msg = msgs[0].content if msgs else ""
                    user_msg = msgs[-1].content if len(msgs) > 1 else ""
                else:
                    system_msg = str(messages)
                    user_msg = ""
                
                # Vérifier que le prompt contient les bonnes instructions
                checks = {
                    "Instructions pour questions précises": "RÉPONSE COURTE UNIQUEMENT" in system_msg,
                    "Interdiction recommandations": "NE FAIS AUCUNE RECOMMANDATION" in system_msg,
                    "Exemples exacts": "EXEMPLES EXACTS DE TRAITEMENT" in system_msg,
                    "Règles absolues": "RÈGLES ABSOLUES" in system_msg,
                    "Wikipedia prioritaire": "wikipedia_search" in system_msg and "DIRECTEMENT" in system_msg
                }
                
                print("\n🔍 Vérification du prompt:")
                for check, result in checks.items():
                    status = "✅" if result else "❌"
                    print(f"   {status} {check}")
                
                # Simuler une réponse selon le type de question
                user_lower = user_msg.lower()
                
                if any(phrase in user_lower for phrase in ["qui a écrit", "auteur de", "qui est l'auteur"]):
                    return "L'auteur de cette œuvre est [Auteur identifié par Wikipedia]."
                elif any(phrase in user_lower for phrase in ["œuvres de", "livres de"]):
                    return "Voici les œuvres principales de cet auteur : [Liste des œuvres]"
                elif any(phrase in user_lower for phrase in ["recommande", "similaire", "comme"]):
                    return "Voici mes recommandations : [Liste de livres recommandés]"
                else:
                    return "Réponse adaptée au type de question."
            
            @property 
            def temperature(self):
                return 0.1
                
        mock_llm = MockLLM()
        
        # Créer l'agent avec le mock LLM
        lit_agent = LiteratureAgentNode(mock_llm)
        print("✅ Agent littérature créé avec mock LLM")
        
        # Tester différents types de questions
        test_questions = [
            ("Question précise", "Qui a écrit Les Misérables ?"),
            ("Question précise", "Qui est l'auteur de L'Étranger ?"),
            ("Question précise", "Auteur de Le Mythe de Sisyphe"),
            ("Demande d'œuvres", "œuvres de Stendhal"),
            ("Demande d'œuvres", "livres de Victor Hugo"),  
            ("Recommandation", "recommande-moi des livres"),
            ("Recommandation", "livres similaires à Camus")
        ]
        
        for question_type, question in test_questions:
            print(f"\n🔸 Type: {question_type}")
            print(f"❓ Question: '{question}'")
            
            try:
                result = lit_agent.agent_executor.invoke({
                    "input": question
                })
                
                response = result.get("output", "Pas de réponse")
                print(f"🤖 Réponse: {response}")
                
            except Exception as e:
                print(f"❌ Erreur: {e}")
        
        print(f"\n✅ Tests du prompt terminés!")
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")

def test_prompt_content():
    """Test direct du contenu du prompt"""
    print("\n📝 Test du contenu du prompt")
    print("=" * 40)
    
    try:
        from agents.langchain_agents.nodes.agent_nodes import LiteratureAgentNode
        from langchain_community.llms import Ollama
        
        class DummyLLM:
            pass
        
        lit_agent = LiteratureAgentNode(DummyLLM())
        prompt = lit_agent._create_prompt()
        
        # Convertir le prompt en messages pour l'analyser
        messages = prompt.format_messages(input="test", agent_scratchpad="")
        system_content = messages[0].content
        
        print("🔍 Vérification des instructions clés:")
        
        key_instructions = {
            "Questions précises identifiées": "QUESTIONS PRÉCISES" in system_content,
            "Workflow obligatoire": "WORKFLOW OBLIGATOIRE" in system_content,
            "Pas de recommandations": "NE FAIS AUCUNE RECOMMANDATION" in system_content,
            "Réponse courte": "RÉPONSE COURTE UNIQUEMENT" in system_content,
            "Exemples exacts": "EXEMPLES EXACTS" in system_content,
            "Règles absolues": "RÈGLES ABSOLUES" in system_content,
            "Wikipedia direct": "wikipedia_search" in system_content and "DIRECTEMENT" in system_content
        }
        
        all_good = True
        for instruction, present in key_instructions.items():
            status = "✅" if present else "❌"
            print(f"   {status} {instruction}")
            if not present:
                all_good = False
        
        if all_good:
            print("\n🎉 Toutes les instructions sont présentes dans le prompt !")
        else:
            print("\n⚠️ Certaines instructions manquent")
            
        # Afficher un extrait du prompt pour vérification
        print(f"\n📄 Extrait du prompt système (premiers 500 caractères):")
        print(f"   {system_content[:500]}...")
        
    except Exception as e:
        print(f"❌ Erreur test prompt: {e}")

def main():
    """Test complet"""
    print("🧪 Test complet - Questions précises vs Recommandations")
    print("=" * 70)
    
    # Test 1: Contenu du prompt
    test_prompt_content()
    
    # Test 2: Comportement de l'agent  
    test_agent_response_types()

if __name__ == "__main__":
    main()