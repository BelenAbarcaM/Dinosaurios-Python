# Centro de adopción de dinosaurios prehistóricos

## Descripción
Aplicación web para administrar un centro donde las personas pueden adoptar dinosaurios prehistóricos.
Permite registrar personas, adoptantes, cuidadores, dinosaurios, alimentos, cuidados y las adopciones
con todo su detalle (CRUD completo sobre las 9 tablas).

## Análisis y planteamiento
- **Problema:** el centro controla las adopciones, los cuidadores y la alimentación de cada dinosaurio en papel, lo que provoca pérdidas de información y errores en los cobros.
- **Objetivo general:** centralizar en una sola aplicación web la información del centro y de sus adopciones.
- **Funcionalidades principales:** registrar, consultar, editar y eliminar personas, adoptantes, cuidadores, dinosaurios, alimentos, cuidados y adopciones; ver el detalle de una adopción (alimentos y cuidados incluidos).
- **Usuarios:** personal administrativo del centro, cuidadores y encargados de las adopciones.

## Tecnologías utilizadas
Python · FastAPI · SQLite · HTML, CSS y JavaScript · GitHub · Vercel

## Instalación
```bash
python -m venv venv
venv\Scripts\activate        # En Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
```

## Ejecución
```bash
uvicorn main:app --reload
```
Abrir <http://127.0.0.1:8000>. La documentación automática de la API está en <http://127.0.0.1:8000/docs>.
La base `dinosaurios.db` se crea sola si no existe; `docs/crear_base_de_datos.sql` contiene el script de creación de las tablas (sin datos).

## Estructura del sistema
```
├── main.py                  # API FastAPI (rutas CRUD y validaciones)
├── database.py              # Esquema SQLite y conexión
├── dinosaurios.db           # Base de datos SQLite
├── static/
│   ├── index.html           # Estructura de la interfaz
│   ├── styles.css           # Estilos (tema verde)
│   └── app.js               # Lógica del frontend (consume la API)
├── docs/
│   ├── diagrama_er.md / .png # Diagrama entidad-relación
│   └── crear_base_de_datos.sql
├── requirements.txt
├── vercel.json
└── .gitignore
```

## Endpoints
| Método | Ruta | Acción |
|---|---|---|
| GET | `/api/{tabla}` | Listar registros |
| GET | `/api/{tabla}/{id}` | Consultar uno |
| POST | `/api/{tabla}` | Crear |
| PUT | `/api/{tabla}/{id}` | Actualizar |
| DELETE | `/api/{tabla}/{id}` | Eliminar |
| GET | `/api/adopcion/{id}/detalle` | Adopción con sus alimentos y cuidados |

Tablas: `persona`, `adoptante`, `cuidador`, `alimento`, `cuidado`, `dinosaurio`, `adopcion`, `adopcion_alimento`, `adopcion_cuidado`.

## Base de datos
Ver el diagrama en [`docs/diagrama_er.md`](docs/diagrama_er.md) (imagen: `docs/diagrama_er.png`).

| Tabla | Llave primaria | Llaves foráneas |
|---|---|---|
| persona | cedula | — |
| adoptante | cedula | cedula → persona |
| cuidador | cedula | cedula → persona |
| alimento | identificador | — |
| cuidado | identificador | — |
| dinosaurio | codigo | adoptante → adoptante |
| adopcion | identificador | dinosaurio_adoptado → dinosaurio, cuidador_asignado → cuidador |
| adopcion_alimento | (identificador_adopcion, identificador_alimento) | ambas columnas |
| adopcion_cuidado | (identificador_adopcion, identificador_cuidado) | ambas columnas |
