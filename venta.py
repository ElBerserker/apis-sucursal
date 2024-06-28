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

# Definición del modelo Venta
class Venta(db.Model):
    folio_venta = db.Column(db.String(18), primary_key=True)
    folio_sesion = db.Column(db.String(18), db.ForeignKey('sesion.folio_sesion'), nullable=False)
    clv_cliente = db.Column(db.String(18), db.ForeignKey('cliente.clv_cliente'), nullable=False)
    fecha_venta = db.Column(db.Date, nullable=False)
    total_venta = db.Column(db.Numeric(10,2), nullable=False)

    def __init__(self, folio_venta, folio_sesion, clv_cliente, fecha_venta, total_venta):
        self.folio_venta = folio_venta
        self.folio_sesion = folio_sesion
        self.clv_cliente = clv_cliente
        self.fecha_venta = fecha_venta
        self.total_venta = total_venta

with app.app_context():
    db.create_all()

# Definición del esquema Venta
class VentaSchema(ma.Schema):
    class Meta:
        fields = ('folio_venta', 'folio_sesion', 'clv_cliente', 'fecha_venta', 'total_venta')

# Instancias de los esquemas
venta_schema = VentaSchema()
ventas_schema = VentaSchema(many=True)

# GET todas las ventas
@app.route('/venta', methods=['GET'])
def obtenerVentas():
    todas_las_ventas = Venta.query.all()
    consulta_ventas = ventas_schema.dump(todas_las_ventas)
    return jsonify(consulta_ventas)

# GET una venta por folio
@app.route('/venta/<string:folio_venta>', methods=['GET'])
def obtenerVenta(folio_venta):
    una_venta = Venta.query.get(folio_venta)
    if una_venta is None:
        return jsonify({'message': 'Venta no encontrada'}), 404
    return venta_schema.jsonify(una_venta)

# POST nueva venta
@app.route('/venta/nueva_venta', methods=['POST'])
def insertar_venta():
    datosJSON = request.get_json(force=True)
    folio_venta = datosJSON.get('folio_venta')
    folio_sesion = datosJSON.get('folio_sesion')
    clv_cliente = datosJSON.get('clv_cliente')
    fecha_venta = datosJSON.get('fecha_venta')
    total_venta = datosJSON.get('total_venta')

    if not folio_venta or not folio_sesion or not clv_cliente or not fecha_venta or not total_venta:
        return jsonify({'message': 'Faltan datos necesarios'}), 400

    nueva_venta = Venta(folio_venta, folio_sesion, clv_cliente, fecha_venta, total_venta)
    db.session.add(nueva_venta)
    db.session.commit()
    return venta_schema.jsonify(nueva_venta), 201

# PUT actualizar venta
@app.route('/venta/actualizar_venta/<string:folio_venta>', methods=['PUT'])
def actualizarVenta(folio_venta):
    actualizar_venta = Venta.query.get(folio_venta)
    if actualizar_venta is None:
        return jsonify({'message': 'Venta no encontrada'}), 404

    datosJSON = request.get_json(force=True)
    actualizar_venta.folio_sesion = datosJSON.get('folio_sesion', actualizar_venta.folio_sesion)
    actualizar_venta.clv_cliente = datosJSON.get('clv_cliente', actualizar_venta.clv_cliente)
    actualizar_venta.fecha_venta = datosJSON.get('fecha_venta', actualizar_venta.fecha_venta)
    actualizar_venta.total_venta = datosJSON.get('total_venta', actualizar_venta.total_venta)

    db.session.commit()
    return venta_schema.jsonify(actualizar_venta)

# DELETE eliminar venta
@app.route('/venta/eliminar_venta/<string:folio_venta>', methods=['DELETE'])
def eliminarVenta(folio_venta):
    eliminar_venta = Venta.query.get(folio_venta)
    if eliminar_venta is None:
        return jsonify({'message': 'Venta no encontrada'}), 404

    db.session.delete(eliminar_venta)
    db.session.commit()
    return venta_schema.jsonify(eliminar_venta)

if __name__ == "__main__":
    app.run(debug=True, port=4044, host="localhost")

