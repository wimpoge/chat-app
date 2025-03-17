import os

# Security configurations
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"  # Replace in production
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