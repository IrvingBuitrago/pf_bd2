from flask import Flask, request, jsonify, render_template, url_for, redirect
from conex import myconex
from passlib.hash import pbkdf2_sha256

app = Flask(__name__)

instancia = myconex

@app.route('/', methods= ['GET', 'POST'])
def dashboard():
    return render_template('dash.html')

@app.route('/login', methods=['GET', 'POST'])
def logIn():
    if request.method == 'POST':
        id = request.form['id']
        password = request.form['password']
        instancia.conectar()
        query = 'SELECT passwrd FROM students WHERE id = %s'
        result = instancia.consultar(query, (id))
        try:
            if result and pbkdf2_sha256.verify(password, result[0]):
                # Si hay un resultado, redirigir al usuario al dashboard
                instancia.cerrar_conex()
                return redirect(url_for('dashboard'))
            else:
                # Si no hay resultado, mostrar un mensaje de error
                instancia.cerrar_conex()
                return render_template('login.html', error='Datos no encontrados')
        except Exception as e:
            return render_template('login.html', error=f'{str(e)}')
    else:
        return render_template('login.html')

@app.route('/registro/estudiante', methods= ['GET', 'POST'])
def registro_studiante():
    if request.method == 'POST':
        id = request.form['id']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        cellphone = request.form['cellphone']
        career = request.form['career']
        university = request.form['university']
        year_study = request.form['year_study']
        instancia.conectar()
        query = 'SELECT * FROM students WHERE id = %s'
        result = instancia.consultar(query, (id))
        if result:
            # Si hay un resultado, mostrar un mensaje de error
            instancia.cerrar_conex()
            return render_template('registro_estudiante.html', error= 'Este usuario ya existe')
        else:
            try:
                # Si no hay resultado, agregar al usuario
                password_hash = pbkdf2_sha256.hash(password)
                query2 = 'INSERT INTO students (id, first_name, last_name, email, passwrd, cellphone, career, university, year_study) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
                values = (id, first_name, last_name, email, password_hash, cellphone, career, university, year_study)
                instancia.insertar(query2, values)
                instancia.cerrar_conex()
                return redirect(url_for('dashboard'))
            except Exception as e:
                instancia.cerrar_conex()
                # Si ocurre un error, mostrar mensaje de error genérico
                return render_template('registro_estudiante.html', error=f'Error en el registro. Error: {str(e)}')
    else:
        return render_template('registro_estudiante.html')


if __name__ == '__main__':
    app.run(debug=True)