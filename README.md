# Videoflix Backend

![Videoflix Logo](static/images/logo.png)

## Overview

Videoflix is a video streaming platform backend built with Django and Django REST Framework. It provides a robust API for user authentication, video management, and content delivery with support for multiple video qualities.

## Features

- **User Authentication System**
  - Email-based registration with verification
  - Token-based authentication
  - Password reset functionality
  - Custom user model with extended fields

- **Video Management**
  - Upload and manage video content
  - Automatic video transcoding to multiple qualities (1080p, 720p, 480p)
  - Thumbnail generation
  - Video categorization

- **API Endpoints**
  - RESTful API for all functionality
  - CORS support for frontend integration
  - Token-based authentication for secure access

- **Background Processing**
  - Redis-based task queue for video processing
  - Asynchronous video transcoding
  - Email sending via background workers


## Technology Stack

- **Backend Framework**: Django 5.1.4
- **API Framework**: Django REST Framework 3.15.2
- **Database**: SQLite (development), PostgreSQL (production)
- **Task Queue**: Redis Queue (RQ)
- **Authentication**: Token-based authentication
- **Email**: SMTP backend
- **Caching**: Redis

## Installation

### Prerequisites

- Python 3.8+
- Redis server
- PostgreSQL (for production)
- WSL (Windows Subsystem for Linux) with PostgreSQL installed

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/KasZaim/videoflix_backend.git
   cd videoflix_backend
   ```

2. Create and activate a virtual environment:
   ```bash
   # Windows
   python -m venv venv
   .venv\Scripts\activate

   # Linux/Mac
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory with the following variables:
   ```
   EMAIL_HOST=smtp.example.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@example.com
   EMAIL_HOST_PASSWORD=your-email-password

   FRONTEND_DOMAIN='http://localhost:4200' 
   BACKEND_DOMAIN='http://127.0.0.1:8000'
   ```

5. **WSL PostgreSQL Setup**:
   ```bash
   # In WSL terminal
   pip3 install -r requirements_lin.txt
   sudo service postgresql start
   sudo -u postgres psql
   
   # In PostgreSQL prompt
   CREATE DATABASE videoflix;
   \q
   ```

6. Run migrations:
   ```bash
   python manage.py migrate
   ```

7. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

8. Start the development server:
   ```bash
   python manage.py runserver
   ```

9. Start the Redis worker for background tasks:
   ```bash
   python manage.py rqworker --worker-class simpleworker.SimpleWorker
   ```


## Video Upload

### Accepted Video Formats
- MP4 (.mp4)
- AVI (.avi)
- MOV (.mov)
- MKV (.mkv)
- WMV (.wmv)
- FLV (.flv)
- WEBM (.webm)

### Upload Methods

#### 1. Django Admin Panel
1. Log in to the Django admin panel at `/admin/`
2. Navigate to "Videos" section
3. Click "Add Video"
4. Fill in the required fields:
   - Title
   - Description
   - Original Video File (select from your computer)
   - Thumbnail (optional, recommended size: 1280x720px)
   - Category (optional)
5. Click "Save"

#### 2. API Upload
Use the following endpoint to upload videos via API:

```http
POST /api/videos/
Content-Type: multipart/form-data

{
    "title": "Video Title",
    "description": "Video Description",
    "original_video_file": [binary file],
    "thumbnail": [binary file] (optional),
    "category": "Category Name" (optional)
}
```

**Note**: 
- Videos are automatically converted to multiple qualities (1080p, 720p, 480p)
- Thumbnails are optional but recommended
- All uploaded files are automatically deleted when the video is deleted

## API Endpoints

### Authentication

- `POST /api/auth/register/` - Register a new user
- `POST /api/auth/login/` - Login and receive authentication token
- `GET /api/auth/verify-email/<uidb64>/<token>/` - Verify email address
- `POST /api/auth/forgot-password/` - Request password reset
- `POST /api/auth/reset-password/` - Reset password

### Videos

- `GET /api/videos/` - List all videos
- `POST /api/videos/` - Upload a new video
- `GET /api/videos/<id>/` - Get video details
- `PUT /api/videos/<id>/` - Update video details
- `DELETE /api/videos/<id>/` - Delete a video

## Development

### Running Tests

```bash
python manage.py test
```

## Deployment

For production deployment, make sure to:

1. Set `DEBUG = False` in settings.py
2. Configure a proper database (PostgreSQL recommended)
3. Set up proper email settings
4. Configure proper CORS settings
5. Set up proper static and media file serving
6. Use a production-grade web server (Gunicorn, uWSGI)
7. Set up proper SSL/TLS

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Django and Django REST Framework teams
- Redis and RQ teams
- All contributors to this project 
