// Describe cada entidad: nombre visible, explicación y campos del formulario.
// Cada campo tiene: name (columna), label (nombre visible), hint (qué significa y cómo llenarlo),
// placeholder (ejemplo), type (text, email, tel, date, number) y, si apunta a otra tabla, ref.
// El PRIMER campo de cada entidad es su identificador (llave primaria).
const entities = {
  persona: {
    label: 'Personas',
    help: 'Datos básicos de cualquier persona del centro. Para que alguien pueda adoptar o cuidar, primero debe estar registrado aquí.',
    fields: [
      { name: 'cedula', label: 'Cédula', type: 'text', maxlength: 30, placeholder: 'Ej: 1-1234-5678', hint: 'Número de identificación de la persona. Es único: no pueden existir dos personas con la misma cédula y no se puede cambiar después de crearla.' },
      { name: 'nombre', label: 'Nombre', type: 'text', maxlength: 80, placeholder: 'Ej: Ana María', hint: 'Nombre (o nombres) de pila.' },
      { name: 'apellidos', label: 'Apellidos', type: 'text', maxlength: 100, placeholder: 'Ej: Abarca Monge', hint: 'Primer y segundo apellido.' },
      { name: 'correo', label: 'Correo electrónico', type: 'email', maxlength: 120, placeholder: 'nombre@correo.com', hint: 'Correo de contacto. Debe tener el formato nombre@dominio.com.' },
      { name: 'telefono', label: 'Teléfono', type: 'tel', maxlength: 30, placeholder: 'Ej: 6336-8011', hint: 'Número de contacto de la persona.' }
    ]
  },
  adoptante: {
    label: 'Adoptantes',
    help: 'Personas que adoptan dinosaurios. Elige a una persona ya registrada en «Personas» y define qué clase de adoptante es.',
    fields: [
      { name: 'cedula', label: 'Persona adoptante', ref: 'persona', hint: 'Persona que va a adoptar. Solo aparecen las registradas en «Personas». Una persona solo puede ser adoptante una vez.' },
      { name: 'tipo', label: 'Tipo de adoptante', type: 'text', maxlength: 40, placeholder: 'Ej: Particular', options: ['Particular', 'Familia', 'Empresa', 'Escuela', 'Zoológico'], hint: 'Clase de adoptante. Puedes elegir una sugerencia o escribir la tuya.' }
    ]
  },
  cuidador: {
    label: 'Cuidadores',
    help: 'Personal que atiende a los dinosaurios adoptados. Elige a una persona ya registrada en «Personas».',
    fields: [
      { name: 'cedula', label: 'Persona cuidadora', ref: 'persona', hint: 'Persona que trabajará como cuidador. Solo aparecen las registradas en «Personas». Una persona solo puede ser cuidador una vez.' },
      { name: 'especialidad', label: 'Especialidad', type: 'text', maxlength: 80, placeholder: 'Ej: Carnívoros', options: ['Carnívoros', 'Herbívoros', 'Veterinaria', 'Alimentación', 'Dinosaurios voladores'], hint: 'Área en la que se especializa el cuidador. Puedes elegir una sugerencia o escribir la tuya.' },
      { name: 'salario_x_hora', label: 'Salario por hora', type: 'number', placeholder: 'Ej: 3500', hint: 'Lo que se le paga al cuidador por cada hora trabajada. Solo número, sin símbolo de moneda; no puede ser negativo.' }
    ]
  },
  alimento: {
    label: 'Alimentos',
    help: 'Catálogo de comidas que se pueden dar a los dinosaurios.',
    fields: [
      { name: 'identificador', label: 'Identificador del alimento', type: 'text', maxlength: 30, placeholder: 'Ej: AL-001', hint: 'Código único para reconocer este alimento. No se puede repetir ni cambiar después de crearlo.' },
      { name: 'tipo', label: 'Tipo de alimento', type: 'text', maxlength: 60, placeholder: 'Ej: Carne', options: ['Carne', 'Pescado', 'Vegetal', 'Fruta', 'Suplemento'], hint: 'Categoría del alimento. Puedes elegir una sugerencia o escribir la tuya.' },
      { name: 'nombre', label: 'Nombre del alimento', type: 'text', maxlength: 80, placeholder: 'Ej: Carne de res', hint: 'Cómo se llama el alimento.' },
      { name: 'precio_x_unidad', label: 'Precio por unidad', type: 'number', placeholder: 'Ej: 2500', hint: 'Lo que cuesta una unidad del alimento (un kilo, una porción, un paquete…). Solo número; no puede ser negativo.' }
    ]
  },
  cuidado: {
    label: 'Cuidados',
    help: 'Catálogo de atenciones que se pueden dar a un dinosaurio (baño, revisión, paseo…).',
    fields: [
      { name: 'identificador', label: 'Identificador del cuidado', type: 'text', maxlength: 30, placeholder: 'Ej: CU-001', hint: 'Código único para reconocer este cuidado. No se puede repetir ni cambiar después de crearlo.' },
      { name: 'nombre', label: 'Nombre del cuidado', type: 'text', maxlength: 80, placeholder: 'Ej: Revisión veterinaria', hint: 'Actividad de cuidado que recibe el dinosaurio.' }
    ]
  },
  dinosaurio: {
    label: 'Dinosaurios',
    help: 'Los dinosaurios del centro. Cada uno pertenece a un adoptante ya registrado en «Adoptantes».',
    fields: [
      { name: 'codigo', label: 'Código del dinosaurio', type: 'text', maxlength: 30, placeholder: 'Ej: DINO-001', hint: 'Código único del dinosaurio. No se puede repetir ni cambiar después de crearlo.' },
      { name: 'color', label: 'Color', type: 'text', maxlength: 60, placeholder: 'Ej: Verde oscuro', hint: 'Color predominante de su piel o escamas.' },
      { name: 'especie', label: 'Especie', type: 'text', maxlength: 80, placeholder: 'Ej: Triceratops', hint: 'Especie a la que pertenece el dinosaurio.' },
      { name: 'dieta', label: 'Dieta', type: 'text', maxlength: 60, placeholder: 'Ej: Herbívoro', options: ['Herbívoro', 'Carnívoro', 'Omnívoro', 'Piscívoro'], hint: 'Qué come: herbívoro (plantas), carnívoro (carne) u omnívoro (ambos). Puedes elegir una sugerencia o escribir la tuya.' },
      { name: 'adoptante', label: 'Adoptante (dueño)', ref: 'adoptante', hint: 'Adoptante al que pertenece este dinosaurio. Solo aparecen los registrados en «Adoptantes».' }
    ]
  },
  adopcion: {
    label: 'Adopciones',
    help: 'Cada adopción de un dinosaurio: cuándo ocurrió, cuánto se cobra, cuántas horas de cuidado incluye y qué cuidador la atiende.',
    fields: [
      { name: 'identificador', label: 'Identificador de la adopción', type: 'text', maxlength: 30, placeholder: 'Ej: ADP-001', hint: 'Código único de esta adopción. No se puede repetir ni cambiar después de crearla.' },
      { name: 'fecha', label: 'Fecha de adopción', type: 'date', hint: 'Día en que se realizó la adopción.' },
      { name: 'monto_total', label: 'Monto total', type: 'number', placeholder: 'Ej: 150000', hint: 'Total que se cobra por la adopción. Solo número, sin símbolo de moneda; no puede ser negativo.' },
      { name: 'cantidad_horas_cuidado', label: 'Horas de cuidado', type: 'number', placeholder: 'Ej: 40', hint: 'Total de horas de cuidado incluidas en la adopción. Acepta decimales (ej: 2.5).' },
      { name: 'dinosaurio_adoptado', label: 'Dinosaurio adoptado', ref: 'dinosaurio', hint: 'Dinosaurio que se adopta. Solo aparecen los registrados en «Dinosaurios».' },
      { name: 'cuidador_asignado', label: 'Cuidador asignado', ref: 'cuidador', hint: 'Cuidador responsable de esta adopción. Solo aparecen los registrados en «Cuidadores».' }
    ]
  },
  adopcion_alimento: {
    label: 'Adopción-alimento',
    link: true,
    help: 'Indica qué alimentos recibe el dinosaurio de cada adopción. Cada fila une UNA adopción con UN alimento; para varios alimentos, crea varias filas.',
    fields: [
      { name: 'identificador_adopcion', label: 'Adopción', ref: 'adopcion', hint: 'Adopción a la que se le asigna el alimento. Solo aparecen las registradas en «Adopciones».' },
      { name: 'identificador_alimento', label: 'Alimento', ref: 'alimento', hint: 'Alimento que recibirá. Solo aparecen los registrados en «Alimentos». No se puede repetir el mismo alimento en la misma adopción.' }
    ]
  },
  adopcion_cuidado: {
    label: 'Adopción-cuidado',
    link: true,
    help: 'Indica qué cuidados recibe el dinosaurio de cada adopción. Cada fila une UNA adopción con UN cuidado; para varios cuidados, crea varias filas.',
    fields: [
      { name: 'identificador_adopcion', label: 'Adopción', ref: 'adopcion', hint: 'Adopción a la que se le asigna el cuidado. Solo aparecen las registradas en «Adopciones».' },
      { name: 'identificador_cuidado', label: 'Cuidado', ref: 'cuidado', hint: 'Cuidado que recibirá. Solo aparecen los registrados en «Cuidados». No se puede repetir el mismo cuidado en la misma adopción.' }
    ]
  }
};

