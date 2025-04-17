from rest_framework import serializers
from ..models import Video
from django.conf import settings

class VideoSerializer(serializers.ModelSerializer):
    video_1080p = serializers.SerializerMethodField()
    video_720p = serializers.SerializerMethodField()
    video_480p = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ['id', 'title', 'description', 'video_1080p', 'video_720p', 'video_480p', 'thumbnail', 'category']

    def get_video_1080p(self, obj):
        if obj.video_1080p:
            return self.context['request'].build_absolute_uri(obj.video_1080p.url)
        return None

    def get_video_720p(self, obj):
        if obj.video_720p:
            return self.context['request'].build_absolute_uri(obj.video_720p.url)
        return None

    def get_video_480p(self, obj):
        if obj.video_480p:
            return self.context['request'].build_absolute_uri(obj.video_480p.url)
        return None
