from rest_framework import serializers
from core.models import Comment


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # or user id if you prefer

    class Meta:
        model = Comment
        fields = ['id', 'user', 'text', 'created_at']