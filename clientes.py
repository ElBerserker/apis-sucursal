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

with app.app_context():
    db.create_all()

# Definición del esquema Cliente
class ClienteSchema(ma.Schema):
    class Meta:
        fields = ('clv_cliente', 'nombre', 'apellido1', 'apellido2', 'telefono', 'correo')

# Instancias de los esquemas
cliente_schema = ClienteSchema()
clientes_schema = ClienteSchema(many=True)

# Rutas de la API

# GET todos los clientes
@app.route('/cliente', methods=['GET'])
def obtenerClientes():
    todos_los_clientes = Cliente.query.all()
    consulta_clientes = clientes_schema.dump(todos_los_clientes)
    return jsonify(consulta_clientes)

# GET un cliente por clave
@app.route('/cliente/<string:clv_cliente>', methods=['GET'])
def obtenerCliente(clv_cliente):
    un_cliente = Cliente.query.get(clv_cliente)
    if un_cliente is None:
        return jsonify({'message': 'Cliente no encontrado'}), 404
    return cliente_schema.jsonify(un_cliente)

# POST nuevo cliente
@app.route('/cliente/nuevo_cliente', methods=['POST'])
def insertar_cliente():
    datosJSON = request.get_json(force=True)
    clv_cliente = datosJSON.get('clv_cliente')
    nombre = datosJSON.get('nombre')
    apellido1 = datosJSON.get('apellido1')
    apellido2 = datosJSON.get('apellido2')
    telefono = datosJSON.get('telefono')
    correo = datosJSON.get('correo')

    if not clv_cliente or not nombre or not apellido1 or not apellido2 or not telefono or not correo:
        return jsonify({'message': 'Faltan datos necesarios'}), 400

    nuevo_cliente = Cliente(clv_cliente, nombre, apellido1, apellido2, telefono, correo)
    db.session.add(nuevo_cliente)
    db.session.commit()
    return cliente_schema.jsonify(nuevo_cliente), 201

# PUT actualizar cliente
@app.route('/cliente/actualizar_cliente/<string:clv_cliente>', methods=['PUT'])
def actualizarCliente(clv_cliente):
    actualizar_cliente = Cliente.query.get(clv_cliente)
    if actualizar_cliente is None:
        return jsonify({'message': 'Cliente no encontrado'}), 404

    datosJSON = request.get_json(force=True)
    actualizar_cliente.nombre = datosJSON.get('nombre', actualizar_cliente.nombre)
    actualizar_cliente.apellido1 = datosJSON.get('apellido1', actualizar_cliente.apellido1)
    actualizar_cliente.apellido2 = datosJSON.get('apellido2', actualizar_cliente.apellido2)
    actualizar_cliente.telefono = datosJSON.get('telefono', actualizar_cliente.telefono)
    actualizar_cliente.correo = datosJSON.get('correo', actualizar_cliente.correo)

    db.session.commit()
    return cliente_schema.jsonify(actualizar_cliente)

# DELETE eliminar cliente
@app.route('/cliente/eliminar_cliente/<string:clv_cliente>', methods=['DELETE'])
def eliminarCliente(clv_cliente):
    eliminar_cliente = Cliente.query.get(clv_cliente)
    if eliminar_cliente is None:
        return jsonify({'message': 'Cliente no encontrado'}), 404

    db.session.delete(eliminar_cliente)
    db.session.commit()
    return cliente_schema.jsonify(eliminar_cliente)

if __name__ == "__main__":
    app.run(debug=True, port=4043, host="localhost")

