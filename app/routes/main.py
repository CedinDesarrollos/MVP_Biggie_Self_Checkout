from flask import Blueprint, render_template, jsonify, request
from sqlalchemy import text
import json
import uuid
from .. import db  # Importamos el objeto de base de datos global

main_bp = Blueprint('main', __name__)

# Caché de productos (inicialmente vacío)
productos_cache = {}

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/checkout')
def checkout():
    return render_template('checkout.html', productos=productos_cache)

@main_bp.route('/historico')
def historico():
    return render_template('historico.html')

@main_bp.route('/perfil')
def perfil():
    return render_template('perfil.html')

@main_bp.route('/confirmar_pago')
def confirmar_pago():
    return render_template('confirmar_pago.html')

@main_bp.route('/obtener_facturas')
def obtener_facturas():
    return render_template('obtener_facturas.html')

@main_bp.route('/controlar_facturas')
def controlar_facturas():
    return render_template('controlar_facturas.html')

@main_bp.route('/guardar_compra', methods=['POST'])
def guardar_compra():
    try:
        data = request.get_json()
        nombre = data.get("nombre")
        cedula = data.get("cedula")
        total = float(data.get("total"))
        productos = data.get("productos")

        if not nombre or not cedula or not productos:
            return jsonify({"success": False, "message": "Datos incompletos"}), 400

        # Generar nro_ticket único
        nro_ticket = str(uuid.uuid4())[:8]
        qr_content = json.dumps({
            "nro_ticket": nro_ticket,
            "cliente_nombre": nombre,
            "cliente_cedula": cedula,
            "total": total,
            "productos": productos
        })

        print(f"📝 Guardando compra: {qr_content}")

        # Guardar en la tabla compras (con db.session)
        db.session.execute(text("""
            INSERT INTO compras (nro_ticket, sucursal, total, qr_code, cliente_nombre, cliente_cedula)
            VALUES (:nro_ticket, 'suc_01', :total, :qr_code, :cliente_nombre, :cliente_cedula)
        """), {
            "nro_ticket": nro_ticket,
            "total": total,
            "qr_code": qr_content,
            "cliente_nombre": nombre,
            "cliente_cedula": cedula
        })

        print("✅ Compra guardada en la tabla compras")

        # Guardar en la tabla detalles_compra
        for producto in productos:
            db.session.execute(text("""
                INSERT INTO detalles_compra (nro_ticket, codigo_producto, nombre_producto, cantidad, precio_unitario, subtotal)
                VALUES (:nro_ticket, :codigo_producto, :nombre_producto, :cantidad, :precio_unitario, :subtotal)
            """), {
                "nro_ticket": nro_ticket,
                "codigo_producto": producto['upc'],
                "nombre_producto": producto['name'],
                "cantidad": int(producto['cantidad']),
                "precio_unitario": float(producto['price']),
                "subtotal": float(producto['price']) * int(producto['cantidad'])
            })

        db.session.commit()  # Confirmar la transacción
        print("✅ Detalles de compra guardados")

        return jsonify({"success": True, "message": "Compra guardada correctamente"})
    
    except Exception as e:
        print("🚨 Error al guardar la compra:", str(e))
        db.session.rollback()  # Revertir si ocurre un error
        return jsonify({"success": False, "message": "Error al guardar la compra.", "error": str(e)}), 500


@main_bp.route('/obtener_historico')
def obtener_historico():
    try:
        query = text("SELECT nro_ticket, fecha, total FROM compras ORDER BY fecha DESC")
        result = db.session.execute(query).mappings().all()
        return jsonify([dict(row) for row in result])
    except Exception as e:
        print("🚨 Error al obtener histórico:", str(e))
        return jsonify({"success": False, "message": "Error al obtener histórico.", "error": str(e)}), 500


@main_bp.route('/obtener_detalle/<nro_ticket>')
def obtener_detalle(nro_ticket):
    try:
        # Obtener el QR y los detalles de la compra en una sola consulta
        query_qr = text("SELECT qr_code FROM compras WHERE nro_ticket = :nro_ticket")
        qr_result = db.session.execute(query_qr, {"nro_ticket": nro_ticket}).scalar()

        query_detalle = text("""
            SELECT nombre_producto, cantidad, precio_unitario, subtotal 
            FROM detalles_compra 
            WHERE nro_ticket = :nro_ticket
        """)
        detalles_result = db.session.execute(query_detalle, {"nro_ticket": nro_ticket}).mappings().all()

        return jsonify({
            "qr_code": qr_result if qr_result else "",
            "detalles": [dict(row) for row in detalles_result]
        })
    except Exception as e:
        print("🚨 Error al obtener detalle de la compra:", str(e))
        return jsonify({"success": False, "message": "Error al obtener detalle de la compra.", "error": str(e)}), 500


# ✅ Mejoramos la función de caché de productos
def cargar_productos_cache():
    global productos_cache
    print("🔄 Cargando productos en caché...")
    
    query = text("SELECT upc, product_name, price FROM productos")
    result = db.session.execute(query).fetchall()
    
    # Convertir resultados en diccionario (caché)
    productos_cache = {str(row[0]): {"name": row[1], "price": row[2]} for row in result}
    print(f"✅ Productos cacheados: {len(productos_cache)}")
