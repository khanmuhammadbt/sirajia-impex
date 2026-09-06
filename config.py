import os
import secrets
from dotenv import load_dotenv


load_dotenv()

class config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data.db'
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'Admin')
    ADMIN_PASSWORD_HASH = os.environ.get('ADMIN_PASSWORD_HASH')