from rest_framework import status, generics
from ..models import Video
from .serializers import VideoSerializer

class VideoListAPIView(generics.ListAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
