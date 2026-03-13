import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash


#coneccion con la base de datos
def get_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

#Creacion de la tabla empleados
def crear_tabla_empleados():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS empleados(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        apellido TEXT NOT NULL,
        cedula TEXT UNIQUE NOT NULL,
        cargo TEXT,
        departamento TEXT,
        salario REAL,
        fecha_ingreso TEXT,
        estado TEXT
    )
    """)
    conn.commit()
    conn.close()


#Tabla para los usuarios
def crear_tabla_usuarios():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        rol TEXT NOT NULL,
        empleado_id INTEGER,
        FOREIGN KEY (empleado_id) REFERENCES empleados(id)
    )
    """)

    conn.commit()
    conn.close()


#Tabla para las evaluaciones
def crear_tabla_evaluaciones():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS evaluaciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        empleado_id INTEGER,
        fecha TEXT,
        puntuacion INTEGER,
        comentarios TEXT,
        FOREIGN KEY (empleado_id) REFERENCES empleados(id)
    )
    """)

    conn.commit()
    conn.close()


#Tabla para las Capacitaciones
def crear_tabla_capacitaciones():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS capacitaciones(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        fecha text,
        estado text     
    )
    """)
    conn.commit()
    conn.close()
    


#Aqui se van a insertar los empleados
def insertar_empleados(nombre, apellido, cedula, cargo, departamento, salario, fecha_ingreso, estado):
    conn = get_connection()
    cursor = conn.cursor()

    '''cursor.execute("""
        INSERT INTO empleados 
        (nombre, apellido, cedula, cargo, departamento, salario, fecha_ingreso, estado)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (nombre, apellido, cedula, cargo, departamento, salario, fecha_ingreso, estado))'''

    cursor.execute("""
        INSERT INTO empleados (nombre, apellido, cedula, cargo, departamento, salario, fecha_ingreso, estado) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (nombre, apellido, cedula, cargo, departamento, salario, fecha_ingreso, estado))

    conn.commit()
    conn.close()

#Como dice la funcion, aqui obtenemos a los empleados
def obtener_empleados():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM empleados")
    empleados = cursor.fetchall()
    conn.close()
    return empleados


#Para actualizar empleados
def obtener_empleado_por_id(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM empleados WHERE id = ?", (id,))
    empleado = cursor.fetchone()
    conn.close()
    return empleado


def actualizar_empleado(id, nombre, apellido, cedula, cargo, departamento, salario, fecha_ingreso, estado):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE empleados
        SET nombre=?, apellido=?, cedula=?, cargo=?, departamento=?,
            salario=?, fecha_ingreso=?, estado=?
        WHERE id=?
    """, (nombre, apellido, cedula, cargo, departamento, salario, fecha_ingreso, estado, id))

    conn.commit()
    conn.close()


#para eliminar los empleados
def eliminar_empleado(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM empleados WHERE id = ?", (id,))
    conn.commit()
    conn.close()



#Pa la nomina
def crear_tabla_nomina():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS nomina (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        empleado_id INTEGER,
        salario_base REAL,
        afp REAL,
        sfs REAL,
        salario_neto REAL,
        fecha TEXT,
        FOREIGN KEY (empleado_id) REFERENCES empleados(id)
    )
    """)

    conn.commit()
    conn.close()


def obtener_salario_empleado(empleado_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT salario FROM empleados WHERE id = ?", (empleado_id)
    )
    
    resultado = cursor.fetchone()
    conn.close()
    return resultado['salario']




def generar_nomina(empleado_id, fecha):
    salario_base = obtener_salario_empleado(empleado_id)

    afp = salario_base * 0.0287
    sfs = salario_base * 0.0304
    salario_neto = salario_base - afp - sfs

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO nomina 
        (empleado_id, salario_base, afp, sfs, salario_neto, fecha)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (empleado_id, salario_base, afp, sfs, salario_neto, fecha))

    conn.commit()
    conn.close()



def obtener_nomina():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT nomina.*, empleados.nombre, empleados.apellido
        FROM nomina
        JOIN empleados ON nomina.empleado_id = empleados.id
    """)

    datos = cursor.fetchall()
    conn.close()
    return datos


#Para el login
def crear_usuario(username, password, rol, empleado_id=None):
    pasword_hash = generate_password_hash(password)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""INSERT INTO usuarios(username, password, rol, empleado_id) VALUES INTO (?, ?, ?, ?)""", (username, password, rol, empleado_id))
    conn.commit()
    conn.close()


#Pa Validar el login

def validar_usuario(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, username, password, rol FROM usuarios WHERE username = ?",
        (username,)
    )

    usuario = cursor.fetchone()
    conn.close()

    if usuario:
        password_hash = usuario[2]

        if check_password_hash(password_hash, password):
            return usuario

    return None

#pa que se cree un admin por defecto
def crear_admin_por_defecto():
    conn = get_connection()
    cursor = conn.cursor()

    print("Verificando creación de admin...")

    cursor.execute("SELECT * FROM usuarios WHERE username = ?", ("admin",))
    admin = cursor.fetchone()

    if not admin:
        print("ADMIN CREADO")
        password_hash = generate_password_hash("admin")

        cursor.execute("""
            INSERT INTO usuarios (username, password, rol)
            VALUES (?, ?, ?)
        """, ("admin", password_hash, "ADMIN"))

        conn.commit()

    conn.close()
