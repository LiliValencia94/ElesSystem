from flask import Flask, render_template, request, redirect, url_for, flash, session
import pyodbc 
import os 
from functools import wraps 
from werkzeug.utils import secure_filename 

# ===================================================
# CONFIGURACIÓN INICIAL Y DE BASE DE DATOS
# ===================================================

app = Flask(__name__)
app.config['SECRET_KEY'] = 'una_clave_secreta_muy_larga_y_segura_para_flask_session' 

UPLOAD_FOLDER = 'uploads' 
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Nombre del servidor verificado: DESKTOP-N8V3NEK\SQLEXPRESS
CONNECTION_STRING = (
    r'DRIVER={SQL Server};'  
    r'SERVER=DESKTOP-N8V3NEK\SQLEXPRESS;' 
    r'DATABASE=ElesSystemDB;'
    r'Trusted_Connection=yes;'
)

def get_db_connection():
    """Establece y devuelve una conexión a la base de datos."""
    try:
        conn = pyodbc.connect(CONNECTION_STRING)
        return conn
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        print(f"Error CRÍTICO al conectar a SQL Server: {sqlstate}")
        return None

# ===================================================
# FUNCIONES DE VERIFICACIÓN DE SESIÓN Y ROLES
# ===================================================

def login_required(f):
    """Decorador que verifica si el usuario ha iniciado sesión."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_rol' not in session:
            flash('Debe iniciar sesión para acceder.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def requires_admin(f):
    """Decorador que verifica si el rol es 'Administrador'."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_rol') != 'Administrador':
            # La acción CRÍTICA es redirigir al menú.
            flash('Acceso denegado: Se requiere ser Administrador.', 'error')
            return redirect(url_for('menu')) 
        return f(*args, **kwargs)
    return decorated_function

# ===================================================
# RUTAS DE AUTENTICACIÓN Y MENÚ
# ===================================================

@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        usuario = request.form.get("usuario")
        clave = request.form.get("clave")
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                sql_query = "SELECT clave, rol FROM dbo.Usuarios WHERE usuario = ?"
                cursor.execute(sql_query, (usuario,))
                row = cursor.fetchone()
                
                if row and row[0] == clave:
                    session['user_rol'] = row[1] 
                    session['user_name'] = usuario 
                    return redirect(url_for("menu"))
                else:
                    error = "Usuario o contraseña incorrectos"
                
            except Exception as e:
                print(f"Error de autenticación: {e}")
                error = "Error de conexión o base de datos."
            finally:
                if cursor: cursor.close()
                if conn: conn.close()
        else:
            error = "Error al intentar conectar a la base de datos."
            
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear() 
    return redirect(url_for('login'))

@app.route("/menu", methods=["GET"])
@login_required 
def menu():
    return render_template("menu_inicio.html")

# ===================================================
# RUTAS DE GESTIÓN DE EMPLEADOS
# ===================================================

@app.route("/empleado/nuevo", methods=["GET", "POST"]) 
@requires_admin # PROTEGIDA: Solo Administradores
def nuevo_empleado():
    mensaje = None
    
    if request.method == "POST":
        nombre_form = request.form.get("nombre")
        cedula_form = request.form.get("cedula")
        area_form = request.form.get("area")
        
        archivos = {
            'examenes_medicos': request.files.get('examenes_medicos'),
            'examenes_induccion': request.files.get('examenes_induccion'),
            'carnet_covid': request.files.get('carnet_covid')
        }
        
        conn = get_db_connection()
        
        if conn:
            cursor = conn.cursor()
            sql_insert = "INSERT INTO dbo.Empleados (nombre, cedula, area) VALUES (?, ?, ?)"
            
            try:
                cursor.execute(sql_insert, (nombre_form, cedula_form, area_form))
                conn.commit() 
                
                archivos_subidos = 0
                for file_key, file in archivos.items():
                    if file and file.filename != '' and allowed_file(file.filename):
                        filename = secure_filename(f"{cedula_form}_{file_key}_{file.filename}")
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        archivos_subidos += 1
                
                # Ejemplo de éxito: "Empleado agregado exitosamente."
                flash(f"Éxito: Empleado {nombre_form} registrado. ({archivos_subidos} documentos subidos).", 'success')
                return redirect(url_for('nuevo_empleado')) 
            
            except pyodbc.IntegrityError:
                mensaje = "Error: La cédula ingresada ya está registrada (duplicada)."
            except Exception as e:
                print(f"\n--- ERROR SQL INSERCIÓN EMPLEADO ---\n{e}\n-------------------------------------------------\n")
                mensaje = "Error al registrar empleado. Falla en la base de datos."
            finally:
                if cursor: cursor.close()
                if conn: conn.close()
        else:
            mensaje = "Error de conexión: No se pudo establecer la conexión a la base de datos."
    
    return render_template("nuevo_empleado.html", mensaje=mensaje)


