from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    # API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/leads.db')
    
    # Scraping Settings
    SCRAPE_INTERVAL = int(os.getenv('SCRAPE_INTERVAL', 14400))  # 4 hours in seconds
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = 'logs/automation.log'
    
    # Gemini Settings
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_TEMPERATURE = 0.7
    GEMINI_TOP_P = 0.9
    GEMINI_TOP_K = 40 