from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from flask import jsonify

app = Flask(__name__)
app.secret_key = "clave_secreta"  # Clave secreta para manejar sesiones

# Conexión a la base de datos MongoDB (asegúrate de que MongoDB esté en funcionamiento)
client = MongoClient('mongodb://localhost:27017/')
db = client['mi_base_de_datos']
productos_collection = db['productos']
usuarios_collection = db['usuarios']

@app.route('/')
def inicio():
    if 'usuario' in session:
        usuario = session["usuario"]
        productos = productos_collection.find()
        return render_template('tabla.html', usuario=usuario, productos=productos)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contraseña = request.form['contraseña']
        usuario_encontrado = usuarios_collection.find_one({'usuario': usuario})
        if usuario_encontrado and usuario_encontrado['contraseña'] == contraseña:
            session['usuario'] = usuario
            return redirect(url_for('inicio'))
        else:
            # Mostrar una alerta de SweetAlert si las credenciales son incorrectas
            return render_template('login.html', mensaje="Usuario o contraseña incorrectos.")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('inicio'))


@app.route('/registrar_producto', methods=['POST'])
def registrar_producto():
    if 'usuario' in session:
        if request.method == 'POST':
            codigo = request.form['codigo']
            nombre = request.form['nombre']
            precio = request.form['precio']
            categoria = request.form['categoria']
            foto = request.form['foto']

            # Validación de campos obligatorios
            if not codigo or not nombre or not precio or not categoria or not foto:
                return "Todos los campos son obligatorios. Por favor, completa el formulario."

            # Insertar el producto en la base de datos
            producto = {
                "codigo": codigo,
                "nombre": nombre,
                "precio": precio,
                "categoria": categoria,
                "foto": foto
            }
            productos_collection.insert_one(producto)
            return redirect(url_for('inicio'))
    return redirect(url_for('login'))


@app.route('/eliminar_producto', methods=['POST'])
def eliminar_producto():
    if 'usuario' in session:
        if request.method == 'POST':
            codigo = request.json.get('codigo')
            productos_collection.delete_one({'codigo': codigo})
            return 'Producto eliminado exitosamente', 200
    return redirect(url_for('login'))




@app.route('/actualizar_producto', methods=['POST'])
def actualizar_producto():
    if 'usuario' in session:
        if request.method == 'POST':
            datos_producto = request.json
            codigo = datos_producto.get('codigo')
            nombre = datos_producto.get('nombre')
            precio = datos_producto.get('precio')
            categoria = datos_producto.get('categoria')
            foto = datos_producto.get('foto')

            # Actualizar el producto en la base de datos
            productos_collection.update_one(
                {'codigo': codigo},
                {'$set': {'nombre': nombre, 'precio': precio, 'categoria': categoria, 'foto': foto}}
            )

            return 'Producto actualizado exitosamente', 200
    return redirect(url_for('login'))





if __name__ == '__main__':
    app.run(debug=True)
