from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, UserProfile, Genre, ProgrammingLanguage


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name', 'description']


class ProgrammingLanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgrammingLanguage
        fields = ['id', 'name', 'description']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password_confirm']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.create(user=user)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    favorite_genres = GenreSerializer(many=True, read_only=True)
    programming_languages = ProgrammingLanguageSerializer(many=True, read_only=True)
    favorite_genre_ids = serializers.PrimaryKeyRelatedField(
        queryset=Genre.objects.all(), 
        many=True, 
        write_only=True, 
        source='favorite_genres'
    )
    programming_language_ids = serializers.PrimaryKeyRelatedField(
        queryset=ProgrammingLanguage.objects.all(), 
        many=True, 
        write_only=True, 
        source='programming_languages'
    )
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'preferred_agent', 'reading_level', 'favorite_genres', 
            'favorite_authors', 'programming_languages', 'tech_interests', 
            'experience_level', 'bio', 'created_at', 'updated_at',
            'favorite_genre_ids', 'programming_language_ids'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']