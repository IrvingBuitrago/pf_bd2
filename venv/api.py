from flask import Flask, request, jsonify, render_template, url_for, redirect
from conex import myconex
from passlib.hash import pbkdf2_sha256

app = Flask(__name__)

instancia = myconex

@app.route('/dash/estudiantes', methods= ['GET', 'POST'])
def dashboard_estudiante():
    return render_template('dash.html')

@app.route('/dash/admin', methods=['GET'])
def dashboard_admin():
    return render_template('dash_admin.html')

@app.route('/', methods=['GET', 'POST'])
def logIn():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        instancia.conectar()
        query = 'SELECT passwrd FROM users WHERE user_name = %s'
        result = instancia.consultar(query, (username))
        try:
            if result and pbkdf2_sha256.verify(password, result[0]):
                query = 'SELECT rol FROM users WHERE user_name = %s'
                result = instancia.consultar(query, (username,))
                if result:
                    if result[0] == 'Estudiante':
                        # Si el usuario es estudiante, redirigir al dashboard de estudiantes
                        instancia.cerrar_conex()
                        return redirect(url_for('dashboard_estudiante'))
                    else:
                        # Si el usuario no es estudiante, redirigir al dashboard de administrador
                        instancia.cerrar_conex()
                        return redirect(url_for('dashboard_admin'))
        except Exception as e:
            return render_template('login.html', error=f'{str(e)}')
        else:
            # Si no hay resultado, mostrar un mensaje de error
            instancia.cerrar_conex()
            return render_template('login.html', error='Datos no encontrados')
    else:
        return render_template('login.html')

@app.route('/registro', methods= ['GET', 'POST'])
def registro():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        rol = request.form['rol']
        career = request.form['career']
        cellphone = request.form['cellphone']
        year_study = request.form['year_study']
        instancia.conectar()
        query = 'SELECT * FROM users WHERE user_name = %s'
        result = instancia.consultar(query, (username))
        if result:
            # Si hay un resultado, mostrar un mensaje de error
            instancia.cerrar_conex()
            return render_template('registro_estudiante.html', error= 'Este usuario ya existe')
        else:
            try:
                # Si no hay resultado, agregar al usuario
                password_hash = pbkdf2_sha256.hash(password)
                query2 = 'INSERT INTO users (user_name, passwrd, email, first_name, last_name, rol, career, cellphone, year_study) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
                values = (username, password_hash, email, first_name, last_name, rol, career, cellphone, year_study)
                instancia.insertar(query2, values)
                instancia.cerrar_conex()
                return redirect(url_for('dashboard_estudiante'))
            except Exception as e:
                instancia.cerrar_conex()
                # Si ocurre un error, mostrar mensaje de error genérico
                return render_template('registro_estudiante.html', error=f'Error en el registro. Error: {str(e)}')
    else:
        return render_template('registro_estudiante.html')

@app.route('/registro/empresas', methods= ['GET', 'POST'])
def registro_empresas():
    if request.method == 'POST':
        name = request.form['name']
        direction = request.form['direction']
        telephone = request.form['telephone']
        email = request.form['email']
        contact_name = request.form['contact_name']
        contact_last_name = request.form['contact_last_name']
        contact_email = request.form['contact_email']
        contact_telephone = request.form['contact_telephone']
        instancia.conectar()
        query = 'SELECT * FROM enterprises WHERE name_ent = %s'
        result = instancia.consultar(query, (name))
        if result:
            # Si hay un resultado, mostrar un mensaje de error
            instancia.cerrar_conex()
            return render_template('registro_empresa.html', error= 'Esta empresa ya existe')
        else:
            try:
                query2 = 'INSERT INTO enterprises (name_ent, direction, telephone, email, contact_name, contact_last_name, contact_email, contact_telephone) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
                values = (name, direction, telephone, email, contact_name, contact_last_name, contact_email, contact_telephone)
                instancia.insertar(query2, values)
                instancia.cerrar_conex()
                return redirect(url_for('dashboard_admin'))
            except Exception as e:
                instancia.cerrar_conex()
                # Si ocurre un error, mostrar mensaje de error genérico
                return render_template('registro_empresa.html', error=f'Error en el registro. Error: {str(e)}')
    else:
        return render_template('registro_empresa.html')

if __name__ == '__main__':
    app.run(debug=True)