from flask import Blueprint, render_template, jsonify, current_app
from sqlalchemy import create_engine, text
import os

main_bp = Blueprint('main', __name__)

# Caché de productos
productos_cache = {}

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/checkout')
def checkout():
    from .main import productos_cache
    return render_template('checkout.html', productos=productos_cache)

@main_bp.route('/historico')
def historico():
    return render_template('historico.html')

@main_bp.route('/perfil')
def perfil():
    return render_template('perfil.html')

def cargar_productos_cache():
    global productos_cache
    print("🔄 Cargando productos en caché...")
    
    # Usar create_engine de SQLAlchemy
    engine = create_engine(os.getenv('SQLALCHEMY_DATABASE_URI'))
    
    with engine.connect() as connection:
        query = text("SELECT upc, product_name, price FROM productos")
        result = connection.execute(query).fetchall()
        
        # Convertir resultados en diccionario (caché)
        productos_cache = {str(row[0]): {"name": row[1], "price": row[2]} for row in result}
    
    print(f"✅ Productos cacheados: {len(productos_cache)}")
