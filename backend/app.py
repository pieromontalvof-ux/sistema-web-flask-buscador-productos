from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)


def conectar_db():
    return sqlite3.connect("database.db")


def inicializar_db():
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            nombre TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE,
            nombre TEXT,
            descripcion TEXT,
            precio REAL,
            stock INTEGER,
            categoria TEXT
        )
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO usuarios (username, password, nombre)
        VALUES ('admin', '1234', 'Administrador')
    """)

    productos = [
        ("P001", "Laptop Lenovo", "Laptop Core i5 de 8GB RAM", 2500.00, 10, "Tecnología"),
        ("P002", "Mouse Logitech", "Mouse inalámbrico", 65.00, 25, "Accesorios"),
        ("P003", "Teclado Redragon", "Teclado mecánico RGB", 180.00, 15, "Accesorios"),
        ("P004", "Monitor Samsung", "Monitor LED 24 pulgadas", 620.00, 8, "Tecnología")
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO productos
        (codigo, nombre, descripcion, precio, stock, categoria)
        VALUES (?, ?, ?, ?, ?, ?)
    """, productos)

    conn.commit()
    conn.close()


@app.route("/")
def inicio():
    return jsonify({
        "mensaje": "Backend Flask funcionando correctamente"
    })


@app.route("/api/login", methods=["POST"])
def login():
    datos = request.get_json()

    username = datos.get("username")
    password = datos.get("password")

    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT nombre FROM usuarios
        WHERE username = ? AND password = ?
    """, (username, password))

    usuario = cursor.fetchone()
    conn.close()

    if usuario:
        return jsonify({
            "acceso": True,
            "nombre": usuario[0]
        })

    return jsonify({
        "acceso": False,
        "mensaje": "Usuario o contraseña incorrectos"
    })


@app.route("/api/buscar_producto", methods=["POST"])
def buscar_producto():
    datos = request.get_json()
    codigo = datos.get("codigo")

    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT codigo, nombre, descripcion, precio, stock, categoria
        FROM productos
        WHERE codigo = ?
    """, (codigo,))

    producto = cursor.fetchone()
    conn.close()

    if producto:
        return jsonify({
            "encontrado": True,
            "codigo": producto[0],
            "nombre": producto[1],
            "descripcion": producto[2],
            "precio": producto[3],
            "stock": producto[4],
            "categoria": producto[5]
        })

    return jsonify({
        "encontrado": False
    })


inicializar_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)