from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/checkout')
def checkout():
    return render_template('checkout.html')

@main_bp.route('/historico')
def historico():
    return render_template('historico.html')

@main_bp.route('/perfil')
def perfil():
    return render_template('perfil.html')
