from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ConversationHistory(models.Model):
    AGENT_CHOICES = [
        ('tech', 'Tech Agent'),
        ('literature', 'Literature Agent'),
        ('manga', 'Manga/Comics Agent'),
        ('coordinator', 'Agent Coordinateur'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    agent_type = models.CharField(max_length=20, choices=AGENT_CHOICES)
    title = models.CharField(max_length=200)
    
    # Conversation metadata
    session_id = models.UUIDField(blank=True, null=True, help_text="Session identifier for tracking")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name_plural = 'Conversation Histories'
        indexes = [
            models.Index(fields=['user', 'agent_type']),
            models.Index(fields=['updated_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.agent_type.title()} - {self.title}"


class Message(models.Model):
    SENDER_CHOICES = [
        ('user', 'User'),
        ('agent', 'Agent'),
    ]
    
    conversation = models.ForeignKey(ConversationHistory, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    content = models.TextField()
    
    # Message metadata
    tokens_used = models.IntegerField(null=True, blank=True, help_text="Number of tokens used for this message")
    processing_time = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True, help_text="Time taken to process message in seconds")
    
    # RAG metadata (for agent messages)
    rag_sources = models.JSONField(blank=True, null=True, help_text="Sources used for RAG retrieval")
    similarity_scores = models.JSONField(blank=True, null=True, help_text="Similarity scores for retrieved documents")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
            models.Index(fields=['sender']),
        ]
    
    def __str__(self):
        content_preview = self.content[:50] + '...' if len(self.content) > 50 else self.content
        return f"{self.sender}: {content_preview}"