import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Security configurations
SECRET_KEY = os.environ.get("SECRET_KEY", "")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# File storage paths
UPLOAD_DIR = "uploads"
PROFILE_IMAGES_DIR = os.path.join(UPLOAD_DIR, "profile_images")

# Create directories if they don't exist
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
if not os.path.exists(PROFILE_IMAGES_DIR):
    os.makedirs(PROFILE_IMAGES_DIR)

# Database files
USER_DB_FILE = "users.json"
MESSAGE_DB_FILE = "messages.json"
GROUP_DB_FILE = "groups.json"
GROUP_MESSAGE_DB_FILE = "group_messages.json"