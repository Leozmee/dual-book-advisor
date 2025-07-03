from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    def __str__(self):
        return self.email


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name


class ProgrammingLanguage(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name


class UserProfile(models.Model):
    AGENT_CHOICES = [
        ('tech', 'Tech Agent'),
        ('literature', 'Literature Agent'),
        ('both', 'Both Agents'),
    ]
    
    READING_LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    preferred_agent = models.CharField(max_length=20, choices=AGENT_CHOICES, default='both')
    reading_level = models.CharField(max_length=20, choices=READING_LEVEL_CHOICES, default='intermediate')
    
    # Literature preferences
    favorite_genres = models.ManyToManyField(Genre, blank=True)
    favorite_authors = models.TextField(blank=True, help_text="Comma-separated list of favorite authors")
    
    # Tech preferences
    programming_languages = models.ManyToManyField(ProgrammingLanguage, blank=True)
    tech_interests = models.TextField(blank=True, help_text="Comma-separated list of tech interests")
    experience_level = models.CharField(max_length=20, choices=READING_LEVEL_CHOICES, default='intermediate')
    
    # Personal preferences
    bio = models.TextField(blank=True, max_length=500)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email} - Profile"