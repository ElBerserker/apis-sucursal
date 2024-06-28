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
    precio = db.Column(db.Numeric(10, 2), nullable=False)
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

# Definición del modelo Venta
class Venta(db.Model):
    folio_venta = db.Column(db.String(18), primary_key=True)
    folio_sesion = db.Column(db.String(18), db.ForeignKey('sesion.folio_sesion'), nullable=False)
    clv_cliente = db.Column(db.String(18), db.ForeignKey('cliente.clv_cliente'), nullable=False)
    fecha_venta = db.Column(db.Date, nullable=False)
    total_venta = db.Column(db.Numeric(10, 2), nullable=False)

    def __init__(self, folio_venta, folio_sesion, clv_cliente, fecha_venta, total_venta):
        self.folio_venta = folio_venta
        self.folio_sesion = folio_sesion
        self.clv_cliente = clv_cliente
        self.fecha_venta = fecha_venta
        self.total_venta = total_venta

# Definición del modelo Cliente
class Cliente(db.Model):
    clv_cliente = db.Column(db.String(18), primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    apellido1 = db.Column(db.String(255), nullable=False)
    apellido2 = db.Column(db.String(255), nullable=False)
    telefono = db.Column(db.String(255), nullable=False)
    correo = db.Column(db.String(255), nullable=False)

    def __init__(self, clv_cliente, nombre, apellido1, apellido2, telefono, correo):
        self.clv_cliente = clv_cliente
        self.nombre = nombre
        self.apellido1 = apellido1
        self.apellido2 = apellido2
        self.telefono = telefono
        self.correo = correo

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

# Definición del modelo Rol
class Rol(db.Model):
    id_rol = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.String(255), nullable=False)

    def __init__(self, nombre, descripcion):
        self.nombre = nombre
        self.descripcion = descripcion

# Definición del modelo DetalleVenta
class DetalleVenta(db.Model):
    id_detalle_venta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    folio_venta = db.Column(db.String(18), db.ForeignKey('venta.folio_venta'), nullable=True)
    codigo_barras = db.Column(db.String(255), db.ForeignKey('producto.codigo_barras'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_venta = db.Column(db.Numeric(10, 2), nullable=False)

    def __init__(self, folio_venta, codigo_barras, cantidad, precio_venta):
        self.folio_venta = folio_venta
        self.codigo_barras = codigo_barras
        self.cantidad = cantidad
        self.precio_venta = precio_venta

# Definición del esquema de marshmallow para serializar los modelos
class DetalleVentaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = DetalleVenta
        include_fk = True

# Inicialización de los esquemas
detalle_venta_schema = DetalleVentaSchema()
detalles_venta_schema = DetalleVentaSchema(many=True)

# Rutas para DetalleVenta
@app.route('/detalle_venta', methods=['POST'])
def add_detalle_venta():
    folio_venta = request.json['folio_venta']
    codigo_barras = request.json['codigo_barras']
    cantidad = request.json['cantidad']
    precio_venta = request.json['precio_venta']
    
    new_detalle_venta = DetalleVenta(folio_venta, codigo_barras, cantidad, precio_venta)
    db.session.add(new_detalle_venta)
    db.session.commit()
    
    return detalle_venta_schema.jsonify(new_detalle_venta)

@app.route('/detalle_venta', methods=['GET'])
def get_detalles_venta():
    all_detalles_venta = DetalleVenta.query.all()
    result = detalles_venta_schema.dump(all_detalles_venta)
    return jsonify(result)

@app.route('/detalle_venta/<id>', methods=['GET'])
def get_detalle_venta(id):
    detalle_venta = DetalleVenta.query.get(id)
    return detalle_venta_schema.jsonify(detalle_venta)

@app.route('/detalle_venta/<id>', methods=['PUT'])
def update_detalle_venta(id):
    detalle_venta = DetalleVenta.query.get(id)
    
    folio_venta = request.json['folio_venta']
    codigo_barras = request.json['codigo_barras']
    cantidad = request.json['cantidad']
    precio_venta = request.json['precio_venta']
    
    detalle_venta.folio_venta = folio_venta
    detalle_venta.codigo_barras = codigo_barras
    detalle_venta.cantidad = cantidad
    detalle_venta.precio_venta = precio_venta
    
    db.session.commit()
    
    return detalle_venta_schema.jsonify(detalle_venta)

@app.route('/detalle_venta/<id>', methods=['DELETE'])
def delete_detalle_venta(id):
    detalle_venta = DetalleVenta.query.get(id)
    db.session.delete(detalle_venta)
    db.session.commit()
    
    return detalle_venta_schema.jsonify(detalle_venta)

if __name__ == '__main__':
    app.run(debug=True, host="localhost", port=4046)

