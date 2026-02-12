from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import models

app = Flask(__name__)

#para conectarlo con el html
@app.route("/")
def inicio():
    return render_template("index.html")

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


#Pa correr la vaina (SIEMPRE va al final de todas las rutas)
if __name__ == "__main__":
    models.crear_tabla_empleados()
    models.crear_tabla_usuarios()
    models.crear_tabla_evaluaciones()
    models.crear_tabla_capacitaciones()
    models.crear_tabla_nomina()
    app.run(debug=True)
