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

with app.app_context():
    db.create_all()

# Definición del esquema Usuario
class UsuarioSchema(ma.Schema):
    class Meta:
        fields = ('clv_usuario', 'nombre', 'apellido1', 'apellido2', 'telefono', 'correo', 'direccion', 'id_rol', 'contrasenia')

# Instancias de los esquemas
usuario_schema = UsuarioSchema()
usuarios_schema = UsuarioSchema(many=True)

# GET todos los usuarios
@app.route('/usuario', methods=['GET'])
def obtenerUsuarios():
    todos_los_usuarios = Usuario.query.all()
    consulta_usuarios = usuarios_schema.dump(todos_los_usuarios)
    return jsonify(consulta_usuarios)

# GET un usuario por clave
@app.route('/usuario/<string:clv_usuario>', methods=['GET'])
def obtenerUsuario(clv_usuario):
    un_usuario = Usuario.query.get(clv_usuario)
    if un_usuario is None:
        return jsonify({'message': 'Usuario no encontrado'}), 404
    return usuario_schema.jsonify(un_usuario)

# POST nuevo usuario
@app.route('/usuario/nuevo_usuario', methods=['POST'])
def insertar_usuario():
    datosJSON = request.get_json(force=True)
    clv_usuario = datosJSON.get('clv_usuario')
    nombre = datosJSON.get('nombre')
    apellido1 = datosJSON.get('apellido1')
    apellido2 = datosJSON.get('apellido2')
    telefono = datosJSON.get('telefono')
    correo = datosJSON.get('correo')
    direccion = datosJSON.get('direccion')
    id_rol = datosJSON.get('id_rol')
    contrasenia = datosJSON.get('contrasenia')

    if not clv_usuario or not nombre or not apellido1 or not apellido2 or not telefono or not correo or not direccion or not contrasenia:
        return jsonify({'message': 'Faltan datos necesarios'}), 400

    nuevo_usuario = Usuario(clv_usuario, nombre, apellido1, apellido2, telefono, correo, direccion, id_rol, contrasenia)
    db.session.add(nuevo_usuario)
    db.session.commit()
    return usuario_schema.jsonify(nuevo_usuario), 201

# PUT actualizar usuario
@app.route('/usuario/actualizar_usuario/<string:clv_usuario>', methods=['PUT'])
def actualizarUsuario(clv_usuario):
    actualizar_usuario = Usuario.query.get(clv_usuario)
    if actualizar_usuario is None:
        return jsonify({'message': 'Usuario no encontrado'}), 404

    datosJSON = request.get_json(force=True)
    actualizar_usuario.nombre = datosJSON.get('nombre', actualizar_usuario.nombre)
    actualizar_usuario.apellido1 = datosJSON.get('apellido1', actualizar_usuario.apellido1)
    actualizar_usuario.apellido2 = datosJSON.get('apellido2', actualizar_usuario.apellido2)
    actualizar_usuario.telefono = datosJSON.get('telefono', actualizar_usuario.telefono)
    actualizar_usuario.correo = datosJSON.get('correo', actualizar_usuario.correo)
    actualizar_usuario.direccion = datosJSON.get('direccion', actualizar_usuario.direccion)
    actualizar_usuario.id_rol = datosJSON.get('id_rol', actualizar_usuario.id_rol)
    actualizar_usuario.contrasenia = datosJSON.get('contrasenia', actualizar_usuario.contrasenia)

    db.session.commit()
    return usuario_schema.jsonify(actualizar_usuario)

# DELETE eliminar usuario
@app.route('/usuario/eliminar_usuario/<string:clv_usuario>', methods=['DELETE'])
def eliminarUsuario(clv_usuario):
    eliminar_usuario = Usuario.query.get(clv_usuario)
    if eliminar_usuario is None:
        return jsonify({'message': 'Usuario no encontrado'}), 404

    db.session.delete(eliminar_usuario)
    db.session.commit()
    return usuario_schema.jsonify(eliminar_usuario)

# POST validar usuario
@app.route('/usuario/validar_usuario', methods=['POST'])
def validar_usuario():
    datosJSON = request.get_json(force=True)
    clv_usuario = datosJSON.get('clv_usuario')
    contrasenia = datosJSON.get('contrasenia')

    usuario = Usuario.query.filter_by(clv_usuario=clv_usuario, contrasenia=contrasenia).first()
    if usuario is None:
        return jsonify({'message': 'Usuario o contraseña incorrectos'}), 401
    return usuario_schema.jsonify(usuario)

if __name__ == "__main__":
    app.run(debug=True, port=4041, host="localhost")

