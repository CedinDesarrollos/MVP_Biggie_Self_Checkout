from . import db

class Producto(db.Model):
    __tablename__ = 'productos'

    upc = db.Column(db.String, primary_key=True)
    product_name = db.Column(db.String)
    price = db.Column(db.Float)
    weight = db.Column(db.String)
    tax_percentage = db.Column(db.Float)

    def __repr__(self):
        return f'<Producto {self.product_name}>'
