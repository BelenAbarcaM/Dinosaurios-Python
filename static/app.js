// Describe cada entidad, el texto visible y los campos que aparecerán en su formulario.
const entities = {
  persona: { label: 'Personas', fields: ['cedula', 'nombre', 'apellidos', 'correo', 'telefono'] },
  adoptante: { label: 'Adoptantes', fields: ['cedula', 'tipo'] },
  cuidador: { label: 'Cuidadores', fields: ['cedula', 'especialidad', 'salario_x_hora'] },
  alimento: { label: 'Alimentos', fields: ['identificador', 'tipo', 'nombre', 'precio_x_unidad'] },
  cuidado: { label: 'Cuidados', fields: ['identificador', 'nombre'] },
  dinosaurio: { label: 'Dinosaurios', fields: ['codigo', 'color', 'especie', 'dieta', 'adoptante'] },
  adopcion: { label: 'Adopciones', fields: ['identificador', 'fecha', 'monto_total', 'cantidad_horas_cuidado', 'dinosaurio_adoptado', 'cuidador_asignado'] },
  adopcion_alimento: { label: 'Adopción-alimento', fields: ['identificador_adopcion', 'identificador_alimento'] },
  adopcion_cuidado: { label: 'Adopción-cuidado', fields: ['identificador_adopcion', 'identificador_cuidado'] }
};

// Guarda la pestaña seleccionada y, si corresponde, la fila que se está editando.
let current = 'persona';
let editing = null;

// Devuelve la primera columna de una entidad, que el proyecto usa como clave.
const pk = entity => entities[entity].fields[0];
// Reduce document.getElementById a una función corta y legible.
const $ = id => document.getElementById(id);
// Convierte salario_x_hora en salario x hora para mostrarlo al usuario.
function label(text) { return text.replaceAll('_', ' '); }

// Dibuja un botón por cada entidad del objeto entities.
function nav() {
  $('tabs').innerHTML = Object.entries(entities).map(([key, value]) =>
    `<button class="${key === current ? 'active' : ''}" onclick="choose('${key}')">${value.label}</button>`
  ).join('');
}

// Cambia de entidad, descarta una edición pendiente y actualiza la pantalla.
function choose(entity) {
  current = entity;
  editing = null;
  nav();
  render();
  load();
}

// Construye el formulario y los encabezados de tabla para la entidad activa.
function render() {
  const entity = entities[current];
  $('title').textContent = entity.label;
  $('form').innerHTML = entity.fields.map(field =>
    `<label>${label(field)}<input name="${field}" ${field === pk(current) && editing ? 'readonly' : ''} ${field === 'fecha' ? 'type="date"' : ''} ${/precio|salario|monto|cantidad/.test(field) ? 'type="number" step="0.01"' : ''} required></label>`
  ).join('') + `<button class="primary">${editing ? 'Actualizar' : 'Crear'}</button>`;
  $('form').onsubmit = save;
  $('head').innerHTML = '<tr>' + entity.fields.map(field => `<th>${label(field)}</th>`).join('') + '<th>Acciones</th></tr>';
}

// Pide los registros al endpoint GET y dibuja una fila por cada respuesta.
async function load() {
  const response = await fetch('/api/' + current);
  const rows = await response.json();
  $('body').innerHTML = rows.map(row => '<tr>' +
    entities[current].fields.map(field => `<td>${row[field]}</td>`).join('') +
    `<td class="actions"><button onclick='edit(${JSON.stringify(row)})'>Editar</button><button class="danger" onclick="removeRow('${row[pk(current)]}')">Borrar</button></td></tr>`
  ).join('');
}

// Envía el formulario como JSON mediante POST para crear o PUT para actualizar.
async function save(event) {
  event.preventDefault();
  const data = Object.fromEntries(new FormData(event.target));
  for (const field of entities[current].fields) {
    if (/precio|salario|monto|cantidad/.test(field)) data[field] = Number(data[field]);
  }
  const url = '/api/' + current + (editing ? '/' + data[pk(current)] : '');
  const response = await fetch(url, {
    method: editing ? 'PUT' : 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!response.ok) {
    $('message').textContent = (await response.json()).detail;
    return;
  }
  $('message').textContent = 'Guardado correctamente.';
  editing = null;
  render();
  load();
}

// Carga los valores de una fila en el formulario para permitir la actualización.
function edit(row) {
  editing = row;
  render();
  for (const [key, value] of Object.entries(row)) $('form').elements[key].value = value;
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Solicita confirmación y, si el usuario acepta, llama al endpoint DELETE.
async function removeRow(key) {
  if (!confirm('¿Eliminar este registro?')) return;
  const response = await fetch('/api/' + current + '/' + key, { method: 'DELETE' });
  $('message').textContent = response.ok ? 'Registro eliminado.' : (await response.json()).detail;
  // Sube a la parte superior para que el usuario vea el mensaje.
  window.scrollTo({ top: 0, behavior: 'smooth' });
  load();
}

// Inicializa la interfaz al terminar de cargar el archivo JavaScript.
nav();
render();
load();
