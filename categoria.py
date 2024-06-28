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

# Definición del modelo Categoria
class Categoria(db.Model):
    id_categoria = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.String(255), nullable=False)

    def __init__(self, nombre, descripcion):
        self.nombre = nombre
        self.descripcion = descripcion

# Definición del esquema Categoria
class CategoriaSchema(ma.Schema):
    class Meta:
        fields = ('id_categoria', 'nombre', 'descripcion')

categoria_schema = CategoriaSchema()
categorias_schema = CategoriaSchema(many=True)

# Métodos de la API
@app.route('/categoria', methods=['GET'])
def obtenerCategorias():
    todas_las_categorias = Categoria.query.all()
    consulta_categorias = categorias_schema.dump(todas_las_categorias)
    return jsonify(consulta_categorias)

@app.route('/categoria/<int:id_categoria>', methods=['GET'])
def obtenerCategoria(id_categoria):
    una_categoria = Categoria.query.get(id_categoria)
    if una_categoria is None:
        return jsonify({'message': 'Categoría no encontrada'}), 404
    return categoria_schema.jsonify(una_categoria)

@app.route('/categoria/nueva_categoria', methods=['POST'])
def insertarCategoria():
    datosJSON = request.get_json(force=True)
    nombre = datosJSON.get('nombre')
    descripcion = datosJSON.get('descripcion')

    if not nombre or not descripcion:
        return jsonify({'message': 'Nombre y descripción son requeridos'}), 400

    nueva_categoria = Categoria(nombre, descripcion)
    db.session.add(nueva_categoria)
    db.session.commit()
    return categoria_schema.jsonify(nueva_categoria), 201

@app.route('/categoria/actualizar_categoria/<int:id_categoria>', methods=['PUT'])
def actualizarCategoria(id_categoria):
    actualizar_categoria = Categoria.query.get(id_categoria)
    if actualizar_categoria is None:
        return jsonify({'message': 'Categoría no encontrada'}), 404

    datosJSON = request.get_json(force=True)
    nombre = datosJSON.get('nombre', actualizar_categoria.nombre)
    descripcion = datosJSON.get('descripcion', actualizar_categoria.descripcion)

    actualizar_categoria.nombre = nombre
    actualizar_categoria.descripcion = descripcion

    db.session.commit()
    return categoria_schema.jsonify(actualizar_categoria)

@app.route('/categoria/eliminar_categoria/<int:id_categoria>', methods=['DELETE'])
def eliminarCategoria(id_categoria):
    eliminar_categoria = Categoria.query.get(id_categoria)
    if eliminar_categoria is None:
        return jsonify({'message': 'Categoría no encontrada'}), 404

    db.session.delete(eliminar_categoria)
    db.session.commit()
    return categoria_schema.jsonify(eliminar_categoria)

if __name__ == "__main__":
    app.run(debug=True, port=4040, host="127.0.0.1")

