"""API REST completa basada en la guía Python + SQLite + FastAPI."""
from contextlib import asynccontextmanager
import sqlite3
from datetime import date
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from database import get_connection, initialize_database

# Correo sencillo: algo@dominio.ext (sin espacios).
EMAIL_REGEX = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class Base(BaseModel):
    # Quita espacios al inicio y al final de todos los textos ("  Ana " -> "Ana").
    model_config = ConfigDict(str_strip_whitespace=True)


class Persona(Base):
    cedula: str = Field(min_length=1, max_length=30)
    nombre: str = Field(min_length=1, max_length=80)
    apellidos: str = Field(min_length=1, max_length=100)
    correo: str = Field(min_length=3, max_length=120, pattern=EMAIL_REGEX)
    telefono: str = Field(min_length=1, max_length=30)


class Adoptante(Base):
    cedula: str = Field(min_length=1, max_length=30)
    tipo: str = Field(min_length=1, max_length=40)


class Cuidador(Base):
    cedula: str = Field(min_length=1, max_length=30)
    especialidad: str = Field(min_length=1, max_length=80)
    salario_x_hora: float = Field(ge=0, allow_inf_nan=False)


class Alimento(Base):
    identificador: str = Field(min_length=1, max_length=30)
    tipo: str = Field(min_length=1, max_length=60)
    nombre: str = Field(min_length=1, max_length=80)
    precio_x_unidad: float = Field(ge=0, allow_inf_nan=False)


class Cuidado(Base):
    identificador: str = Field(min_length=1, max_length=30)
    nombre: str = Field(min_length=1, max_length=80)


class Dinosaurio(Base):
    codigo: str = Field(min_length=1, max_length=30)
    color: str = Field(min_length=1, max_length=60)
    especie: str = Field(min_length=1, max_length=80)
    dieta: str = Field(min_length=1, max_length=60)
    adoptante: str = Field(min_length=1, max_length=30)


class Adopcion(Base):
    identificador: str = Field(min_length=1, max_length=30)
    fecha: date
    monto_total: float = Field(ge=0, allow_inf_nan=False)
    cantidad_horas_cuidado: float = Field(ge=0, allow_inf_nan=False)
    dinosaurio_adoptado: str = Field(min_length=1, max_length=30)
    cuidador_asignado: str = Field(min_length=1, max_length=30)


class AdopcionAlimento(Base):
    identificador_adopcion: str = Field(min_length=1, max_length=30)
    identificador_alimento: str = Field(min_length=1, max_length=30)


class AdopcionCuidado(Base):
    identificador_adopcion: str = Field(min_length=1, max_length=30)
    identificador_cuidado: str = Field(min_length=1, max_length=30)


MODELS = {"persona": Persona, "adoptante": Adoptante, "cuidador": Cuidador, "alimento": Alimento, "cuidado": Cuidado, "dinosaurio": Dinosaurio, "adopcion": Adopcion, "adopcion_alimento": AdopcionAlimento, "adopcion_cuidado": AdopcionCuidado}
TABLES = set(MODELS)

# Tablas con una sola llave primaria.
PRIMARY_KEYS = {"persona": "cedula", "adoptante": "cedula", "cuidador": "cedula", "alimento": "identificador", "cuidado": "identificador", "dinosaurio": "codigo", "adopcion": "identificador"}
# Tablas de relación: su llave primaria son DOS columnas (no se puede identificar una fila con una sola).
LINK_TABLES = {"adopcion_alimento": ("identificador_adopcion", "identificador_alimento"), "adopcion_cuidado": ("identificador_adopcion", "identificador_cuidado")}

# Para cada tabla: (columna, tabla a la que apunta). Sirve para dar mensajes claros cuando algo no existe.
FOREIGN_KEYS = {
    "adoptante": [("cedula", "persona")],
    "cuidador": [("cedula", "persona")],
    "dinosaurio": [("adoptante", "adoptante")],
    "adopcion": [("dinosaurio_adoptado", "dinosaurio"), ("cuidador_asignado", "cuidador")],
    "adopcion_alimento": [("identificador_adopcion", "adopcion"), ("identificador_alimento", "alimento")],
    "adopcion_cuidado": [("identificador_adopcion", "adopcion"), ("identificador_cuidado", "cuidado")],
}
# Inverso del anterior: quién usa a cada tabla (para explicar por qué no se puede borrar algo).
REFERENCED_BY = {}
for _child, _fks in FOREIGN_KEYS.items():
    for _column, _parent in _fks:
        REFERENCED_BY.setdefault(_parent, []).append((_child, _column))

