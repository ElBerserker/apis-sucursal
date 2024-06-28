from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from config import config as cn

# Configuración de la aplicación y la base de datos
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = cn.DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuración de CORS
CORS(app)
CORS(app, resources={r"/*": {"origins": "*"}})

# Inicialización de SQLAlchemy y Marshmallow
db = SQLAlchemy(app)
ma = Marshmallow(app)

# Definición del modelo Categoria
class Categoria(db.Model):
    id_categoria = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.String(255), nullable=False)

    def __init__(self, nombre, descripcion):
        self.nombre = nombre
        self.descripcion = descripcion

# Definición del modelo Marca
class Marca(db.Model):
    id_marca = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)

    def __init__(self, nombre):
        self.nombre = nombre

# Definición del modelo Presentacion
class Presentacion(db.Model):
    id_presentacion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.String(255), nullable=False)

    def __init__(self, nombre, descripcion):
        self.nombre = nombre
        self.descripcion = descripcion

# Definición del modelo Producto
class Producto(db.Model):
    codigo_barras = db.Column(db.String(255), primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.String(255), nullable=False)
    id_categoria = db.Column(db.Integer, db.ForeignKey('categoria.id_categoria'), nullable=True)
    id_presentacion = db.Column(db.Integer, db.ForeignKey('presentacion.id_presentacion'), nullable=True)
    id_marca = db.Column(db.Integer, db.ForeignKey('marca.id_marca'), nullable=True)
    cantidad_actual = db.Column(db.Integer, nullable=False)
    cantidad_maxima = db.Column(db.Integer, nullable=False)
    cantidad_minima = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Numeric(10,2), nullable=False)
    estado = db.Column(db.String(255), nullable=False)

    def __init__(self, codigo_barras, nombre, descripcion, id_categoria, id_presentacion, id_marca, cantidad_actual, cantidad_maxima, cantidad_minima, precio, estado):
        self.codigo_barras = codigo_barras
        self.nombre = nombre
        self.descripcion = descripcion
        self.id_categoria = id_categoria
        self.id_presentacion = id_presentacion
        self.id_marca = id_marca
        self.cantidad_actual = cantidad_actual
        self.cantidad_maxima = cantidad_maxima
        self.cantidad_minima = cantidad_minima
        self.precio = precio
        self.estado = estado

# Definición del modelo Proveedor
class Proveedor(db.Model):
    rfc_proveedor = db.Column(db.String(255), primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    telefono = db.Column(db.String(255), nullable=False)
    correo = db.Column(db.String(255), nullable=False)

    def __init__(self, rfc_proveedor, nombre, telefono, correo):
        self.rfc_proveedor = rfc_proveedor
        self.nombre = nombre
        self.telefono = telefono
        self.correo = correo

# Definición del modelo Rol
class Rol(db.Model):
    id_rol = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.String(255), nullable=False)

    def __init__(self, nombre, descripcion):
        self.nombre = nombre
        self.descripcion = descripcion

