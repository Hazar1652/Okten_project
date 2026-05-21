from rest_framework import serializers
from .models import News


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = [
            'id', 'venue', 'title', 'content', 'category',
            'is_paid', 'image', 'published_at', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


class NewsListSerializer(serializers.ModelSerializer):
    """Легкий серіалізатор для списків — без важких полів"""
    class Meta:
        model = News
        fields = ['id', 'venue', 'title', 'category', 'is_paid', 'published_at']