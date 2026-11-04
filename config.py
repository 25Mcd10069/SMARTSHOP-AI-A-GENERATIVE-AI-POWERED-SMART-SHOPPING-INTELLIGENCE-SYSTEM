"""
ShopSmart AI - Configuration Module
Manages application configuration, paths, and environment variables securely.
"""

import os
from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables manually if python-dotenv is not installed
env_file = BASE_DIR / '.env'
if env_file.exists():
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    if key not in os.environ:
                        os.environ[key] = val
    except Exception:
        pass

class Config:
    """Application configuration parameters"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'shopsmart_ai_super_secret_key_2026_mca')
    
    # Database configuration (SQLite data warehouse)
    DATA_DIR = BASE_DIR / 'data'
    RAW_DATA_DIR = DATA_DIR / 'raw'
    DATABASE_PATH = DATA_DIR / 'shopsmart.db'
    
    # Generative AI (Gemini) configuration
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '').strip()
    GEMINI_MODEL = 'gemini-1.5-flash'
    
    # AWS Cloud configuration
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', '')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
    AWS_DEFAULT_REGION = os.environ.get('AWS_DEFAULT_REGION', 'ap-south-1')
    S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'shopsmart-ai-datasets')
