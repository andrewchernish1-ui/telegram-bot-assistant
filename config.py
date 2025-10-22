import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    LLM_API_KEY = os.getenv('LLM_API_KEY')
    CHANNEL_ID = os.getenv('CHANNEL_ID')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 5432))
    DB_NAME = os.getenv('DB_NAME', 'tgbot_db')
    DB_USER = os.getenv('DB_USER', 'tgbot_user')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'tgbot_password')

    DATABASE_URL = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

config = Config()
