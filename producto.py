from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from config import config as cn

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = cn.DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)
CORS(app, resources={
    r"/*": {
        "origins": "*"
    }
})

db = SQLAlchemy(app)
ma = Marshmallow(app)

# Modelos
class Presentacion(db.Model):
    id_presentacion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.String(255), nullable=False)

class Marca(db.Model):
    id_marca = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)

class Categoria(db.Model):
    id_categoria = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.String(255), nullable=False)

class Producto(db.Model):
    codigo_barras = db.Column(db.String(255), primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.String(255), nullable=False)
    id_categoria = db.Column(db.Integer, db.ForeignKey('categoria.id_categoria'))
    id_presentacion = db.Column(db.Integer, db.ForeignKey('presentacion.id_presentacion'))
    id_marca = db.Column(db.Integer, db.ForeignKey('marca.id_marca'))
    cantidad_actual = db.Column(db.Integer, nullable=False)
    cantidad_maxima = db.Column(db.Integer, nullable=False)
    cantidad_minima = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(255), nullable=False)

with app.app_context():
    db.create_all()

# Esquema de Producto
class ProductoSchema(ma.Schema):
    class Meta:
        fields = ('codigo_barras', 'nombre', 'descripcion', 'id_categoria', 'id_presentacion', 'id_marca', 'cantidad_actual', 'cantidad_maxima', 'cantidad_minima', 'precio', 'estado')

productoSchema = ProductoSchema()
productosSchema = ProductoSchema(many=True)

# Rutas CRUD
@app.route('/producto', methods=['GET'])
def obtener_productos():
    todos_los_productos = Producto.query.all()
    consulta_productos = productosSchema.dump(todos_los_productos)
    return jsonify(consulta_productos)

@app.route('/producto/<codigo_barras>', methods=['GET'])
def obtener_producto(codigo_barras):
    un_producto = Producto.query.filter_by(codigo_barras=codigo_barras).first()
    if un_producto is None:
        return jsonify({'message': 'Producto no encontrado'}), 404
    return productoSchema.jsonify(un_producto)

@app.route('/producto/nuevo_producto', methods=['POST'])
def insertar_producto():
    datos_json = request.get_json(force=True)
    nuevo_producto = Producto(
        codigo_barras=datos_json['codigo_barras'],
        nombre=datos_json['nombre'],
        descripcion=datos_json['descripcion'],
        id_categoria=datos_json['id_categoria'],
        id_presentacion=datos_json['id_presentacion'],
        id_marca=datos_json['id_marca'],
        cantidad_actual=datos_json['cantidad_actual'],
        cantidad_maxima=datos_json['cantidad_maxima'],
        cantidad_minima=datos_json['cantidad_minima'],
        precio=datos_json['precio'],
        estado=datos_json['estado']
    )
    db.session.add(nuevo_producto)
    db.session.commit()
    return productoSchema.jsonify(nuevo_producto)

@app.route('/producto/actualizar_producto/<codigo_barras>', methods=['PUT'])
def actualizar_producto(codigo_barras):
    producto = Producto.query.filter_by(codigo_barras=codigo_barras).first()
    if producto is None:
        return jsonify({'message': 'Producto no encontrado'}), 404

    datos_json = request.get_json(force=True)
    producto.nombre = datos_json['nombre']
    producto.descripcion = datos_json['descripcion']
    producto.id_categoria = datos_json['id_categoria']
    producto.id_presentacion = datos_json['id_presentacion']
    producto.id_marca = datos_json['id_marca']
    producto.cantidad_actual = datos_json['cantidad_actual']
    producto.cantidad_maxima = datos_json['cantidad_maxima']
    producto.cantidad_minima = datos_json['cantidad_minima']
    producto.precio = datos_json['precio']
    producto.estado = datos_json['estado']

    db.session.commit()
    return productoSchema.jsonify(producto)

@app.route('/producto/eliminar_producto/<codigo_barras>', methods=['DELETE'])
def eliminar_producto(codigo_barras):
    producto = Producto.query.filter_by(codigo_barras=codigo_barras).first()
    if producto is None:
        return jsonify({'message': 'Producto no encontrado'}), 404

    db.session.delete(producto)
    db.session.commit()
    return productoSchema.jsonify(producto)
    
# Nueva ruta para obtener productos con cantidad_actual mayor a 0
@app.route('/producto/disponibles', methods=['GET'])
def obtener_productos_disponibles():
    productos_disponibles = Producto.query.filter(Producto.cantidad_actual > 0).all()
    consulta_productos_disponibles = productosSchema.dump(productos_disponibles)
    return jsonify(consulta_productos_disponibles)    

if __name__ == "__main__":
    app.run(debug=True, port=4040, host="localhost")

