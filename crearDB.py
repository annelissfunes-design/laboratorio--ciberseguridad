import sqlite3

# Crear o abrir la base de datos
conexion = sqlite3.connect("usuarios.db")
cursor = conexion.cursor()

# Crear tabla
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT,
    correo TEXT,
    password TEXT
);
""")

conexion.commit()
conexion.close()

print("Base de datos y tabla creadas correctamente.")