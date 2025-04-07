from rest_framework import serializers
from ..models import Video

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'title', 'description', 'video_1080p', 'video_720p', 'video_480p','thumbnail','category']
