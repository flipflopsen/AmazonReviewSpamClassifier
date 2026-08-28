from django.core.validators import MinValueValidator, MaxValueValidator
from rest_framework import serializers

from .models import ReviewData


class ReviewDataSerializer(serializers.Serializer):
    review_text = serializers.CharField(max_length=10000000)
    helpful = serializers.IntegerField(default=None, validators=[MinValueValidator(0), MaxValueValidator(1000000)])
    not_helpful = serializers.IntegerField(default=None, validators=[MinValueValidator(0), MaxValueValidator(1000000)])
    stars = serializers.IntegerField(default=None, validators=[MinValueValidator(1), MaxValueValidator(5)])

    def create(self, validated_data):
        return ReviewData(**validated_data)

    def update(self, instance, validated_data):
        instance.review_text = validated_data.get('review_text', instance.email)
        instance.helpful = validated_data.get('helpful', instance.content)
        instance.not_helpful = validated_data.get('not_helpful', instance.created)
        instance.stars = validated_data.get('stars', instance.created)
        return instance
