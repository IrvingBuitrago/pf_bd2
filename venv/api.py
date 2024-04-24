from flask import Flask, request, jsonify, render_template, url_for, redirect, session
from conex import myconex
from passlib.hash import pbkdf2_sha256

app = Flask(__name__)
app.secret_key = 'mykey'

instancia = myconex

@app.route('/dash/estudiante', methods= ['GET', 'POST'])
def dashboard_estudiante():
    if request.method == 'GET':
        if 'user' in session:
            username = session['user']
            instancia.conectar()
            query = 'SELECT * FROM float_vacancy'
            result = instancia.consultar(query, fetchall= True)
            instancia.cerrar_conex()
            try:
                if result:
                    result_row = result[0]
                    return render_template('dash.html', result=result)
                else:
                    return "No se encontraron datos para mostrar."
            except Exception as e:
                return f'Error: {str(e)}'
        else:
            return redirect(url_for('logIn'))
    elif request.method == 'POST':
        if 'user' in session:
            username = session['user']
            title = request.form['title']
            instancia.conectar()
            query = 'SELECT * FROM float_vacancy_search WHERE title LIKE %s'
            result = instancia.consultar(query, ('%' + title + '%',), fetchall= True)
            instancia.cerrar_conex()
            try:
                if result:
                    result_row = result[0]
                    return render_template('busqueda.html', result=result)
                else:
                    return "No se encontraron datos para mostrar"
            except Exception as e:
                return f'Error: {str(e)}'
    else:
        return redirect(url_for('logIn'))

@app.route('/dash/admin', methods=['GET'])
def dashboard_admin():
    if request.method == 'GET':
        if 'user' in session:
            username = session['user']
            instancia.conectar()
            # query = 'SELECT * FROM requests_sector_view'
            # result = instancia.consultar(query)
            # print(result)
            instancia.cerrar_conex()
            try:
                if result:
                    return render_template('dash_admin.html')
                else:
                    return "No se encontraron datos para mostrar."
            except Exception as e:
                return f'Error: {str(e)}'
        else:
            return redirect(url_for('logIn'))
    else:
        return redirect(url_for('logIn'))

@app.route('/', methods=['GET', 'POST'])
def logIn():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        instancia.conectar()
        query = 'SELECT passwrd FROM users WHERE user_name = %s'
        result = instancia.consultar(query, (username,), fetchall=False)
        try:
            if result and pbkdf2_sha256.verify(password, result[0]):
                query = 'SELECT rol FROM users WHERE user_name = %s'
                result = instancia.consultar(query, (username,), fetchall=False)
                rol = result[0]
                if rol == 'Estudiante':
                    session['user'] = {'username': username, 'rol': rol}
                    # Si el usuario es estudiante, redirigir al dashboard de estudiantes
                    instancia.cerrar_conex()
                    return redirect(url_for('dashboard_estudiante'))
                elif rol == 'Administrativo':
                    session['user'] = {'username': username, 'rol': rol}
                    # Si el usuario no es estudiante, redirigir al dashboard de administrador
                    instancia.cerrar_conex()
                    return redirect(url_for('dashboard_admin'))
                else:
                    return redirect(url_for('registro'))
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
                return redirect(url_for('logIn'))
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

@app.route('/perfil/estudiante', methods=['GET', 'POST'])
def perfil_estudiante():
    if request.method == 'GET':
        if 'user' in session:
            userinfo = session['user']
            username = userinfo['username']
            rol = userinfo['rol']
            instancia.conectar()
            query = 'SELECT * FROM users WHERE user_name = %s'
            result = instancia.consultar(query, (username,), fetchall=True)
            instancia.cerrar_conex()
            try:
                if result:
                    result_row = result[0]
                    if rol == 'Estudiante':
                        return render_template('perfil_est.html', result=result)
            except Exception as e:
                return f'Error: {str(e)}'
        else:
            return redirect(url_for('logIn'))
    elif request.method == 'POST':
        if 'user' in session:
            instancia.conectar()
            # Obtener los datos del formulario
            updated_data = {
                'first_name': request.form['first_name'],
                'last_name': request.form['last_name'],
                'email': request.form['email'],
                'career': request.form['career'],
                'year_study': request.form['year_study'],
                'cellphone': request.form['cellphone']
            }
            # Actualizar los datos del usuario en la base de datos
            query = '''
                UPDATE users 
                SET first_name = %(first_name)s, last_name = %(last_name)s, 
                    email = %(email)s, career = %(career)s, year_study = %(year_study)s, 
                    cellphone = %(cellphone)s
                WHERE user_name = %(username)s
            '''
            # Obtener el nombre de usuario de la sesión
            username = session['user']['username']
            updated_data['username'] = username  # Agregar el nombre de usuario al diccionario
            instancia.actualizar(query, updated_data)
            instancia.cerrar_conex()
            # Redirigir de vuelta al perfil después de la actualización
            return redirect(url_for('perfil_estudiante'))
        else:
            return redirect(url_for('logIn'))
    else:
        return redirect(url_for('logIn'))

@app.route('/perfil/administrativo', methods=['GET', 'POST'])
def perfil_administrativo():
    if request.method == 'GET':
        if 'user' in session:
            userinfo = session['user']
            username = userinfo['username']
            rol = userinfo['rol']
            instancia.conectar()
            query = 'SELECT * FROM users WHERE user_name = %s'
            result = instancia.consultar(query, (username,), fetchall=True)
            instancia.cerrar_conex()
            try:
                if result:
                    result_row = result[0]
                    if rol == 'Administrativo':
                        return render_template('perfil_adm.html', result=result)
            except Exception as e:
                return f'Error: {str(e)}'
        else:
            return redirect(url_for('logIn'))
    elif request.method == 'POST':
        if 'user' in session:
            instancia.conectar()
            # Obtener los datos del formulario
            updated_data = {
                'first_name': request.form['first_name'],
                'last_name': request.form['last_name'],
                'email': request.form['email'],
                'cellphone': request.form['cellphone']
            }
            # Actualizar los datos del usuario en la base de datos
            query = '''
                UPDATE users 
                SET first_name = %(first_name)s, last_name = %(last_name)s, 
                    email = %(email)s, cellphone = %(cellphone)s
                WHERE user_name = %(username)s
            '''
            # Obtener el nombre de usuario de la sesión
            username = session['user']['username']
            updated_data['username'] = username  # Agregar el nombre de usuario al diccionario
            instancia.actualizar(query, updated_data)
            instancia.cerrar_conex()
            # Redirigir de vuelta al perfil después de la actualización
            return redirect(url_for('perfil_administrativo'))
        else:
            return redirect(url_for('logIn'))
    else:
        return redirect(url_for('logIn'))

if __name__ == '__main__':
    app.run(debug=True)