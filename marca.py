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

# Definición del modelo Marca
class Marca(db.Model):
    id_marca = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)

    def __init__(self, nombre):
        self.nombre = nombre

with app.app_context():
    db.create_all()

# Definición del esquema Marca
class MarcaSchema(ma.Schema):
    class Meta:
        fields = ('id_marca', 'nombre')

# Instancias de los esquemas
marca_schema = MarcaSchema()
marcas_schema = MarcaSchema(many=True)

# Rutas de la API

# GET todas las marcas
@app.route('/marca', methods=['GET'])
def obtenerMarcas():
    todas_las_marcas = Marca.query.all()
    consulta_marcas = marcas_schema.dump(todas_las_marcas)
    return jsonify(consulta_marcas)

# GET una marca por id
@app.route('/marca/<int:id>', methods=['GET'])
def obtenerMarca(id):
    una_marca = Marca.query.get(id)
    if una_marca is None:
        return jsonify({'message': 'Marca no encontrada'}), 404
    return marca_schema.jsonify(una_marca)

# POST nueva marca
@app.route('/marca/nueva_marca', methods=['POST'])
def insertar_marca():
    datosJSON = request.get_json(force=True)
    nombre = datosJSON.get('nombre')

    if not nombre:
        return jsonify({'message': 'El nombre es requerido'}), 400

    nueva_marca = Marca(nombre)
    db.session.add(nueva_marca)
    db.session.commit()
    return marca_schema.jsonify(nueva_marca), 201

# PUT actualizar marca
@app.route('/marca/actualizar_marca/<int:id>', methods=['PUT'])
def actualizarMarca(id):
    actualizar_marca = Marca.query.get(id)
    if actualizar_marca is None:
        return jsonify({'message': 'Marca no encontrada'}), 404

    datosJSON = request.get_json(force=True)
    nombre = datosJSON.get('nombre', actualizar_marca.nombre)

    actualizar_marca.nombre = nombre

    db.session.commit()
    return marca_schema.jsonify(actualizar_marca)

# DELETE eliminar marca
@app.route('/marca/eliminar_marca/<int:id>', methods=['DELETE'])
def eliminarMarca(id):
    eliminar_marca = Marca.query.get(id)
    if eliminar_marca is None:
        return jsonify({'message': 'Marca no encontrada'}), 404

    db.session.delete(eliminar_marca)
    db.session.commit()
    return marca_schema.jsonify(eliminar_marca)

if __name__ == "__main__":
    app.run(debug=True, port=4040, host="localhost")

