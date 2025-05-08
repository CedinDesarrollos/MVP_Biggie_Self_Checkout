import os
from flask import Flask
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()  # Cargar variables del archivo .env

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'supersecreto123')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    
    # Cargar productos en caché al iniciar la app
    from .routes.main import main_bp, cargar_productos_cache
    app.register_blueprint(main_bp)
    cargar_productos_cache()  # Cargar productos en caché al iniciar

    return app
