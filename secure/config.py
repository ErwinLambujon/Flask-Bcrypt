import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'hey1021')
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    DATABASE = 'secure.db'