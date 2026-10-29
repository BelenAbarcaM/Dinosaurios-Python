-- Script de creación de dinosaurios.db (tablas vacías)
PRAGMA foreign_keys = ON;
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
