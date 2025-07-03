from rest_framework import serializers
from .models import ConversationHistory, Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'content', 'tokens_used', 'processing_time', 
            'rag_sources', 'similarity_scores', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ConversationHistorySerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = ConversationHistory
        fields = [
            'id', 'user_email', 'agent_type', 'title', 'session_id', 
            'created_at', 'updated_at', 'messages', 'message_count', 'last_message'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user_email']
    
    def get_message_count(self, obj):
        return obj.messages.count()
    
    def get_last_message(self, obj):
        last_message = obj.messages.last()
        if last_message:
            return {
                'content': last_message.content[:100] + '...' if len(last_message.content) > 100 else last_message.content,
                'sender': last_message.sender,
                'created_at': last_message.created_at
            }
        return None


class ConversationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationHistory
        fields = ['agent_type', 'title']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    



    