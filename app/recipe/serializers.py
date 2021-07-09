from rest_framework import serializers
from core.models import Tag


class TagSerializer(serializers.ModelSerializer):
    """Serializer fr the tag objects"""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_field = ('id',)