# Nombres para mostrar en los mensajes de error.
ENTITY_NAMES = {"persona": "Personas", "adoptante": "Adoptantes", "cuidador": "Cuidadores", "alimento": "Alimentos", "cuidado": "Cuidados", "dinosaurio": "Dinosaurios", "adopcion": "Adopciones", "adopcion_alimento": "Adopción-alimento", "adopcion_cuidado": "Adopción-cuidado"}
LABELS = {
    "cedula": "Cédula", "nombre": "Nombre", "apellidos": "Apellidos", "correo": "Correo", "telefono": "Teléfono",
    "tipo": "Tipo", "especialidad": "Especialidad", "salario_x_hora": "Salario por hora",
    "identificador": "Identificador", "precio_x_unidad": "Precio por unidad",
    "codigo": "Código", "color": "Color", "especie": "Especie", "dieta": "Dieta", "adoptante": "Adoptante",
    "fecha": "Fecha", "monto_total": "Monto total", "cantidad_horas_cuidado": "Horas de cuidado",
    "dinosaurio_adoptado": "Dinosaurio adoptado", "cuidador_asignado": "Cuidador asignado",
    "identificador_adopcion": "Adopción", "identificador_alimento": "Alimento", "identificador_cuidado": "Cuidado",
}


def key_columns(table: str):
    """Columnas que identifican una fila de la tabla (una o dos)."""
    return LINK_TABLES.get(table) or (PRIMARY_KEYS[table],)


def check_table(table: str):
    if table not in TABLES:
        raise HTTPException(404, "Entidad no encontrada")


def check_single_key(table: str):
    """Las tablas de relación no se pueden tratar con una sola clave (borraría o cambiaría varias filas)."""
    check_table(table)
    if table in LINK_TABLES:
        raise HTTPException(400, "Esta tabla se identifica con dos claves: usa /api/{tabla}/{clave1}/{clave2}.")


def friendly_errors(exc: ValidationError) -> str:
    """Convierte los errores de Pydantic en una frase en español que el usuario entienda."""
    messages, seen = [], set()
    for err in exc.errors():
        field = str(err["loc"][0]) if err["loc"] else "datos"
        if field in seen:  # Solo el primer problema de cada campo.
            continue
        seen.add(field)
        kind, ctx = err["type"], err.get("ctx", {})
        if kind == "missing":
            text = "es obligatorio"
        elif kind == "string_too_short":
            text = "no puede estar vacío" if ctx.get("min_length") == 1 else f"debe tener al menos {ctx.get('min_length')} caracteres"
        elif kind == "string_too_long":
            text = f"no puede tener más de {ctx.get('max_length')} caracteres"
        elif kind == "string_pattern_mismatch":
            text = "debe ser un correo válido, por ejemplo nombre@correo.com"
        elif kind in ("greater_than_equal", "greater_than"):
            text = "no puede ser negativo"
        elif kind.startswith("date"):
            text = "debe ser una fecha válida (año-mes-día, por ejemplo 2026-10-29)"
        elif kind.startswith("float") or kind.startswith("int"):
            text = "debe ser un número"
        elif kind == "string_type":
            text = "debe ser texto"
        else:
            text = err["msg"]
        messages.append(f"«{LABELS.get(field, field)}» {text}")
    return "Revisa los datos: " + "; ".join(messages) + "."


def validate(table: str, payload: dict) -> dict:
    try:
        return MODELS[table].model_validate(payload).model_dump(mode="json")
    except ValidationError as exc:
        raise HTTPException(422, friendly_errors(exc)) from exc


def row_exists(conn, table: str, columns, values) -> bool:
    where = " AND ".join(f"{c} = ?" for c in columns)
    return conn.execute(f"SELECT 1 FROM {table} WHERE {where}", list(values)).fetchone() is not None


def check_foreign_keys(conn, table: str, data: dict):
    """Verifica que cada referencia exista y explica cuál falta."""
    for column, parent in FOREIGN_KEYS.get(table, []):
        if not row_exists(conn, parent, [PRIMARY_KEYS[parent]], [data[column]]):
            raise HTTPException(422, f"«{LABELS[column]}»: el valor «{data[column]}» no existe en {ENTITY_NAMES[parent]}. Regístralo primero en esa pestaña.")


def dependents_message(table: str, key_values) -> str:
    """Cuenta qué registros impiden borrar y lo explica."""
    parts = []
    with get_connection() as conn:
        for child, column in REFERENCED_BY.get(table, []):
            total = conn.execute(f"SELECT COUNT(*) FROM {child} WHERE {column} = ?", (key_values[0],)).fetchone()[0]
            if total:
                parts.append(f"{total} en {ENTITY_NAMES[child]}")
    if parts:
        return f"No se puede eliminar: este registro está en uso ({', '.join(parts)}). Elimina primero esos registros."
    return "No se puede eliminar: otro registro depende de este."


def db_error(exc: sqlite3.IntegrityError):
    raise HTTPException(409, "No se pudo guardar: los datos chocan con otro registro existente o con una regla de la base de datos.") from exc


def serialize(row): return dict(row)


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(title="Centro de adopción de dinosaurios", version="1.1.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")


@app.exception_handler(RequestValidationError)
async def request_validation_handler(request: Request, exc: RequestValidationError):
    """Si el cuerpo ni siquiera es un objeto JSON, responde con texto (no con una lista) para que se pueda mostrar."""
    return JSONResponse(status_code=422, content={"detail": "Los datos enviados no tienen un formato válido."})