# Definición del modelo Usuario
class Usuario(db.Model):
    clv_usuario = db.Column(db.String(18), primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    apellido1 = db.Column(db.String(255), nullable=False)
    apellido2 = db.Column(db.String(255), nullable=False)
    telefono = db.Column(db.String(255), nullable=False)
    correo = db.Column(db.String(255), nullable=False)
    direccion = db.Column(db.String(255), nullable=False)
    id_rol = db.Column(db.Integer, db.ForeignKey('rol.id_rol'), nullable=True)
    contrasenia = db.Column(db.String(255), nullable=False)

    def __init__(self, clv_usuario, nombre, apellido1, apellido2, telefono, correo, direccion, id_rol, contrasenia):
        self.clv_usuario = clv_usuario
        self.nombre = nombre
        self.apellido1 = apellido1
        self.apellido2 = apellido2
        self.telefono = telefono
        self.correo = correo
        self.direccion = direccion
        self.id_rol = id_rol
        self.contrasenia = contrasenia

# Definición del modelo Sesion
class Sesion(db.Model):
    folio_sesion = db.Column(db.String(18), primary_key=True)
    clv_usuario = db.Column(db.String(18), db.ForeignKey('usuario.clv_usuario'), nullable=True)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_final = db.Column(db.Date, nullable=False)
    estado = db.Column(db.String(255), nullable=False)

    def __init__(self, folio_sesion, clv_usuario, fecha_inicio, fecha_final, estado):
        self.folio_sesion = folio_sesion
        self.clv_usuario = clv_usuario
        self.fecha_inicio = fecha_inicio
        self.fecha_final = fecha_final
        self.estado = estado

# Definición del modelo Compra
class Compra(db.Model):
    folio_compra = db.Column(db.String(18), primary_key=True)
    rfc_proveedor = db.Column(db.String(255), db.ForeignKey('proveedor.rfc_proveedor'), nullable=False)
    folio_sesion = db.Column(db.String(18), db.ForeignKey('sesion.folio_sesion'), nullable=False)
    fecha_compra = db.Column(db.Date, nullable=False)
    total_compra = db.Column(db.Numeric(10,2), nullable=False)

    def __init__(self, folio_compra, rfc_proveedor, folio_sesion, fecha_compra, total_compra):
        self.folio_compra = folio_compra
        self.rfc_proveedor = rfc_proveedor
        self.folio_sesion = folio_sesion
        self.fecha_compra = fecha_compra
        self.total_compra = total_compra

# Definición del modelo DetalleCompra
class DetalleCompra(db.Model):
    id_detalle_compra = db.Column(db.Integer, primary_key=True, autoincrement=True)
    folio_compra = db.Column(db.String(18), db.ForeignKey('compra.folio_compra'), nullable=True)
    codigo_barras = db.Column(db.String(255), db.ForeignKey('producto.codigo_barras'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_compra = db.Column(db.Numeric(10,2), nullable=False)

    def __init__(self, folio_compra, codigo_barras, cantidad, precio_compra):
        self.folio_compra = folio_compra
        self.codigo_barras = codigo_barras
        self.cantidad = cantidad
        self.precio_compra = precio_compra

# Definición del esquema de marshmallow para serializar los modelos
class DetalleCompraSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = DetalleCompra
        include_fk = True

# Inicialización de los esquemas
detalle_compra_schema = DetalleCompraSchema()
detalles_compra_schema = DetalleCompraSchema(many=True)

# Rutas para DetalleCompra
@app.route('/detalle_compra', methods=['POST'])
def add_detalle_compra():
    folio_compra = request.json['folio_compra']
    codigo_barras = request.json['codigo_barras']
    cantidad = request.json['cantidad']
    precio_compra = request.json['precio_compra']
    new_detalle_compra = DetalleCompra(folio_compra, codigo_barras, cantidad, precio_compra)
    db.session.add(new_detalle_compra)
    db.session.commit()
    return detalle_compra_schema.jsonify(new_detalle_compra)

@app.route('/detalle_compra', methods=['GET'])
def get_detalles_compra():
    all_detalles_compra = DetalleCompra.query.all()
    result = detalles_compra_schema.dump(all_detalles_compra)
    return jsonify(result)

@app.route('/detalle_compra/<id>', methods=['GET'])
def get_detalle_compra(id):
    detalle_compra = DetalleCompra.query.get(id)
    if not detalle_compra:
        return jsonify({"message": "DetalleCompra not found"}), 404
    return detalle_compra_schema.jsonify(detalle_compra)

@app.route('/detalle_compra/<id>', methods=['PUT'])
def update_detalle_compra(id):
    detalle_compra = DetalleCompra.query.get(id)
    if not detalle_compra:
        return jsonify({"message": "DetalleCompra not found"}), 404

    folio_compra = request.json['folio_compra']
    codigo_barras = request.json['codigo_barras']
    cantidad = request.json['cantidad']
    precio_compra = request.json['precio_compra']

    detalle_compra.folio_compra = folio_compra
    detalle_compra.codigo_barras = codigo_barras
    detalle_compra.cantidad = cantidad
    detalle_compra.precio_compra = precio_compra

    db.session.commit()
    return detalle_compra_schema.jsonify(detalle_compra)

@app.route('/detalle_compra/<id>', methods=['DELETE'])
def delete_detalle_compra(id):
    detalle_compra = DetalleCompra.query.get(id)
    if not detalle_compra:
        return jsonify({"message": "DetalleCompra not found"}), 404

    db.session.delete(detalle_compra)
    db.session.commit()
    return jsonify({"message": "DetalleCompra deleted successfully"})

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=True, port=4040, host="localhost")

