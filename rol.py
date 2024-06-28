from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from config.config import DATABASE_URL

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)

db = SQLAlchemy(app)
ma = Marshmallow(app)

# Definición del modelo Rol
class Rol(db.Model):
    id_rol = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.String(255), nullable=False)

    def __init__(self, nombre, descripcion):
        self.nombre = nombre
        self.descripcion = descripcion

# Creación del esquema de Marshmallow para Rol
class RolSchema(ma.Schema):
    class Meta:
        fields = ('id_rol', 'nombre', 'descripcion')

rol_schema = RolSchema()
roles_schema = RolSchema(many=True)

# Rutas de la API
@app.route('/rol', methods=['GET'])
def obtenerRoles():
    todos_los_roles = Rol.query.all()
    consulta_roles = roles_schema.dump(todos_los_roles)
    return jsonify(consulta_roles)

@app.route('/rol/<int:id>', methods=['GET'])
def obtenerRol(id):
    un_rol = Rol.query.get(id)
    if un_rol is None:
        return jsonify({'message': 'Rol no encontrado'}), 404
    return rol_schema.jsonify(un_rol)

@app.route('/rol/nuevo_rol', methods=['POST'])
def insertar_rol():
    datosJSON = request.get_json(force=True)
    nombre = datosJSON.get('nombre')
    descripcion = datosJSON.get('descripcion')

    nuevo_rol = Rol(nombre, descripcion)
    db.session.add(nuevo_rol)
    db.session.commit()
    return rol_schema.jsonify(nuevo_rol), 201

@app.route('/rol/actualizar_rol/<int:id>', methods=['PUT'])
def actualizarRol(id):
    actualizar_rol = Rol.query.get(id)
    if actualizar_rol is None:
        return jsonify({'message': 'Rol no encontrado'}), 404

    datosJSON = request.get_json(force=True)
    actualizar_rol.nombre = datosJSON.get('nombre', actualizar_rol.nombre)
    actualizar_rol.descripcion = datosJSON.get('descripcion', actualizar_rol.descripcion)

    db.session.commit()
    return rol_schema.jsonify(actualizar_rol)

@app.route('/rol/eliminar_rol/<int:id>', methods=['DELETE'])
def eliminarRol(id):
    eliminar_rol = Rol.query.get(id)
    if eliminar_rol is None:
        return jsonify({'message': 'Rol no encontrado'}), 404

    db.session.delete(eliminar_rol)
    db.session.commit()
    return rol_schema.jsonify(eliminar_rol)

if __name__ == "__main__":
    app.run(debug=True, port=4040, host="127.0.0.1")