@app.get("/", include_in_schema=False)
def home(): return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.get("/api/{table}")
def list_rows(table: str):
    check_table(table)
    with get_connection() as conn:
        return [serialize(row) for row in conn.execute(f"SELECT * FROM {table}")]


# Va antes de las rutas genéricas de 3 segmentos para que "detalle" no se confunda con una clave.
@app.get("/api/adopcion/{identificador}/detalle")
def adoption_detail(identificador: str):
    with get_connection() as conn:
        adoption = conn.execute("SELECT * FROM adopcion WHERE identificador = ?", (identificador,)).fetchone()
        if not adoption: raise HTTPException(404, "Adopción no encontrada")
        alimentos = conn.execute("SELECT a.* FROM alimento a JOIN adopcion_alimento aa ON a.identificador=aa.identificador_alimento WHERE aa.identificador_adopcion=?", (identificador,)).fetchall()
        cuidados = conn.execute("SELECT c.* FROM cuidado c JOIN adopcion_cuidado ac ON c.identificador=ac.identificador_cuidado WHERE ac.identificador_adopcion=?", (identificador,)).fetchall()
    return {"adopcion": serialize(adoption), "alimentos": [serialize(a) for a in alimentos], "cuidados": [serialize(c) for c in cuidados]}


@app.get("/api/{table}/{key}")
def get_row(table: str, key: str):
    check_single_key(table)
    with get_connection() as conn:
        row = conn.execute(f"SELECT * FROM {table} WHERE {PRIMARY_KEYS[table]} = ?", (key,)).fetchone()
    if not row: raise HTTPException(404, "Registro no encontrado")
    return serialize(row)


@app.get("/api/{table}/{key}/{key2}")
def get_link_row(table: str, key: str, key2: str):
    if table not in LINK_TABLES: raise HTTPException(404, "Entidad no encontrada")
    with get_connection() as conn:
        row = conn.execute(f"SELECT * FROM {table} WHERE {LINK_TABLES[table][0]} = ? AND {LINK_TABLES[table][1]} = ?", (key, key2)).fetchone()
    if not row: raise HTTPException(404, "Registro no encontrado")
    return serialize(row)


@app.post("/api/{table}", status_code=201)
def create_row(table: str, payload: dict):
    check_table(table)
    data = validate(table, payload)
    keys = key_columns(table)
    columns = list(data)
    try:
        with get_connection() as conn:
            if row_exists(conn, table, keys, [data[k] for k in keys]):
                if table in LINK_TABLES:
                    raise HTTPException(409, "Esa relación ya está registrada.")
                raise HTTPException(409, f"Ya existe un registro en {ENTITY_NAMES[table]} con {LABELS[keys[0]]} «{data[keys[0]]}». Usa un valor distinto o edita el registro existente.")
            check_foreign_keys(conn, table, data)
            conn.execute(f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join('?' for _ in columns)})", [data[c] for c in columns])
    except sqlite3.IntegrityError as exc: db_error(exc)
    return data


@app.put("/api/{table}/{key}")
def update_row(table: str, key: str, payload: dict):
    check_single_key(table)
    data = validate(table, payload)
    pk = PRIMARY_KEYS[table]
    if data[pk] != key: raise HTTPException(400, "La clave de la URL debe coincidir con el cuerpo")
    try:
        with get_connection() as conn:
            check_foreign_keys(conn, table, data)
            result = conn.execute(f"UPDATE {table} SET {', '.join(f'{c} = ?' for c in data if c != pk)} WHERE {pk} = ?", [v for c, v in data.items() if c != pk] + [key])
    except sqlite3.IntegrityError as exc: db_error(exc)
    if result.rowcount == 0: raise HTTPException(404, "Registro no encontrado")
    return data


@app.delete("/api/{table}/{key}", status_code=204)
def delete_row(table: str, key: str):
    check_single_key(table)
    try:
        with get_connection() as conn:
            result = conn.execute(f"DELETE FROM {table} WHERE {PRIMARY_KEYS[table]} = ?", (key,))
    except sqlite3.IntegrityError as exc:
        raise HTTPException(409, dependents_message(table, [key])) from exc
    if result.rowcount == 0: raise HTTPException(404, "Registro no encontrado")


@app.delete("/api/{table}/{key}/{key2}", status_code=204)
def delete_link_row(table: str, key: str, key2: str):
    """Borra UNA relación (adopción + alimento, o adopción + cuidado)."""
    if table not in LINK_TABLES: raise HTTPException(404, "Entidad no encontrada")
    first, second = LINK_TABLES[table]
    with get_connection() as conn:
        result = conn.execute(f"DELETE FROM {table} WHERE {first} = ? AND {second} = ?", (key, key2))
    if result.rowcount == 0: raise HTTPException(404, "Registro no encontrado")