// Cómo se muestra una fila de cada tabla dentro de las listas desplegables y de la tabla.
const personName = cedula => {
  const p = (lookups.persona || []).find(r => r.cedula === cedula);
  return p ? `${cedula} — ${p.nombre} ${p.apellidos}` : cedula;
};
const optionLabel = {
  persona: r => `${r.cedula} — ${r.nombre} ${r.apellidos}`,
  adoptante: r => `${personName(r.cedula)} (${r.tipo})`,
  cuidador: r => `${personName(r.cedula)} (${r.especialidad})`,
  alimento: r => `${r.identificador} — ${r.nombre}`,
  cuidado: r => `${r.identificador} — ${r.nombre}`,
  dinosaurio: r => `${r.codigo} — ${r.especie} (${r.color})`,
  adopcion: r => `${r.identificador} — ${r.fecha}`
};

// Estado: pestaña activa, fila en edición, filas mostradas, datos de las listas desplegables y bandera de guardado.
let current = 'persona';
let editing = null;
let rows = [];
let lookups = {};
let saving = false;

// Atajos y utilidades.
const $ = id => document.getElementById(id);
// Primera columna de una entidad (su clave). En las tablas de relación hay dos: fields[0] y fields[1].
const pk = entity => entities[entity].fields[0].name;
// Escapa texto para insertarlo de forma segura en HTML (evita que un nombre con " o < rompa la página).
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

