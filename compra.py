from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from config import config as cn
from datetime import datetime

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
    folio_compra = db.Column(db.String(255), primary_key=True)
    folio_sesion = db.Column(db.String(18), db.ForeignKey('sesion.folio_sesion'), nullable=False)
    rfc_proveedor = db.Column(db.String(255), db.ForeignKey('proveedor.rfc_proveedor'), nullable=False)
    fecha_compra = db.Column(db.Date, nullable=False)
    total_compra = db.Column(db.Float, nullable=False)

    def __init__(self, folio_compra, folio_sesion, rfc_proveedor, fecha_compra, total_compra):
        self.folio_compra = folio_compra
        self.folio_sesion = folio_sesion
        self.rfc_proveedor = rfc_proveedor
        self.fecha_compra = fecha_compra
        self.total_compra = total_compra

with app.app_context():
    db.create_all()


# Definición del esquema Compra
class CompraSchema(ma.Schema):
    class Meta:
        fields = ('folio_compra', 'folio_sesion', 'rfc_proveedor', 'fecha_compra', 'total_compra')

# Instancias de los esquemas
compra_schema = CompraSchema()
compras_schema = CompraSchema(many=True)

# GET todas las compras
@app.route('/compra', methods=['GET'])
def obtenerCompras():
    todas_las_compras = Compra.query.all()
    consulta_compras = compras_schema.dump(todas_las_compras)
    return jsonify(consulta_compras)

# GET una compra por id
@app.route('/compra/<string:folio_compra>', methods=['GET'])
def obtenerCompra(folio_compra):
    una_compra = Compra.query.get(folio_compra)
    if una_compra is None:
        return jsonify({'message': 'Compra no encontrada'}), 404
    return compra_schema.jsonify(una_compra)

# POST nueva compra
@app.route('/compra/nueva_compra', methods=['POST'])
def insertar_compra():
    datosJSON = request.get_json(force=True)
    folio_compra = datosJSON.get('folio_compra')
    folio_sesion = datosJSON.get('folio_sesion')
    rfc_proveedor = datosJSON.get('rfc_proveedor')
    fecha_compra = datetime.strptime(datosJSON.get('fecha_compra'), '%Y-%m-%d').date()
    total_compra = datosJSON.get('total_compra')

    if not folio_sesion  or not folio_compra or not rfc_proveedor or not fecha_compra or total_compra is None:
        return jsonify({'message': 'Faltan datos necesarios'}), 400

    nueva_compra = Compra(folio_compra, folio_sesion, rfc_proveedor, fecha_compra, total_compra)
    db.session.add(nueva_compra)
    db.session.commit()
    return compra_schema.jsonify(nueva_compra), 201

# PUT actualizar compra
@app.route('/compra/actualizar_compra/<string:folio_compra>', methods=['PUT'])
def actualizarCompra(folio_compra):
    actualizar_compra = Compra.query.get(folio_compra)
    if actualizar_compra is None:
        return jsonify({'message': 'Compra no encontrada'}), 404

    datosJSON = request.get_json(force=True)
    actualizar_compra.folio_sesion = datosJSON.get('folio_sesion', actualizar_compra.folio_sesion)
    actualizar_compra.rfc_proveedor = datosJSON.get('rfc_proveedor', actualizar_compra.rfc_proveedor)
    actualizar_compra.fecha_compra = datetime.strptime(datosJSON.get('fecha_compra'), '%Y-%m-%d').date()
    actualizar_compra.total_compra = datosJSON.get('total_compra', actualizar_compra.total_compra)

    db.session.commit()
    return compra_schema.jsonify(actualizar_compra)

# DELETE eliminar compra
@app.route('/compra/eliminar_compra/<string:folio_compra>', methods=['DELETE'])
def eliminarCompra(folio_compra):
    eliminar_compra = Compra.query.get(folio_compra)
    if eliminar_compra is None:
        return jsonify({'message': 'Compra no encontrada'}), 404

    db.session.delete(eliminar_compra)
    db.session.commit()
    return compra_schema.jsonify(eliminar_compra)

if __name__ == "__main__":
    app.run(debug=True, port=4040, host="localhost")

