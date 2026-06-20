"""
database.py
Conexión a SQLite, creación del esquema y utilidades relacionadas
con la persistencia de datos del Sistema de Gestión Académica.
"""
import sqlite3
import hashlib


def hash_password(password: str) -> str:
    """Convierte la contraseña en un hash SHA-256 (nunca se guarda texto plano)."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def conectar_db(ruta: str = "control_actividades.db"):
    """Establece la conexión con SQLite y crea las tablas si no existen.

    Devuelve (conexion, cursor).
    """
    conexion = sqlite3.connect(ruta)
    cursor = conexion.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

    # Usuarios: credenciales y rol (docente / estudiante)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            contrasena TEXT NOT NULL,
            rol TEXT NOT NULL
        )
    """)

    # Materias: cada materia pertenece a un docente que la dicta
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS materias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            docente_id INTEGER NOT NULL,
            FOREIGN KEY (docente_id) REFERENCES usuarios(id) ON DELETE CASCADE,
            UNIQUE(nombre, docente_id)
        )
    """)

    # Inscripciones: relación estudiante <-> materia
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inscripciones (
            usuario_id INTEGER NOT NULL,
            materia_id INTEGER NOT NULL,
            PRIMARY KEY (usuario_id, materia_id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
            FOREIGN KEY (materia_id) REFERENCES materias(id) ON DELETE CASCADE
        )
    """)

    # Actividades: publicadas por el docente dentro de una materia
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS actividades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            materia_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            fecha TEXT NOT NULL,
            descripcion TEXT,
            FOREIGN KEY (materia_id) REFERENCES materias(id) ON DELETE CASCADE
        )
    """)

    # Entregas: estado de cada actividad, particular para cada estudiante
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entregas (
            usuario_id INTEGER NOT NULL,
            actividad_id INTEGER NOT NULL,
            estado TEXT DEFAULT 'Pendiente',
            PRIMARY KEY (usuario_id, actividad_id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
            FOREIGN KEY (actividad_id) REFERENCES actividades(id) ON DELETE CASCADE
        )
    """)

    # Actividades académicas propias del estudiante: cada estudiante organiza
    # las suyas de forma individual, sin relación con materias ni docentes
    # del módulo de Docente. El campo "materia" es simple texto libre que el
    # propio estudiante escribe, solo para agrupar/identificar su actividad.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS actividades_estudiante (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            materia TEXT,
            tipo TEXT NOT NULL,
            fecha TEXT NOT NULL,
            descripcion TEXT,
            estado TEXT DEFAULT 'Pendiente',
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        )
    """)

    # Migración: si la tabla ya existía de una versión anterior (sin la
    # columna "materia"), se agrega ahora sin perder los datos existentes.
    columnas = [fila[1] for fila in cursor.execute("PRAGMA table_info(actividades_estudiante)")]
    if "materia" not in columnas:
        cursor.execute("ALTER TABLE actividades_estudiante ADD COLUMN materia TEXT")

    conexion.commit()
    return conexion, cursor


# Constantes visuales compartidas por las pantallas de docente y estudiante
COLORES_TIPO = {
    "Evaluación": "#E74C3C",
    "Proyecto": "#E67E22",
    "Laboratorio": "#9B59B6",
    "Tarea": "#3498DB",
}
COLOR_ENTREGADO = "#2ECC71"
COLOR_PENDIENTE = "#7F8C8D"
