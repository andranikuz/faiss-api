import os

# Base storage directory for all persistent data
# Use local directory if not in Docker
if os.path.exists("/app"):
    default_storage = "/app/storage"
else:
    # Local development - use current directory
    default_storage = os.path.join(os.getcwd(), "storage")

STORAGE_DIR = os.getenv("STORAGE_DIR", default_storage)
DATA_DIR = os.path.join(STORAGE_DIR, "data")
INDEX_DIR = os.path.join(STORAGE_DIR, "index")

def ensure_directories():
    """Create storage directories if they don't exist"""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(INDEX_DIR, exist_ok=True)