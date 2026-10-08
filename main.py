"""API REST completa basada en la guía Python + SQLite + FastAPI."""
from contextlib import asynccontextmanager
import sqlite3
from datetime import date
from pathlib import Path
from typing import Annotated, Generic, TypeVar

from fastapi import FastAPI, HTTPException, Path as ApiPath, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field

from database import get_connection, initialize_database

class Persona(BaseModel):
    cedula: str = Field(min_length=1, max_length=30)
    nombre: str = Field(min_length=1, max_length=80)
    apellidos: str = Field(min_length=1, max_length=100)
    correo: str = Field(min_length=3, max_length=120)
    telefono: str = Field(min_length=1, max_length=30)
class Adoptante(BaseModel): cedula: str; tipo: str = Field(min_length=1, max_length=40)
class Cuidador(BaseModel): cedula: str; especialidad: str = Field(min_length=1, max_length=80); salario_x_hora: float = Field(ge=0)
class Alimento(BaseModel): identificador: str; tipo: str = Field(min_length=1); nombre: str = Field(min_length=1); precio_x_unidad: float = Field(ge=0)
class Cuidado(BaseModel): identificador: str; nombre: str = Field(min_length=1)
class Dinosaurio(BaseModel): codigo: str; color: str = Field(min_length=1); especie: str = Field(min_length=1); dieta: str = Field(min_length=1); adoptante: str
class Adopcion(BaseModel): identificador: str; fecha: date; monto_total: float = Field(ge=0); cantidad_horas_cuidado: float = Field(ge=0); dinosaurio_adoptado: str; cuidador_asignado: str
class AdopcionAlimento(BaseModel): identificador_adopcion: str; identificador_alimento: str
class AdopcionCuidado(BaseModel): identificador_adopcion: str; identificador_cuidado: str

MODELS = {"persona": Persona, "adoptante": Adoptante, "cuidador": Cuidador, "alimento": Alimento, "cuidado": Cuidado, "dinosaurio": Dinosaurio, "adopcion": Adopcion, "adopcion_alimento": AdopcionAlimento, "adopcion_cuidado": AdopcionCuidado}
PRIMARY_KEYS = {"persona": "cedula", "adoptante": "cedula", "cuidador": "cedula", "alimento": "identificador", "cuidado": "identificador", "dinosaurio": "codigo", "adopcion": "identificador", "adopcion_alimento": "identificador_adopcion", "adopcion_cuidado": "identificador_adopcion"}
TABLES = set(MODELS)

def quoted_columns(data: dict):
    return list(data), list(data.values())
def db_error(exc: sqlite3.IntegrityError):
    raise HTTPException(409, "No se puede completar la operación: clave duplicada o relación inexistente/en uso.") from exc
def serialize(row): return dict(row)

@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield

app = FastAPI(title="Centro de adopción de dinosaurios", version="1.0.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")

@app.get("/", include_in_schema=False)
def home(): return FileResponse(Path(__file__).parent / "static" / "index.html")

@app.get("/api/{table}")
def list_rows(table: str):
    if table not in TABLES: raise HTTPException(404, "Entidad no encontrada")
    with get_connection() as conn:
        return [serialize(row) for row in conn.execute(f"SELECT * FROM {table}")]

@app.get("/api/{table}/{key}")
def get_row(table: str, key: str):
    if table not in TABLES: raise HTTPException(404, "Entidad no encontrada")
    with get_connection() as conn:
        row = conn.execute(f"SELECT * FROM {table} WHERE {PRIMARY_KEYS[table]} = ?", (key,)).fetchone()
    if not row: raise HTTPException(404, "Registro no encontrado")
    return serialize(row)

@app.post("/api/{table}", status_code=201)
def create_row(table: str, payload: dict):
    if table not in TABLES: raise HTTPException(404, "Entidad no encontrada")
    data = MODELS[table].model_validate(payload).model_dump(mode="json")
    columns, values = quoted_columns(data)
    try:
        with get_connection() as conn:
            conn.execute(f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join('?' for _ in columns)})", values)
    except sqlite3.IntegrityError as exc: db_error(exc)
    return data

@app.put("/api/{table}/{key}")
def update_row(table: str, key: str, payload: dict):
    if table not in TABLES: raise HTTPException(404, "Entidad no encontrada")
    data = MODELS[table].model_validate(payload).model_dump(mode="json")
    pk = PRIMARY_KEYS[table]
    if data[pk] != key: raise HTTPException(400, "La clave de la URL debe coincidir con el cuerpo")
    try:
        with get_connection() as conn:
            result = conn.execute(f"UPDATE {table} SET {', '.join(f'{c} = ?' for c in data if c != pk)} WHERE {pk} = ?", [v for c,v in data.items() if c != pk] + [key])
    except sqlite3.IntegrityError as exc: db_error(exc)
    if result.rowcount == 0: raise HTTPException(404, "Registro no encontrado")
    return data

@app.delete("/api/{table}/{key}", status_code=204)
def delete_row(table: str, key: str):
    if table not in TABLES: raise HTTPException(404, "Entidad no encontrada")
    try:
        with get_connection() as conn:
            result = conn.execute(f"DELETE FROM {table} WHERE {PRIMARY_KEYS[table]} = ?", (key,))
    except sqlite3.IntegrityError as exc:
        raise HTTPException(409, "No se puede eliminar: otro registro depende de este. Elimina primero los registros relacionados (por ejemplo, adopción-alimento y adopción-cuidado, luego adopciones, dinosaurios, adoptantes/cuidadores y al final personas).") from exc
    if result.rowcount == 0: raise HTTPException(404, "Registro no encontrado")

@app.get("/api/adopcion/{identificador}/detalle")
def adoption_detail(identificador: str):
    with get_connection() as conn:
        adoption = conn.execute("SELECT * FROM adopcion WHERE identificador = ?", (identificador,)).fetchone()
        if not adoption: raise HTTPException(404, "Adopción no encontrada")
        alimentos = conn.execute("SELECT a.* FROM alimento a JOIN adopcion_alimento aa ON a.identificador=aa.identificador_alimento WHERE aa.identificador_adopcion=?", (identificador,)).fetchall()
        cuidados = conn.execute("SELECT c.* FROM cuidado c JOIN adopcion_cuidado ac ON c.identificador=ac.identificador_cuidado WHERE ac.identificador_adopcion=?", (identificador,)).fetchall()
    return {"adopcion": serialize(adoption), "alimentos": [serialize(a) for a in alimentos], "cuidados": [serialize(c) for c in cuidados]}