// Muestra un mensaje: verde si salió bien, rojo si hubo un error.
function show(text, ok = false) {
  $('message').textContent = text;
  $('message').className = ok ? 'ok' : 'error';
}

// Convierte cualquier respuesta de error (JSON, texto o servidor caído) en un mensaje legible.
async function readError(response) {
  try {
    const body = await response.json();
    if (Array.isArray(body.detail)) return body.detail.map(d => d.msg).join(' · ');
    return body.detail || 'Ocurrió un error inesperado.';
  } catch {
    return `El servidor respondió con un error (${response.status}). Intenta de nuevo.`;
  }
}

// Dibuja un botón por cada entidad.
function nav() {
  $('tabs').innerHTML = Object.entries(entities).map(([key, value]) =>
    `<button class="${key === current ? 'active' : ''}" onclick="choose('${key}')">${value.label}</button>`
  ).join('');
}

// Descarga las tablas que alimentan las listas desplegables de la entidad activa.
async function loadLookups() {
  const needed = new Set();
  for (const field of entities[current].fields) {
    if (!field.ref) continue;
    needed.add(field.ref);
    if (field.ref === 'adoptante' || field.ref === 'cuidador') needed.add('persona');
  }
  await Promise.all([...needed].map(async name => {
    const response = await fetch('/api/' + name);
    if (!response.ok) throw new Error(await readError(response));
    lookups[name] = await response.json();
  }));
}

// Cambia de entidad, descarta una edición pendiente y actualiza la pantalla.
async function choose(entity) {
  current = entity;
  editing = null;
  nav();
  $('message').textContent = '';
  try {
    await loadLookups();
    render();
    await load();
  } catch (error) {
    render();
    show(error.message || 'No se pudo conectar con el servidor.');
  }
}

// Construye el HTML de un campo: etiqueta, control (input o lista desplegable) y su explicación.
function fieldHtml(field) {
  const locked = editing && field.name === pk(current);
  let control;
  if (field.ref) {
    const options = lookups[field.ref] || [];
    const empty = options.length ? '— Selecciona una opción —' : `— No hay registros: crea uno primero en «${entities[field.ref].label}» —`;
    control = `<select name="${field.name}" required ${locked ? 'disabled' : ''}><option value="">${esc(empty)}</option>` +
      options.map(r => `<option value="${esc(r[pk(field.ref)])}">${esc(optionLabel[field.ref](r))}</option>`).join('') + '</select>';
  } else {
    const number = field.type === 'number';
    control = `<input name="${field.name}" type="${field.type || 'text'}" ${field.maxlength ? `maxlength="${field.maxlength}"` : ''} ` +
      `${number ? 'step="any" min="0" inputmode="decimal"' : ''} ${field.placeholder ? `placeholder="${esc(field.placeholder)}"` : ''} ` +
      `${field.options ? `list="list_${field.name}"` : ''} ${locked ? 'readonly' : ''} autocomplete="off" required>` +
      (field.options ? `<datalist id="list_${field.name}">${field.options.map(o => `<option value="${esc(o)}">`).join('')}</datalist>` : '');
  }
  return `<label><span>${esc(field.label)} <b class="req" title="Obligatorio">*</b></span>${control}<small class="hint">${esc(field.hint)}</small></label>`;
}

