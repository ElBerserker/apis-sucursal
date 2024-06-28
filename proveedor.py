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

# Definición del esquema Proveedor
class ProveedorSchema(ma.Schema):
    class Meta:
        fields = ('rfc_proveedor', 'nombre', 'telefono', 'correo')

proveedor_schema = ProveedorSchema()
proveedores_schema = ProveedorSchema(many=True)

# Métodos de la API
@app.route('/proveedor', methods=['GET'])
def obtenerProveedores():
    todos_los_proveedores = Proveedor.query.all()
    consulta_proveedores = proveedores_schema.dump(todos_los_proveedores)
    return jsonify(consulta_proveedores)

@app.route('/proveedor/<string:rfc_proveedor>', methods=['GET'])
def obtenerProveedor(rfc_proveedor):
    un_proveedor = Proveedor.query.get(rfc_proveedor)
    if un_proveedor is None:
        return jsonify({'message': 'Proveedor no encontrado'}), 404
    return proveedor_schema.jsonify(un_proveedor)

@app.route('/proveedor/nuevo_proveedor', methods=['POST'])
def insertarProveedor():
    datosJSON = request.get_json(force=True)
    rfc_proveedor = datosJSON.get('rfc_proveedor')
    nombre = datosJSON.get('nombre')
    telefono = datosJSON.get('telefono')
    correo = datosJSON.get('correo')

    if not rfc_proveedor or not nombre or not telefono or not correo:
        return jsonify({'message': 'Todos los campos son requeridos'}), 400

    nuevo_proveedor = Proveedor(rfc_proveedor, nombre, telefono, correo)

    db.session.add(nuevo_proveedor)
    db.session.commit()
    return proveedor_schema.jsonify(nuevo_proveedor), 201

@app.route('/proveedor/actualizar_proveedor/<string:rfc_proveedor>', methods=['PUT'])
def actualizarProveedor(rfc_proveedor):
    actualizar_proveedor = Proveedor.query.get(rfc_proveedor)
    if actualizar_proveedor is None:
        return jsonify({'message': 'Proveedor no encontrado'}), 404

    datosJSON = request.get_json(force=True)
    nombre = datosJSON.get('nombre', actualizar_proveedor.nombre)
    telefono = datosJSON.get('telefono', actualizar_proveedor.telefono)
    correo = datosJSON.get('correo', actualizar_proveedor.correo)

    actualizar_proveedor.nombre = nombre
    actualizar_proveedor.telefono = telefono
    actualizar_proveedor.correo = correo

    db.session.commit()
    return proveedor_schema.jsonify(actualizar_proveedor)

@app.route('/proveedor/eliminar_proveedor/<string:rfc_proveedor>', methods=['DELETE'])
def eliminarProveedor(rfc_proveedor):
    eliminar_proveedor = Proveedor.query.get(rfc_proveedor)
    if eliminar_proveedor is None:
        return jsonify({'message': 'Proveedor no encontrado'}), 404

    db.session.delete(eliminar_proveedor)
    db.session.commit()
    return proveedor_schema.jsonify(eliminar_proveedor)

if __name__ == "__main__":
    app.run(debug=True, port=4040, host="127.0.0.1")

