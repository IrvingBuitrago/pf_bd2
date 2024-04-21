from flask import Flask, request, jsonify, render_template, url_for, redirect
from dml import DML
from passlib.hash import pbkdf2_sha256

app = Flask(__name__)

instancia = DML("localhost", "root", "Iiebc04299?", "practicas_profesionales", 3305)

@app.route('/', methods= ['GET', 'POST'])
def dashboard():
    return render_template('dash.html')

@app.route('/login', methods=['GET', 'POST'])
def logIn():
    if request.method == 'POST':
        id = request.form['id']
        password = request.form['password']
        instancia.conectar()
        query = 'SELECT * FROM students WHERE id = %s AND passwrd = %s'
        result = instancia.consultar(query, (id, password))
        if result:
            # Si hay un resultado, redirigir al usuario al dashboard
            return render_template('dash.html')
        else:
            # Si no hay resultado, mostrar un mensaje de error
            return render_template('login.html', error='Datos no encontrados')
    else:
        return render_template('login.html')
if __name__ == '__main__':
    app.run(debug=True)