// Construye el formulario y los encabezados de tabla para la entidad activa.
function render() {
  const entity = entities[current];
  $('title').textContent = entity.label;
  $('help').textContent = entity.help;
  $('form').innerHTML = entity.fields.map(fieldHtml).join('') +
    `<div class="form-actions"><button class="primary">${editing ? 'Actualizar' : 'Crear'}</button>` +
    (editing ? '<button type="button" onclick="cancelEdit()">Cancelar edición</button>' : '') +
    '<span class="req-note"><b class="req">*</b> Todos los campos son obligatorios.</span></div>';
  $('form').onsubmit = save;
  $('head').innerHTML = '<tr>' + entity.fields.map(field => `<th>${esc(field.label)}</th>`).join('') + '<th>Acciones</th></tr>';
}

// Valor legible de una celda: en las referencias muestra el nombre además del código.
function cellText(field, row) {
  const value = row[field.name];
  if (field.ref && optionLabel[field.ref]) {
    const target = (lookups[field.ref] || []).find(r => r[pk(field.ref)] === value);
    return target ? optionLabel[field.ref](target) : value;
  }
  return value;
}

// Pide los registros al endpoint GET y dibuja una fila por cada respuesta.
async function load() {
  const response = await fetch('/api/' + current);
  if (!response.ok) throw new Error(await readError(response));
  rows = await response.json();
  const fields = entities[current].fields;
  $('body').innerHTML = rows.length ? rows.map((row, i) => '<tr>' +
    fields.map(field => `<td>${esc(cellText(field, row))}</td>`).join('') +
    `<td class="actions">${entities[current].link ? '' : `<button onclick="edit(${i})">Editar</button>`}<button class="danger" onclick="removeRow(${i})">Borrar</button></td></tr>`
  ).join('') : `<tr><td colspan="${fields.length + 1}" class="empty">Aún no hay registros.</td></tr>`;
}

// Envía el formulario como JSON mediante POST para crear o PUT para actualizar.
async function save(event) {
  event.preventDefault();
  if (saving) return; // Evita guardar dos veces si se hace doble clic (la segunda daría "ya existe").
  const fields = entities[current].fields;
  const data = Object.fromEntries(new FormData(event.target));
  for (const field of fields) {
    if (typeof data[field.name] === 'string') data[field.name] = data[field.name].trim();
    if (field.type === 'number') data[field.name] = Number(data[field.name]);
  }
  // Los campos bloqueados no se envían en el formulario: la clave se toma de la fila que se edita.
  if (editing) data[pk(current)] = editing[pk(current)];
  const url = '/api/' + current + (editing ? '/' + encodeURIComponent(data[pk(current)]) : '');
  const button = event.target.querySelector('.primary');
  saving = true;
  button.disabled = true;
  try {
    const response = await fetch(url, {
      method: editing ? 'PUT' : 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!response.ok) {
      show(await readError(response)); // El formulario conserva lo escrito para poder corregirlo.
      return;
    }
    show('Guardado correctamente.', true);
    editing = null;
    render();
    await load();
  } catch {
    show('No se pudo conectar con el servidor. Revisa tu conexión e intenta de nuevo.');
  } finally {
    saving = false;
    if (button.isConnected) button.disabled = false;
  }
}

// Carga los valores de una fila en el formulario para permitir la actualización.
function edit(index) {
  editing = rows[index];
  render();
  for (const [key, value] of Object.entries(editing)) $('form').elements[key].value = value;
  show('Editando un registro. Cambia lo que necesites y pulsa «Actualizar».', true);
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Cancela la edición y deja el formulario vacío.
function cancelEdit() {
  editing = null;
  render();
  $('message').textContent = '';
}

// Solicita confirmación y, si el usuario acepta, llama al endpoint DELETE.
async function removeRow(index) {
  const row = rows[index];
  if (!confirm('¿Eliminar este registro?')) return;
  const fields = entities[current].fields;
  // Las tablas de relación se identifican con dos claves; las demás con una.
  const keys = entities[current].link ? [row[fields[0].name], row[fields[1].name]] : [row[pk(current)]];
  try {
    const response = await fetch('/api/' + current + '/' + keys.map(encodeURIComponent).join('/'), { method: 'DELETE' });
    response.ok ? show('Registro eliminado.', true) : show(await readError(response));
    await load();
  } catch {
    show('No se pudo conectar con el servidor. Revisa tu conexión e intenta de nuevo.');
  }
  // Sube a la parte superior para que el usuario vea el mensaje.
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Inicializa la interfaz al terminar de cargar el archivo JavaScript.
choose('persona');
