from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from .models import Video
import os
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
import tempfile
from PIL import Image
import io
from unittest.mock import patch

class VideoListAPIViewTest(APITestCase):
    @patch('content.signals.django_rq.get_queue')
    def setUp(self, mock_get_queue):
        mock_queue = mock_get_queue.return_value
        mock_queue.enqueue.return_value = None
        
        self.client = APIClient()
        self.videos_url = reverse('videos')
        
        # Create a test video file
        self.video_file = SimpleUploadedFile(
            name='test_video.mp4',
            content=b'',  # Empty content for testing
            content_type='video/mp4'
        )
        
        # Create a test thumbnail
        image = Image.new('RGB', (100, 100), color='red')
        tmp_file = io.BytesIO()
        image.save(tmp_file, format='JPEG')
        tmp_file.seek(0)
        
        self.thumbnail = SimpleUploadedFile(
            name='test_thumbnail.jpg',
            content=tmp_file.read(),
            content_type='image/jpeg'
        )
        
        # Create test videos
        self.video1 = Video.objects.create(
            title='Test Video 1',
            description='Test Description 1',
            category='Test Category',
            original_video_file=self.video_file,
            thumbnail=self.thumbnail
        )
        
        self.video2 = Video.objects.create(
            title='Test Video 2',
            description='Test Description 2',
            category='Another Category',
            original_video_file=self.video_file,
            thumbnail=self.thumbnail
        )
    
    def tearDown(self):
        # Clean up files after test
        for video in Video.objects.all():
            if video.original_video_file:
                path = os.path.join(settings.MEDIA_ROOT, video.original_video_file.name)
                if os.path.exists(path):
                    os.remove(path)
            if video.thumbnail:
                path = os.path.join(settings.MEDIA_ROOT, video.thumbnail.name)
                if os.path.exists(path):
                    os.remove(path)
    
    @patch('content.signals.django_rq.get_queue')
    def test_get_video_list(self, mock_get_queue):
        """Test retrieving the list of videos"""
        # Mock the RQ queue to prevent Redis connection attempts
        mock_queue = mock_get_queue.return_value
        mock_queue.enqueue.return_value = None
        
        response = self.client.get(self.videos_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Should return both videos
        
        # Check that the video data is correctly returned
        video_titles = [video['title'] for video in response.data]
        self.assertIn('Test Video 1', video_titles)
        self.assertIn('Test Video 2', video_titles)
