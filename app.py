from flask import Flask, request, render_template_string
import sqlite3
import re
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Función para registrar eventos en eventos.log (Requisito de seguridad)
def registrar_evento(evento, usuario):
    tiempo_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("eventos.log", "a") as f:
        f.write(f"{tiempo_actual}, {evento}, {usuario}\n")

# Crear la base de datos y tabla automáticamente si no existen
def init_db():
    conexion = sqlite3.connect("usuarios.db")
    cursor = conexion.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            correo TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conexion.commit()
    conexion.close()

init_db()

@app.route("/")
def inicio():
    return '<h1>Laboratorio de Ciberseguridad</h1><p><a href="/registro">Ir al Registro</a> | <a href="/login">Ir al Login</a></p>'

@app.route("/registro", methods=["GET", "POST"])
def registro():
    mensaje = ""
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        correo = request.form.get("correo", "").strip()
        password = request.form.get("password", "")

        # Validaciones de la guía
        if not re.fullmatch(r"[A-Za-z0-9_]{4,20}", usuario):
            mensaje = "Usuario inválido."
        elif not re.fullmatch(r"^[A-Za-z0-9_.%+]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", correo):
            mensaje = "Correo electrónico inválido."
        elif len(password) < 8:
            mensaje = "La contraseña debe contener al menos 8 caracteres."
        else:
            try:
                # Cifrado seguro de la contraseña (Hash)
                password_cifrada = generate_password_hash(password)
                conexion = sqlite3.connect("usuarios.db")
                cursor = conexion.cursor()
                cursor.execute(
                    "INSERT INTO usuarios (usuario, correo, password) VALUES (?, ?, ?)",
                    (usuario, correo, password_cifrada)
                )
                conexion.commit()
                conexion.close()
                return "<h3>¡Usuario registrado con éxito!</h3><br><a href='/login'>Iniciar Sesión</a> | <a href='/'>Inicio</a>"
            except Exception as e:
                # Evita registros duplicados (Control de excepciones por UNIQUE)
                mensaje = "El usuario o correo ya existe en la base de datos."

    html = """
    <h2>Registro - Ciberseguridad</h2>
    <p style="color: red; font-weight: bold;">{{ mensaje }}</p>
    <form method="POST">
        <label>Usuario:</label><br>
        <input type="text" name="usuario" required><br><br>
        
        <label>Correo:</label><br>
        <input type="email" name="correo" required><br><br>
        
        <label>Contraseña (mínimo 8 caracteres):</label><br>
        <input type="password" name="password" required><br><br>
        
        <button type="submit">Registrarse</button>
    </form>
    <br><a href="/">Volver al inicio</a>
    """
    return render_template_string(html, mensaje=mensaje)

@app.route("/login", methods=["GET", "POST"])
def login():
    mensaje = ""
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        password = request.form.get("password", "")
        
        conexion = sqlite3.connect("usuarios.db")
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE usuario = ?", (usuario,))
        user = cursor.fetchone()
        conexion.close()
        
        # Verificación segura del hash y registro de logs de éxito/fallo
        if user and check_password_hash(user[3], password):
            registrar_evento("login_correcto", usuario)
            return f"<h3>¡Bienvenido de nuevo, {user[1]}!</h3><br><a href='/'>Volver al inicio</a>"
        else:
            registrar_evento("login_fallido", usuario)
            mensaje = "Credenciales incorrectas"
            
    html = """
    <h2>Iniciar Sesión - Ciberseguridad</h2>
    <p style="color: red; font-weight: bold;">{{ mensaje }}</p>
    <form method="POST">
        <label>Usuario:</label><br>
        <input type="text" name="usuario" required><br><br>
        
        <label>Contraseña:</label><br>
        <input type="password" name="password" required><br><br>
        
        <button type="submit">Entrar</button>
    </form>
    <br><a href="/">Volver al inicio</a>
    """
    return render_template_string(html, mensaje=mensaje)

if __name__ == "__main__":
    app.run(debug=True)