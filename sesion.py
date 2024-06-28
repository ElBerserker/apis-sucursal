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

with app.app_context():
    db.create_all()

# Definición del esquema Sesion
class SesionSchema(ma.Schema):
    class Meta:
        fields = ('folio_sesion', 'clv_usuario', 'fecha_inicio', 'fecha_final', 'estado')

sesion_schema = SesionSchema()
sesiones_schema = SesionSchema(many=True)

# GET todas las sesiones
@app.route('/sesion', methods=['GET'])
def obtenerSesiones():
    todas_las_sesiones = Sesion.query.all()
    consulta_sesiones = sesiones_schema.dump(todas_las_sesiones)
    return jsonify(consulta_sesiones)

# GET una sesion por folio
@app.route('/sesion/<string:folio_sesion>', methods=['GET'])
def obtenerSesion(folio_sesion):
    una_sesion = Sesion.query.get(folio_sesion)
    if una_sesion is None:
        return jsonify({'message': 'Sesión no encontrada'}), 404
    return sesion_schema.jsonify(una_sesion)

# POST nueva sesion
@app.route('/sesion/nueva_sesion', methods=['POST'])
def insertar_sesion():
    datosJSON = request.get_json(force=True)
    folio_sesion = datosJSON.get('folio_sesion')
    clv_usuario = datosJSON.get('clv_usuario')
    fecha_inicio = datetime.strptime(datosJSON.get('fecha_inicio'), '%Y-%m-%d').date()
    fecha_final = datetime.strptime(datosJSON.get('fecha_final'), '%Y-%m-%d').date()
    estado = datosJSON.get('estado')

    if not folio_sesion or not fecha_inicio or not fecha_final or not estado:
        return jsonify({'message': 'Faltan datos necesarios'}), 400

    nueva_sesion = Sesion(folio_sesion, clv_usuario, fecha_inicio, fecha_final, estado)
    db.session.add(nueva_sesion)
    db.session.commit()
    return sesion_schema.jsonify(nueva_sesion), 201

# PUT actualizar sesion
@app.route('/sesion/actualizar_sesion/<string:folio_sesion>', methods=['PUT'])
def actualizarSesion(folio_sesion):
    actualizar_sesion = Sesion.query.get(folio_sesion)
    if actualizar_sesion is None:
        return jsonify({'message': 'Sesión no encontrada'}), 404

    datosJSON = request.get_json(force=True)
    actualizar_sesion.clv_usuario = datosJSON.get('clv_usuario', actualizar_sesion.clv_usuario)
    fecha_inicio = datosJSON.get('fecha_inicio')
    fecha_final = datosJSON.get('fecha_final')

    if fecha_inicio:
        actualizar_sesion.fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
    if fecha_final:
        actualizar_sesion.fecha_final = datetime.strptime(fecha_final, '%Y-%m-%d').date()

    actualizar_sesion.estado = datosJSON.get('estado', actualizar_sesion.estado)

    db.session.commit()
    return sesion_schema.jsonify(actualizar_sesion)

# DELETE eliminar sesion
@app.route('/sesion/eliminar_sesion/<string:folio_sesion>', methods=['DELETE'])
def eliminarSesion(folio_sesion):
    eliminar_sesion = Sesion.query.get(folio_sesion)
    if eliminar_sesion is None:
        return jsonify({'message': 'Sesión no encontrada'}), 404

    db.session.delete(eliminar_sesion)
    db.session.commit()
    return sesion_schema.jsonify(eliminar_sesion)

# Nueva ruta para verificar si la sesión de un usuario está activa
@app.route('/sesion/activa/<string:clv_usuario>', methods=['GET'])
def sesion_activa(clv_usuario):
    sesion_activa = Sesion.query.filter_by(clv_usuario=clv_usuario, estado='activa').first()
    if sesion_activa:
        return jsonify({'activa': True, 'folio_sesion': sesion_activa.folio_sesion})
    else:
        return jsonify({'activa': False, 'folio_sesion': None})

if __name__ == "__main__":
    app.run(debug=True, port=4042, host="localhost")

