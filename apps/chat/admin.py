from django.contrib import admin
from .models import ConversationHistory, Message


@admin.register(ConversationHistory)
class ConversationHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'agent_type', 'title', 'message_count', 'created_at', 'updated_at')
    list_filter = ('agent_type', 'created_at', 'updated_at')
    search_fields = ('user__email', 'title')
    readonly_fields = ('created_at', 'updated_at', 'message_count')
    ordering = ('-updated_at',)
    
    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Messages'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'sender', 'message_preview', 'created_at')
    list_filter = ('sender', 'created_at')
    search_fields = ('conversation__title', 'content')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    def message_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    message_preview.short_description = 'Message Preview'