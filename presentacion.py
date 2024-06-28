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

# Definición del modelo Presentacion
class Presentacion(db.Model):
    id_presentacion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.String(255), nullable=False)

    def __init__(self, nombre, descripcion):
        self.nombre = nombre
        self.descripcion = descripcion

with app.app_context():
    db.create_all()

# Definición del esquema Presentacion
class PresentacionSchema(ma.Schema):
    class Meta:
        fields = ('id_presentacion', 'nombre', 'descripcion')

# Instancias de los esquemas
presentacion_schema = PresentacionSchema()
presentaciones_schema = PresentacionSchema(many=True)

# Rutas de la API

# GET todas las presentaciones
@app.route('/presentacion', methods=['GET'])
def obtenerPresentaciones():
    todas_las_presentaciones = Presentacion.query.all()
    consulta_presentaciones = presentaciones_schema.dump(todas_las_presentaciones)
    return jsonify(consulta_presentaciones)

# GET una presentacion por id
@app.route('/presentacion/<int:id_presentacion>', methods=['GET'])
def obtenerPresentacion(id_presentacion):
    una_presentacion = Presentacion.query.get(id_presentacion)
    if una_presentacion is None:
        return jsonify({'message': 'Presentación no encontrada'}), 404
    return presentacion_schema.jsonify(una_presentacion)

# POST nueva presentacion
@app.route('/presentacion/nueva_presentacion', methods=['POST'])
def insertar_presentacion():
    datosJSON = request.get_json(force=True)
    nombre = datosJSON.get('nombre')
    descripcion = datosJSON.get('descripcion')

    if not nombre or not descripcion:
        return jsonify({'message': 'Nombre y descripción son requeridos'}), 400

    nueva_presentacion = Presentacion(nombre, descripcion)
    db.session.add(nueva_presentacion)
    db.session.commit()
    return presentacion_schema.jsonify(nueva_presentacion), 201

# PUT actualizar presentacion
@app.route('/presentacion/actualizar_presentacion/<int:id_presentacion>', methods=['PUT'])
def actualizarPresentacion(id_presentacion):
    actualizar_presentacion = Presentacion.query.get(id_presentacion)
    if actualizar_presentacion is None:
        return jsonify({'message': 'Presentación no encontrada'}), 404

    datosJSON = request.get_json(force=True)
    nombre = datosJSON.get('nombre', actualizar_presentacion.nombre)
    descripcion = datosJSON.get('descripcion', actualizar_presentacion.descripcion)

    actualizar_presentacion.nombre = nombre
    actualizar_presentacion.descripcion = descripcion

    db.session.commit()
    return presentacion_schema.jsonify(actualizar_presentacion)

# DELETE eliminar presentacion
@app.route('/presentacion/eliminar_presentacion/<int:id_presentacion>', methods=['DELETE'])
def eliminarPresentacion(id_presentacion):
    eliminar_presentacion = Presentacion.query.get(id_presentacion)
    if eliminar_presentacion is None:
        return jsonify({'message': 'Presentación no encontrada'}), 404

    db.session.delete(eliminar_presentacion)
    db.session.commit()
    return presentacion_schema.jsonify(eliminar_presentacion)

if __name__ == "__main__":
    app.run(debug=True, port=4040, host="localhost")

