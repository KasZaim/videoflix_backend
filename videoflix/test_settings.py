from .settings import *

# Use SQLite for tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'test_db.sqlite3',
    }
}

# Use console email backend for tests
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Create a directory for test media if it doesn't exist
import os
TEST_MEDIA_ROOT = os.path.join(BASE_DIR, 'test_media')
if not os.path.exists(TEST_MEDIA_ROOT):
    os.makedirs(TEST_MEDIA_ROOT)
MEDIA_ROOT = TEST_MEDIA_ROOT

# Disable Redis/RQ for tests
RQ_QUEUES = {
    'default': {
        'URL': 'memory://',
        'DEFAULT_TIMEOUT': 360,
    },
    'high': {
        'URL': 'memory://',
        'DEFAULT_TIMEOUT': 500,
    },
    'low': {
        'URL': 'memory://',
        'DEFAULT_TIMEOUT': 500,
    }
} 