"""Esquema y utilidades de SQLite para el centro de adopción de dinosaurios."""
from pathlib import Path
import os
import shutil
import sqlite3

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "dinosaurios.db"

# En Vercel el disco del proyecto es de solo lectura: se copia la base a /tmp para poder escribir.
if os.environ.get("VERCEL"):
    _tmp = Path("/tmp/dinosaurios.db")
    if not _tmp.exists() and DB_PATH.exists():
        shutil.copy(DB_PATH, _tmp)
    DB_PATH = _tmp

SCHEMA = """
CREATE TABLE IF NOT EXISTS persona (
  cedula TEXT PRIMARY KEY, nombre TEXT NOT NULL, apellidos TEXT NOT NULL,
  correo TEXT NOT NULL, telefono TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS adoptante (
  cedula TEXT PRIMARY KEY, tipo TEXT NOT NULL,
  FOREIGN KEY (cedula) REFERENCES persona(cedula) ON DELETE RESTRICT
);
CREATE TABLE IF NOT EXISTS cuidador (
  cedula TEXT PRIMARY KEY, especialidad TEXT NOT NULL, salario_x_hora REAL NOT NULL CHECK(salario_x_hora >= 0),
  FOREIGN KEY (cedula) REFERENCES persona(cedula) ON DELETE RESTRICT
);
CREATE TABLE IF NOT EXISTS alimento (
  identificador TEXT PRIMARY KEY, tipo TEXT NOT NULL, nombre TEXT NOT NULL, precio_x_unidad REAL NOT NULL CHECK(precio_x_unidad >= 0)
);
CREATE TABLE IF NOT EXISTS cuidado (
  identificador TEXT PRIMARY KEY, nombre TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS dinosaurio (
  codigo TEXT PRIMARY KEY, color TEXT NOT NULL, especie TEXT NOT NULL, dieta TEXT NOT NULL, adoptante TEXT NOT NULL,
  FOREIGN KEY (adoptante) REFERENCES adoptante(cedula) ON DELETE RESTRICT
);
CREATE TABLE IF NOT EXISTS adopcion (
  identificador TEXT PRIMARY KEY, fecha TEXT NOT NULL, monto_total REAL NOT NULL CHECK(monto_total >= 0),
  cantidad_horas_cuidado REAL NOT NULL CHECK(cantidad_horas_cuidado >= 0),
  dinosaurio_adoptado TEXT NOT NULL, cuidador_asignado TEXT NOT NULL,
  FOREIGN KEY (dinosaurio_adoptado) REFERENCES dinosaurio(codigo) ON DELETE RESTRICT,
  FOREIGN KEY (cuidador_asignado) REFERENCES cuidador(cedula) ON DELETE RESTRICT
);
CREATE TABLE IF NOT EXISTS adopcion_alimento (
  identificador_adopcion TEXT NOT NULL, identificador_alimento TEXT NOT NULL,
  PRIMARY KEY (identificador_adopcion, identificador_alimento),
  FOREIGN KEY (identificador_adopcion) REFERENCES adopcion(identificador) ON DELETE CASCADE,
  FOREIGN KEY (identificador_alimento) REFERENCES alimento(identificador) ON DELETE RESTRICT
);
CREATE TABLE IF NOT EXISTS adopcion_cuidado (
  identificador_adopcion TEXT NOT NULL, identificador_cuidado TEXT NOT NULL,
  PRIMARY KEY (identificador_adopcion, identificador_cuidado),
  FOREIGN KEY (identificador_adopcion) REFERENCES adopcion(identificador) ON DELETE CASCADE,
  FOREIGN KEY (identificador_cuidado) REFERENCES cuidado(identificador) ON DELETE RESTRICT
);
"""

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def initialize_database():
    with get_connection() as conn:
        conn.executescript(SCHEMA)
