from flask import Flask, render_template, request, redirect, url_for
import models
from flask import session
from functools import wraps

app = Flask(__name__)
app.secret_key = "gesthum_secreto"

#para conectarlo con el html
@app.route("/")
def inicio():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    else:
        return redirect(url_for("login"))

# 🔐 Decorador de protección
def login_requerido(roles=None):
    def decorador(f):
        @wraps(f)
        def funcion_protegida(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))

            if roles and session['rol'] not in roles:
                return "Acceso no autorizado", 403

            return f(*args, **kwargs)
        return funcion_protegida
    return decorador


#ruta para los empleados (para mostrar y obtener, etc)
@app.route('/empleados', methods=['GET', 'POST'])
def empleados():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        cedula = request.form['cedula']
        cargo = request.form['cargo']
        departamento = request.form['departamento']
        salario = request.form['salario']
        fecha_ingreso = request.form['fecha_ingreso']
        estado = request.form['estado']

        models.insertar_empleados(
            nombre, apellido, cedula, cargo,
            departamento, salario, fecha_ingreso, estado
        )

        return redirect(url_for('empleados'))

    lista_empleados = models.obtener_empleados()
    return render_template('empleados.html', empleados=lista_empleados)

#Ruta para editar
@app.route('/empleados/editar/<int:id>', methods=['GET', 'POST'])
def editar_empleado(id):
    empleado = models.obtener_empleado_por_id(id)

    if request.method == 'POST':
        models.actualizar_empleado(
            id,
            request.form['nombre'],
            request.form['apellido'],
            request.form['cedula'],
            request.form['cargo'],
            request.form['departamento'],
            request.form['salario'],
            request.form['fecha_ingreso'],
            request.form['estado']
        )
        return redirect(url_for('empleados'))

    return render_template('editar_empleado.html', empleado=empleado)


#ruta pa borrar o eliminar
@app.route('/empleados/eliminar/<int:id>')
def eliminar_empleado(id):
    models.eliminar_empleado(id)
    return redirect(url_for('empleados'))

#Ruta pa nomina
@app.route('/nomina', methods=['GET', 'POST'])
def nomina():
    empleados = models.obtener_empleados()

    if request.method == 'POST':
        empleado_id = request.form['empleado_id']
        fecha = request.form['fecha']

        models.generar_nomina(empleado_id, fecha)
        return redirect(url_for('nomina'))

    nominas = models.obtener_nomina()
    return render_template('nomina.html', empleados=empleados, nominas=nominas)


#Pa el login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        usuario = models.validar_usuario(username, password)

        if usuario:
            session["user_id"] = usuario[0]
            session["rol"] = usuario[3]

            return redirect(url_for("dashboard"))

        else:
            return "Usuario o contraseña incorrectos"

    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

#pal dashboard
@app.route("/dashboard")
@login_requerido()
def dashboard():
    rol = session['rol']

    if rol == "ADMIN":
        return render_template("dashboard_admin.html")

    elif rol == "EMPLEADO":
        return render_template("dashboard_empleado.html")

    else:
        return "Rol no reconocido"


#pa crear un usuario de un empleado vv
@app.route("/crear_usuario", methods=["GET", "POST"])
@login_requerido(roles=["ADMIN"])
def crear_usuario():
    empleados = models.obtener_empleados()

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        rol = request.form["rol"]
        empleado_id = request.form.get("empleado_id")

        #por si no selecciona empleado
        if not empleado_id:
            empleado_id = None
        else:
            empleado_id = int(empleado_id)

        models.crear_usuario(username, password, rol, empleado_id)
        return redirect(url_for("dashboard"))
    
    return render_template("crear_usuario.html", empleados=empleados)


#Pa la ruta de evaluaciones
@app.route("/evaluaciones", methods=["GET", "POST"])
@login_requerido(roles=["ADMIN"])
def evaluaciones():

    empleados = models.obtener_empleados()

    if request.method == "POST":
        empleado_id = request.form["empleado_id"]
        fecha = request.form["fecha"]
        puntuacion = request.form["puntuacion"]
        comentarios = request.form["comentarios"]

        models.crear_evaluacion(empleado_id, fecha, puntuacion, comentarios)

        return redirect(url_for("evaluaciones"))

    lista = models.obtener_evaluaciones()

    return render_template("evaluaciones.html", empleados=empleados, evaluaciones=lista)

#pa la ruta de capacitaciones
@app.route("/capacitaciones", methods=["GET", "POST"])
@login_requerido(roles=["ADMIN"])
def capacitaciones():

    if request.method == "POST":
        nombre = request.form["nombre"]
        fecha = request.form["fecha"]
        estado = request.form["estado"]

        models.crear_capacitacion(nombre, fecha, estado)

        return redirect(url_for("capacitaciones"))

    lista = models.obtener_capacitaciones()

    return render_template("capacitaciones.html", capacitaciones=lista)


@app.route("/mis_evaluaciones")
@login_requerido(roles=["EMPLEADO"])
def mis_evaluaciones():

    user_id = session["user_id"]
    empleado_id = models.obtener_empleado_por_usuario(user_id)

    evaluaciones = models.obtener_evaluaciones_empleado(empleado_id)

    return render_template("mis_evaluaciones.html", evaluaciones=evaluaciones)


@app.route("/mis_capacitaciones")
@login_requerido(roles=["EMPLEADO"])
def mis_capacitaciones():

    capacitaciones = models.obtener_capacitaciones()

    return render_template("mis_capacitaciones.html", capacitaciones=capacitaciones)


@app.route("/mi_nomina")
@login_requerido(roles=["EMPLEADO"])
def mi_nomina():

    user_id = session["user_id"]
    empleado_id = models.obtener_empleado_por_usuario(user_id)

    nomina = models.obtener_nomina_empleado(empleado_id)

    return render_template("mi_nomina.html", nomina=nomina)


#Pa correr la vaina (SIEMPRE va al final de todas las rutas)
if __name__ == "__main__":
    print("INICIANDO SISTEMA GESTHUM")
    models.crear_tabla_empleados()
    models.crear_tabla_usuarios()
    models.crear_tabla_evaluaciones()
    models.crear_tabla_capacitaciones()
    models.crear_tabla_nomina()
    models.crear_admin_por_defecto()
    app.run(debug=True)