@app.route("/empleado/buscar", methods=["GET", "POST"])
@login_required # ABIERTA: Para Administradores y Empleados
def buscar_empleado():
    empleado_encontrado = None
    mensaje = None
    
    if request.method == "POST":
        documento = request.form.get("documento") 
        conn = get_db_connection()
        
        if conn:
            cursor = conn.cursor()
            
            try:
                # La búsqueda se realiza por cédula
                sql_query = "SELECT id, nombre, cedula, area FROM dbo.Empleados WHERE CAST(cedula AS VARCHAR(50)) = ?"
                cursor.execute(sql_query, (documento,)) 
                row = cursor.fetchone()
                
                if row:
                    empleado_encontrado = {
                        "id": row[0],
                        "nombre": row[1],
                        "documento": row[2],  
                        "cargo": row[3]       
                    }
                    mensaje = "Empleado encontrado exitosamente."
                else:
                    mensaje = f"No se encontró un empleado con el documento/cédula: {documento}"
            
            except Exception as e:
                mensaje = f"Ocurrió un error al buscar en la base de datos: {e}"
            finally:
                if cursor: cursor.close()
                if conn: conn.close()
        else:
            mensaje = "Error de conexión: No se pudo establecer la conexión a la base de datos."
            
    return render_template(
        "buscar_empleado.html",
        empleado=empleado_encontrado,
        mensaje=mensaje
    )

# ===================================================
# RUTAS DE GESTIÓN DE USUARIOS (CRUD)
# ===================================================

@app.route("/usuarios", methods=["GET"])
@requires_admin # PROTEGIDA: Solo Administradores
def usuarios():
    conn = get_db_connection()
    usuarios_list = []
    mensaje = None
    
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, usuario, rol FROM dbo.Usuarios ORDER BY id")
            
            for row in cursor.fetchall():
                usuarios_list.append({
                    'id': row[0],
                    'usuario': row[1],
                    'rol': row[2]
                })
            
        except Exception as e:
            mensaje = f"Error al cargar usuarios de la BD: {e}"
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
    else:
        mensaje = "Error de conexión a la base de datos."
        
    return render_template("usuarios.html", usuarios=usuarios_list, mensaje=mensaje)


@app.route("/usuario/crear", methods=["POST"])
@requires_admin # PROTEGIDA: Solo Administradores
def crear_usuario():
    if request.method == "POST":
        nuevo_usuario = request.form.get("nuevo_usuario")
        nueva_clave = request.form.get("nueva_clave")
        rol_usuario = request.form.get("rol")
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            sql_insert = "INSERT INTO dbo.Usuarios (usuario, clave, rol) VALUES (?, ?, ?)"
            
            try:
                cursor.execute(sql_insert, (nuevo_usuario, nueva_clave, rol_usuario))
                conn.commit()
                flash(f"Usuario '{nuevo_usuario}' creado exitosamente.", 'success')
            
            except pyodbc.IntegrityError:
                flash("Error: El nombre de usuario ya existe. Por favor, elija otro.", 'error')
            except Exception as e:
                flash(f"Error al crear usuario: {e}", 'error')
            finally:
                if cursor: cursor.close()
                if conn: conn.close()
                
    return redirect(url_for('usuarios'))

@app.route("/usuario/eliminar/<int:user_id>", methods=["POST"])
@requires_admin # PROTEGIDA: Solo Administradores
def eliminar_usuario(user_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM dbo.Usuarios WHERE id = ?", (user_id,))
            conn.commit()
            flash(f"Usuario con ID {user_id} eliminado exitosamente.", 'success')
        except Exception as e:
            flash(f"Error al eliminar usuario {user_id}: {e}", 'error')
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
            
    return redirect(url_for('usuarios'))


# ===================================================
# INICIO DE LA APLICACIÓN
# ===================================================

if __name__ == "__main__":
    app.run(debug=True)