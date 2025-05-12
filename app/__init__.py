# app/__init__.py
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()  # Cargar variables del archivo .env

# Crear instancia global de SQLAlchemy
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'supersecreto123')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Desactivar alertas de modificación innecesarias

    # Inicializar la base de datos
    db.init_app(app)

    # Registrar el blueprint dentro del contexto de la aplicación
    with app.app_context():
        from app.routes.main import main_bp, cargar_productos_cache
        app.register_blueprint(main_bp)
        cargar_productos_cache()  # Cargar productos en caché al iniciar
    
    return app
