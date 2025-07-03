"""
Vue Django pour les agents LangChain
"""
import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from agents.simple_agents import SimpleAgentManager

logger = logging.getLogger(__name__)

# Instance globale du manager d'agents
agent_manager = None

def get_agent_manager():
    """Obtient ou crée l'instance du manager d'agents"""
    global agent_manager
    if agent_manager is None:
        try:
            agent_manager = SimpleAgentManager()
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du manager d'agents: {e}")
            return None
    return agent_manager

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def langchain_chat(request):
    """
    API endpoint pour interagir avec les agents LangChain
    
    Body:
    {
        "message": "votre question",
        "agent_type": "router|tech|literature"  // optionnel, défaut: router
    }
    """
    try:
        # Récupérer les données de la requête
        message = request.data.get('message', '').strip()
        agent_type = request.data.get('agent_type', 'router').lower()
        
        if not message:
            return Response({
                'error': 'Le message ne peut pas être vide'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if agent_type not in ['router', 'tech', 'literature']:
            return Response({
                'error': 'Type d\'agent invalide. Utilisez: router, tech, ou literature'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtenir le manager d'agents
        manager = get_agent_manager()
        if manager is None:
            return Response({
                'error': 'Service d\'agents temporairement indisponible'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # Obtenir la réponse de l'agent
        response = manager.get_agent_response(message, agent_type)
        
        return Response({
            'message': message,
            'agent_type': agent_type,
            'response': response,
            'status': 'success'
        })
    
    except Exception as e:
        logger.error(f"Erreur dans langchain_chat: {e}")
        return Response({
            'error': f'Erreur interne: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def agent_status(request):
    """
    Vérifie le statut des agents LangChain
    """
    try:
        manager = get_agent_manager()
        
        if manager is None:
            return Response({
                'status': 'unavailable',
                'message': 'Agents non disponibles'
            })
        
        return Response({
            'status': 'available',
            'provider': 'Simple RAG-based agents',
            'agents': {
                'router': 'Actif',
                'tech': 'Actif', 
                'literature': 'Actif'
            }
        })
    
    except Exception as e:
        logger.error(f"Erreur dans agent_status: {e}")
        return Response({
            'status': 'error',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def tech_agent_direct(request):
    """
    Interaction directe avec l'agent technique
    """
    try:
        message = request.data.get('message', '').strip()
        
        if not message:
            return Response({
                'error': 'Le message ne peut pas être vide'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        manager = get_agent_manager()
        if manager is None:
            return Response({
                'error': 'Agent technique indisponible'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        response = manager.get_agent_response(message, 'tech')
        
        return Response({
            'agent': 'tech',
            'message': message,
            'response': response
        })
    
    except Exception as e:
        logger.error(f"Erreur dans tech_agent_direct: {e}")
        return Response({
            'error': f'Erreur: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def literature_agent_direct(request):
    """
    Interaction directe avec l'agent littéraire
    """
    try:
        message = request.data.get('message', '').strip()
        
        if not message:
            return Response({
                'error': 'Le message ne peut pas être vide'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        manager = get_agent_manager()
        if manager is None:
            return Response({
                'error': 'Agent littéraire indisponible'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        response = manager.get_agent_response(message, 'literature')
        
        return Response({
            'agent': 'literature',
            'message': message,
            'response': response
        })
    
    except Exception as e:
        logger.error(f"Erreur dans literature_agent_direct: {e}")
        return Response({
            'error': f'Erreur: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)