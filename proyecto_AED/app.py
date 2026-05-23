from flask import Flask, render_template, request, redirect, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import os
import datetime
import secrets
import time

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY") or secrets.token_hex(24)

# --------------------------------------------------
# Conexión a la base de datos
# --------------------------------------------------
def get_connection(max_retries=3):
    for i in range(max_retries):
        try:
            return mysql.connector.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', 'admin'),
                database=os.getenv('DB_NAME', 'veterinaria')
            )
        except mysql.connector.Error as err:
            if i < max_retries - 1:
                wait_time = 2 ** i
                print(f"Error de conexión. Reintentando en {wait_time} segundos... ({err})")
                time.sleep(wait_time)
            else:
                raise err


# --------------------------------------------------
# Helpers
# --------------------------------------------------
def close_conn(conn):
    try:
        if conn:
            conn.close()
    except Exception:
        pass


# --------------------------------------------------
# Rutas
# --------------------------------------------------
@app.route('/')
def home():
    hoy = datetime.date.today().isoformat()
    max_fecha = (datetime.date.today() + datetime.timedelta(days=90)).isoformat()
    return render_template('home.html', hoy=hoy, max_fecha=max_fecha)


# ============================================================
# REGISTRO (SOLO PARA CLIENTES)
# ============================================================
@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        # Recibir datos del formulario
        correo = request.form.get('correo', '').strip()
        nombre = request.form.get('nombre', '').strip()
        password = request.form.get('password', '').strip()
        telefono = request.form.get('telefono', '').strip()
        direccion = request.form.get('direccion', '').strip()
        rol = request.form.get('rol', 'cliente')  # Por defecto 'cliente'
        especialidad = request.form.get('especialidad', '').strip() if rol == 'veterinario' else None

        # Validar campos obligatorios
        campos_obligatorios = [correo, nombre, password, telefono, direccion]
        if rol == 'veterinario':
            campos_obligatorios.append(especialidad)

        if not all(campos_obligatorios):
            flash("Todos los campos son obligatorios.", "error")
            return render_template('registrar.html')

        # Hashear la contraseña
        hashed_password = generate_password_hash(password)

        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(buffered=True)
            
            cursor.execute("""
                INSERT INTO Cliente (correo, nombre, password, telefono, direccion, rol, especialidad)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (correo, nombre, hashed_password, telefono, direccion, rol, especialidad))
            
            conn.commit()
            cursor.close()
            flash("Registro exitoso. Ahora puedes iniciar sesión.", "success")
            return redirect('/login')
        
        except mysql.connector.Error as err:
            if getattr(err, 'errno', None) == 1062:  # Error de duplicado
                flash("El correo ya está registrado. Intenta iniciar sesión.", "error")
            else:
                flash("Error en el registro. Inténtalo más tarde.", "error")
            return render_template('registrar.html')
        
        finally:
            close_conn(conn)

    # GET: Mostrar formulario
    return render_template('registrar.html')


# ============================================================
# LOGIN
# ============================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form.get('correo', '').strip()
        password = request.form.get('password', '').strip()

        if not correo or not password:
            flash("Correo y contraseña son obligatorios.", "error")
            return render_template('login.html')

        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True, buffered=True)
            cursor.execute("SELECT id_cliente, nombre, password, rol FROM Cliente WHERE correo = %s", (correo,))
            usuario = cursor.fetchone()
            cursor.close()
        except mysql.connector.Error as err:
            flash(f"Error al conectar con la base de datos: {err}", "error")
            return render_template('login.html')
        finally:
            close_conn(conn)

        if usuario and check_password_hash(usuario['password'], password):
            session['cliente_id'] = usuario['id_cliente']
            session['cliente_nombre'] = usuario['nombre']
            session['cliente_rol'] = usuario['rol']
            return redirect('/bienvenido')
        else:
            flash("Correo o contraseña incorrectos.", "error")

    return render_template('login.html')


# ============================================================
# LOGOUT
# ============================================================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# ============================================================
# HORARIOS
# ============================================================
def obtener_horarios_disponibles(id_veterinario, fecha):
    inicio_time = datetime.time(8, 0)
    fin_time = datetime.time(17, 0)
    intervalo = datetime.timedelta(minutes=30)

    slots_dt = []
    actual = datetime.datetime.combine(fecha, inicio_time)
    fin_dt = datetime.datetime.combine(fecha, fin_time) - intervalo
    while actual <= fin_dt:
        slots_dt.append(actual)
        actual += intervalo

    conn = None
    ocupadas = []
    try:
        conn = get_connection()
        cursor = conn.cursor(buffered=True)
        cursor.execute("""
            SELECT TIME_FORMAT(hora, '%%H:%%i') AS hora_str
            FROM Cita
            WHERE fecha = %s AND id_veterinario = %s AND estado IN ('Pendiente', 'Aceptada')
        """, (fecha, id_veterinario))
        rows = cursor.fetchall()
        ocupadas = [r[0] for r in rows if r and r[0]]
        cursor.close()
    except Exception as e:
        print(f"Error al obtener horarios ocupados: {e}")
        ocupadas = []
    finally:
        close_conn(conn)

    disponibles = []
    for s in slots_dt:
        inicio_str = s.time().strftime("%H:%M")
        if inicio_str not in ocupadas:
            disponibles.append((inicio_str, inicio_str))
    return disponibles


@app.route('/disponibles')
def disponibles():
    fecha_str = request.args.get('fecha')
    vet_id_str = request.args.get('veterinario_id')

    if not fecha_str or not vet_id_str:
        return jsonify({"error": "Fecha y veterinario son requeridos"}), 400

    try:
        fecha = datetime.datetime.strptime(fecha_str, "%Y-%m-%d").date()
        vet_id = int(vet_id_str)
    except (ValueError, TypeError):
        return jsonify({"error": "Formato de fecha o ID de veterinario inválido"}), 400

    horarios = obtener_horarios_disponibles(id_veterinario=vet_id, fecha=fecha)
    horarios_obj = [{"slot": h[0], "display": h[0]} for h in horarios]
    return jsonify({"fecha": fecha_str, "horarios": horarios_obj})


# ============================================================
# AGENDAR (CLIENTE)
# ============================================================
@app.route('/agendar', methods=['POST'])
def agendar():
    if session.get('cliente_rol') != 'cliente':
        flash("Solo los clientes pueden agendar citas.", "error")
        return redirect('/bienvenido')

    fecha_str = request.form.get('fecha')
    hora_str = request.form.get('hora')
    vet_id = request.form.get('veterinario_id')
    mascota_nombre = request.form.get('mascota_nombre', '').strip()

    cliente_id = session.get('cliente_id')
    if not cliente_id:
        flash("Error de sesión: No se pudo identificar al cliente.", "error")
        return redirect('/login')

    if not all([fecha_str, hora_str, vet_id, mascota_nombre]):
        flash("Todos los campos (Fecha, Hora, Veterinario, Mascota) son requeridos.", "error")
        return redirect('/bienvenido')

    try:
        fecha = datetime.datetime.strptime(fecha_str, "%Y-%m-%d").date()
        hora_time = datetime.datetime.strptime(hora_str, "%H:%M").time()
        vet_id = int(vet_id)
    except ValueError:
        flash("Formato de fecha/hora o ID de veterinario inválido.", "error")
        return redirect('/bienvenido')

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)

        # 1) Buscar mascota
        cursor.execute("SELECT id_mascota AS id FROM Mascota WHERE id_cliente = %s AND nombre = %s", (cliente_id, mascota_nombre))
        rows = cursor.fetchall()
        if rows:
            mascota_id = rows[0]['id']
        else:
            cursor.execute("INSERT INTO Mascota (nombre, id_cliente) VALUES (%s, %s)", (mascota_nombre, cliente_id))
            mascota_id = cursor.lastrowid
            conn.commit()
            flash(f"Mascota '{mascota_nombre}' registrada automáticamente.", "info")

        # 2) Verificar que el veterinario existe
        cursor.execute("SELECT id_cliente FROM Cliente WHERE id_cliente = %s AND rol = 'veterinario'", (vet_id,))
        vet = cursor.fetchone()
        if not vet:
            flash("Veterinario no encontrado.", "error")
            cursor.close()
            return redirect('/bienvenido')

        # 3) Verificar disponibilidad: veterinario y cliente
        cursor.execute("""
            SELECT 1 
            FROM Cita 
            WHERE fecha = %s AND hora = %s 
              AND (id_veterinario = %s OR id_cliente = %s)
              AND estado IN ('Pendiente','Aceptada')
        """, (fecha, hora_time, vet_id, cliente_id))
        conflict = cursor.fetchone()
        if conflict:
            flash("La hora seleccionada ya está ocupada por ti o por el veterinario. Elige otra.", "error")
            cursor.close()
            return redirect('/bienvenido')

        # 4) Insertar cita
        cursor.execute("""
            INSERT INTO Cita (id_cliente, fecha, hora, id_mascota, id_veterinario, estado) 
            VALUES (%s, %s, %s, %s, %s, 'Pendiente')
        """, (cliente_id, fecha, hora_time, mascota_id, vet_id))
        conn.commit()
        cursor.close()

        flash("Cita agendada correctamente. Pendiente de confirmación del veterinario.", "success")
        return redirect('/bienvenido')

    except mysql.connector.Error as err:
        flash(f"Error al agendar la cita: {err}", "error")
        return redirect('/bienvenido')
    finally:
        close_conn(conn)

# ============================================================
# PANEL BIENVENIDO Y FUNCIONES RELACIONADAS
# ============================================================
def obtener_citas_veterinario(veterinario_id):
    import datetime
    hoy = datetime.date.today()
    conn = None
    citas = []
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute("""
            SELECT 
                c.id_cita, c.fecha, c.hora, c.estado,
                m.nombre AS nombre_mascota,
                cl.nombre AS nombre_cliente, cl.telefono AS telefono_cliente, cl.correo AS correo_cliente
            FROM Cita c
            JOIN Mascota m ON c.id_mascota = m.id_mascota
            JOIN Cliente cl ON m.id_cliente = cl.id_cliente
            WHERE c.id_veterinario = %s AND c.fecha >= %s
            ORDER BY c.fecha, c.hora
        """, (veterinario_id, hoy))
        citas = cursor.fetchall()

        # FORMATEAR HORA
        for c in citas:
            try:
                if c['hora'] is not None:
                    # Si es datetime.time
                    c['hora_str'] = c['hora'].strftime("%H:%M")
                else:
                    c['hora_str'] = "—"
            except Exception:
                # En caso de que sea string
                try:
                    c['hora_str'] = datetime.datetime.strptime(str(c['hora']), "%H:%M:%S").strftime("%H:%M")
                except Exception:
                    c['hora_str'] = str(c['hora'])  # dejar original
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error al cargar citas para el veterinario: {err}")
    finally:
        close_conn(conn)
    return citas


@app.route('/bienvenido')
def bienvenido():
    if 'cliente_id' not in session:
        return redirect('/login')

    cliente_id = session['cliente_id']
    rol = session.get('cliente_rol')

    conn = None
    usuario = None
    mascotas = []
    veterinarios = []
    citas_veterinario = []
    citas_cliente = []

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)

        cursor.execute("SELECT nombre, rol, especialidad FROM Cliente WHERE id_cliente = %s", (cliente_id,))
        usuario = cursor.fetchone()
        if not usuario:
            session.clear()
            cursor.close()
            return redirect('/login')

        if rol == 'cliente':
            cursor.execute("SELECT id_mascota AS id, nombre FROM Mascota WHERE id_cliente = %s", (cliente_id,))
            mascotas = cursor.fetchall()

            cursor.execute("SELECT id_cliente AS id, nombre, especialidad FROM Cliente WHERE rol = 'veterinario' ORDER BY nombre")
            veterinarios = cursor.fetchall()

            # Traer la hora directamente desde la BD
            cursor.execute("""
                SELECT 
                    c.id_cita, c.fecha, c.hora, c.estado,
                    m.nombre AS nombre_mascota,
                    v.nombre AS nombre_veterinario
                FROM Cita c
                JOIN Mascota m ON c.id_mascota = m.id_mascota
                LEFT JOIN Cliente v ON c.id_veterinario = v.id_cliente
                WHERE m.id_cliente = %s AND c.fecha >= %s
                ORDER BY c.fecha, c.hora
            """, (cliente_id, datetime.date.today()))
            citas_cliente = cursor.fetchall()

            # FORMATEAR HORA en Python
            for c in citas_cliente:
                try:
                    if c['hora'] is not None:
                        c['hora_str'] = c['hora'].strftime("%H:%M")
                    else:
                        c['hora_str'] = "—"
                except Exception:
                    # por si fuera string
                    try:
                        c['hora_str'] = datetime.datetime.strptime(str(c['hora']), "%H:%M:%S").strftime("%H:%M")
                    except Exception:
                        c['hora_str'] = str(c['hora'])

        elif rol == 'veterinario':
            cursor.close()
            citas_veterinario = obtener_citas_veterinario(cliente_id)

        cursor.close()

    except mysql.connector.Error as err:
        flash(f"Error al cargar tu perfil: {err}", "error")
        return redirect('/login')
    finally:
        close_conn(conn)

    hoy = datetime.date.today().isoformat()
    max_fecha = (datetime.date.today() + datetime.timedelta(days=90)).isoformat()

    return render_template('bienvenido.html', 
                            nombre=usuario['nombre'], 
                            rol=rol,
                            especialidad=usuario.get('especialidad'),
                            mascotas=mascotas,
                            veterinarios=veterinarios,
                            citas_veterinario=citas_veterinario,
                            citas_cliente=citas_cliente,
                            hoy=hoy,
                            max_fecha=max_fecha)



# ============================================================
# VETERINARIO: ACEPTAR CITA
# ============================================================
@app.route('/veterinario/aceptar_cita/<int:cita_id>', methods=['POST'])
def aceptar_cita(cita_id):
    if session.get('cliente_rol') != 'veterinario':
        flash("Acceso no autorizado.", "error")
        return redirect('/bienvenido')

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(buffered=True)
        cursor.execute("SELECT id_veterinario FROM Cita WHERE id_cita = %s", (cita_id,))
        row = cursor.fetchone()
        if not row or row[0] != session['cliente_id']:
            cursor.close()
            flash("Cita no encontrada o no te pertenece.", "error")
            return redirect('/bienvenido')

        cursor.execute("UPDATE Cita SET estado = 'Aceptada' WHERE id_cita = %s", (cita_id,))
        conn.commit()
        cursor.close()
        flash(f"Cita #{cita_id} aceptada. El cliente ha sido notificado.", "success")
        return redirect('/bienvenido')

    except mysql.connector.Error as err:
        flash(f"Error al aceptar la cita: {err}", "error")
        return redirect('/bienvenido')
    finally:
        close_conn(conn)

# ============================================================
# CREAR EXPEDIENTE (VETERINARIO)
# ============================================================
@app.route('/crear_expediente', methods=['GET', 'POST'])
def crear_expediente():
    # Solo veterinarios pueden acceder
    if 'cliente_id' not in session or session.get('cliente_rol') != 'veterinario':
        flash("Debes iniciar sesión como veterinario.", "error")
        return redirect('/login')

    vet_id = session['cliente_id']

    conn = None
    mascotas = []
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)

        # Traer todas las mascotas para que el veterinario elija
        cursor.execute("""
            SELECT m.id_mascota AS id, m.nombre AS nombre, c.nombre AS cliente_nombre
            FROM Mascota m
            JOIN Cliente c ON m.id_cliente = c.id_cliente
            ORDER BY c.nombre, m.nombre
        """)
        mascotas = cursor.fetchall()

        if request.method == 'POST':
            # Obtener datos del formulario
            mascota_id = request.form.get('mascota_id')
            especie = request.form.get('especie', '').strip()
            raza = request.form.get('raza', '').strip() or None
            edad = request.form.get('edad', '').strip()
            peso = request.form.get('peso', '').strip()
            fecha = datetime.date.today()

            # Validación mínima
            if not mascota_id or not especie:
                flash("Debes seleccionar la mascota y la especie.", "error")
                return redirect('/crear_expediente')

            # Convertir edad y peso a tipos correctos
            edad = int(edad) if edad.isdigit() else None
            peso = float(peso) if peso.replace('.', '', 1).isdigit() else None

            # Insertar expediente
            cursor.execute("""
                INSERT INTO Expediente (id_mascota, especie, raza, edad, peso, fecha_creacion)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (mascota_id, especie, raza, edad, peso, fecha))
            conn.commit()
            flash("Expediente creado correctamente.", "success")
            return redirect('/bienvenido')

        cursor.close()
    except mysql.connector.Error as err:
        flash(f"Error al crear expediente: {err}", "error")
        return redirect('/crear_expediente')
    finally:
        close_conn(conn)

    return render_template('crear_expediente.html', mascotas=mascotas)

# ============================================================
# VETERINARIO: VER CITAS (INTERFAZ)
# ============================================================
@app.route('/veterinario/citas')
def veterinario_citas():
    if 'cliente_id' not in session or session.get('cliente_rol') != 'veterinario':
        return redirect('/login')

    id_vet = session['cliente_id']
    fecha_hoy = datetime.date.today()

    conn = None
    citas = []
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute("""
            SELECT c.hora, cl.nombre AS cliente, m.nombre AS mascota, c.motivo
            FROM Cita c
            JOIN Cliente cl ON c.id_cliente = cl.id_cliente
            JOIN Mascota m ON c.id_mascota = m.id_mascota
            WHERE c.id_veterinario = %s AND c.fecha = %s
            ORDER BY c.hora
        """, (id_vet, fecha_hoy))
        citas = cursor.fetchall()
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error veterinario_citas: {err}")
    finally:
        close_conn(conn)

    return render_template('veterinario_citas.html', citas=citas)


# ============================================================
# EJECUCIÓN
# ============================================================
if __name__ == '__main__':
    app.run(debug=True, port=5000)
