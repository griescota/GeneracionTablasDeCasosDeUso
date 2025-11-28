document.addEventListener("DOMContentLoaded", async () => {
  console.log("proyecto_detalle.js cargado v3");
  const baseUrl   = "http://127.0.0.1:8000";
  const token     = localStorage.getItem("token");
  const params    = new URLSearchParams(location.search);
  let projectId = params.get("project_id"); 

  if (!token) {
    
    console.warn("No hay token, continuando para desarrollo sin autenticación.");
  }
  if (!projectId) {
   
    console.warn("No se encontró project_id en la URL, usando 'dummyProject123' para desarrollo.");
    projectId = "dummyProject123"; 
  }

 
  const genericModal = document.getElementById("genericModal");
  const modalTitle = document.getElementById("modalTitle");
  const modalForm = document.getElementById("modalForm");
  const modalSaveButton = document.getElementById("modal-save");
  const modalCancelButton = document.getElementById("modal-cancel");

  let currentEditData = { section: null, itemId: null, sectionCardContainerElement: null };


  const EnumValues = {
    TipoRequisitoEnum: ["FUNCIONAL", "NO_FUNCIONAL"],
    CategoriaCasoUsoEnum: ["Principal", "Secundario", "Excepcional"], 
    TipoEscenarioEnum: ["NORMAL", "ALTERNATIVO", "EXCEPCION"],
    EstadoRequisitoEnum: ["Propuesto", "Aprobado", "Implementado", "Verificado", "Rechazado"],
    EstadoCasoUsoEnum: ["Propuesto", "En Desarrollo", "Implementado", "Validado"]
  };

  const authFetch = async (url, opts = {}) => {
    const headers = {
     
      ...opts.headers,
    };
    if (token) { 
        headers["Authorization"] = `Bearer ${token}`;
    }

    if (opts.body && !(opts.body instanceof FormData)) {
        headers["Content-Type"] = "application/json";
    }

    try {
      const response = await fetch(url, { ...opts, headers });
      if (!response.ok) {
        let errorData;
        try {
            errorData = await response.json();
        } catch (e) {
            errorData = { message: response.statusText };
        }
        console.error("API Error:", response.status, errorData);
        alert(`Error ${response.status}: ${errorData.detail || errorData.message || 'Ocurrió un error desconocido.'}`);
        if (response.status === 401 && token) { 
            localStorage.clear();
            window.location.href = "index.html";
        }
        return null;
      }
      if (response.status === 204) return true; 
      return response.json();
    } catch (error) {
      console.error("Fetch Error:", error);
      alert("Error de conexión. Por favor, intente de nuevo.");
      return null;
    }
  };

  // 1) Cargar datos del proyecto
  let proj = { nombre: "Cargando Proyecto...", estado: "Desconocido" }; 
  if (projectId !== "dummyProject123") { 
      proj = await authFetch(`${baseUrl}/projects/${projectId}`) || proj;
  } else {
      proj = { id: "dummyProject123", nombre: "Proyecto de Demostración", estado: "Activo", descripcion: "Un proyecto para pruebas."};
      console.log("Usando datos dummy para el proyecto.");
  }


  document.getElementById("project-name").textContent = proj.nombre;
  const statusEl = document.getElementById("project-status");
  statusEl.className = `status-badge status-${proj.estado.toLowerCase().replace(/\s+/g, '-')}`;
  statusEl.textContent = proj.estado;

  // 2) Secciones actualizadas con todos los campos de los modelos
  const sections = [
    { 
      key: 'requisitos',  
      title: 'Requisitos',    
      endpoint: `/projects/${projectId}/requisitos`, 
      fields: ['nombre', 'descripcion', 'tipo', 'estado', 'prioridad', 'fuente', 'observaciones', 'version', 'requisito_padre_id', 'fecha_creacion', 'fecha_actualizacion'], 
      displayFields: ['nombre', 'descripcion', 'tipo', 'estado'], 
      idField: 'id', 
      items: [] 
    },
    { 
      key: 'casos_uso',   
      title: 'Casos de Uso',  
      endpoint: `/projects/${projectId}/casos_uso`,    
      fields: ['titulo', 'descripcion', 'actores', 'categoria', 'estado', 'precondiciones', 'postcondiciones', 'flujo_normal', 'flujo_alternativo', 'requisito_id', 'fecha_creacion', 'fecha_actualizacion'], 
      displayFields: ['titulo', 'descripcion', 'actores', 'categoria', 'estado'],
      idField: 'id', 
      items: [] 
    },
    { 
      key: 'escenarios',  
      title: 'Escenarios',     
      endpoint: `/escenarios`, 
      fields: ['nombre', 'descripcion', 'tipo', 'resultado_esperado', 'caso_uso_id', 'fecha_creacion', 'fecha_actualizacion'], 
      displayFields: ['nombre', 'descripcion', 'tipo', 'resultado_esperado', 'caso_uso_id'],
      idField: 'id', 
      parentField: 'caso_uso_id', 
      items: [] 
    },
    { 
      key: 'actores',     
      title: 'Actores',        
      endpoint: `/actores`,    
      fields: ['nombre', 'tipo', 'descripcion'],        
      displayFields: ['nombre', 'tipo', 'descripcion'],
      idField: 'id', 
      items: [] 
    },
  ];

  // Tipos de campo para el formulario modal
  const fieldTypes = {
      'descripcion': 'textarea',
      'observaciones': 'textarea',
      'precondiciones': 'textarea',
      'postcondiciones': 'textarea',
      'flujo_normal': 'textarea',
      'flujo_alternativo': 'textarea',
      'resultado_esperado': 'textarea',
      'tipo': { 
          'requisitos': EnumValues.TipoRequisitoEnum,
          'escenarios': EnumValues.TipoEscenarioEnum,
          'actores': ['Humano', 'Sistema Externo', 'Dispositivo'] 
      },
      'estado': { 
          'requisitos': EnumValues.EstadoRequisitoEnum,
          'casos_uso': EnumValues.EstadoCasoUsoEnum
      },
      'categoria': EnumValues.CategoriaCasoUsoEnum, // Para casos_uso
      'prioridad': 'number',
      'version': 'number',
      // Campos de fecha (usualmente no editables directamente o con datepicker)
      'fecha_creacion': 'datetime-local', // O 'text' si es solo display
      'fecha_actualizacion': 'datetime-local', // O 'text' si es solo display
      // Campos de relación (se manejarán como select)
      'requisito_padre_id': 'select-requisito',
      'requisito_id': 'select-requisito', // Para CasosDeUso
      'caso_uso_id': 'select-caso_uso'    // Para Escenarios
  };
  
  // Helper para formatear fechas
  function formatDisplayDate(dateString) {
    if (!dateString) return 'N/A';
    try {
        const date = new Date(dateString);
        return date.toLocaleString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
    } catch (e) {
        return dateString; // Devuelve el string original si hay error
    }
  }


  // 3) Renderizar secciones
  const container = document.getElementById("container");
  const tpl = document.getElementById("section-template");

  // Primero cargar requisitos y casos de uso para que estén disponibles para los selects
  const requisitosSectionDef = sections.find(s => s.key === 'requisitos');
  const casosUsoSectionDef = sections.find(s => s.key === 'casos_uso');

  if (requisitosSectionDef) {
    const el = document.createElement('div'); // Contenedor temporal para la carga
    await loadItems(requisitosSectionDef, el, true); // Cargar silenciosamente
  }
  if (casosUsoSectionDef) {
    const el = document.createElement('div'); 
    await loadItems(casosUsoSectionDef, el, true); // Cargar silenciosamente
  }


  for (const sec of sections) {
    const clone = tpl.content.cloneNode(true);
    clone.querySelector("h2").textContent = sec.title;
    const sectionEl = clone.querySelector(".dynamic-section");
    sectionEl.dataset.sectionKey = sec.key;

    const cardContainer = sectionEl.querySelector(".card-container");
    clone.querySelector(".add-btn").addEventListener("click", () => handleShowModal(sec, null, cardContainer));
    
    container.appendChild(clone);
    // Si ya se cargaron silenciosamente, solo renderizar. Sino, cargar y renderizar.
    if (sec.items && sec.items.length > 0 && (sec.key === 'requisitos' || sec.key === 'casos_uso')) {
        renderItems(sec, cardContainer);
    } else {
        await loadItems(sec, cardContainer);
    }
  }


  // 4) Cargar y mostrar datos
  async function loadItems(sec, el, silent = false) {
    if (!silent) el.innerHTML = '<p>Cargando...</p>';
    
    let dataUrl = baseUrl + sec.endpoint;
    // Para desarrollo con dummy projectId, simular datos
    if (projectId === "dummyProject123" && sec.endpoint.includes("dummyProject123")) {
        console.log(`Simulando datos para ${sec.key}`);
        sec.items = getDummyData(sec.key);
        if (!silent) renderItems(sec, el);
        return;
    } else if (projectId === "dummyProject123" && (sec.key === 'actores' || sec.key === 'escenarios')) {
        // Endpoints globales para dummy
        sec.items = getDummyData(sec.key);
        if (!silent) renderItems(sec, el);
        return;
    }


    let data = await authFetch(dataUrl);

    if (!data || !Array.isArray(data)) {
        if (!silent) el.innerHTML = `<p>No se pudieron cargar los datos para ${sec.title} o no hay elementos.</p>`;
        sec.items = [];
        return;
    }
    
    if (sec.key === 'escenarios' && casosUsoSectionDef) {
      const idsCasosUsoProyecto = casosUsoSectionDef.items.map(c => c[casosUsoSectionDef.idField]);
      data = data.filter(e => idsCasosUsoProyecto.includes(e.caso_uso_id));
    }

    sec.items = data;
    if (!silent) renderItems(sec, el);
  }

  function getDummyData(sectionKey) {
    const now = new Date().toISOString();
    switch(sectionKey) {
        case 'requisitos':
            return [
                { id: 1, nombre: 'Req Demo 1', descripcion: 'Descripción del Req 1', tipo: 'FUNCIONAL', estado: 'Propuesto', prioridad: 1, fuente: 'Cliente', observaciones: '', version: 1, requisito_padre_id: null, fecha_creacion: now, fecha_actualizacion: now, proyecto_id: 'dummyProject123' },
                { id: 2, nombre: 'Req Demo 2', descripcion: 'Descripción del Req 2', tipo: 'NO_FUNCIONAL', estado: 'Aprobado', prioridad: 2, fuente: 'Analista', observaciones: 'Ninguna', version: 1, requisito_padre_id: 1, fecha_creacion: now, fecha_actualizacion: now, proyecto_id: 'dummyProject123' },
            ];
        case 'casos_uso':
            return [
                { id: 1, titulo: 'CU Demo 1', descripcion: 'Descripción CU 1', actores: 'Usuario, Admin', categoria: 'Principal', estado: 'Propuesto', precondiciones: 'Sistema activo', postcondiciones: 'Tarea completada', flujo_normal: 'Pasos...', flujo_alternativo: '', requisito_id: 1, fecha_creacion: now, fecha_actualizacion: now, proyecto_id: 'dummyProject123' },
            ];
        case 'escenarios': // Global dummy data
            return [
                { id: 1, nombre: 'Escenario Demo 1', descripcion: 'Descripción Escenario 1', tipo: 'NORMAL', resultado_esperado: 'Éxito', caso_uso_id: 1, fecha_creacion: now, fecha_actualizacion: now },
            ];
        case 'actores': // Global dummy data
            return [
                { id: 1, nombre: 'Actor Demo 1', tipo: 'Humano', descripcion: 'Usuario principal' },
            ];
        default: return [];
    }
  }

  function renderItems(sec, el) {
    el.innerHTML = ''; 
    if (!sec.items || sec.items.length === 0) {
        el.innerHTML = `<p>No hay elementos en ${sec.title}.</p>`;
        return;
    }

    sec.items.forEach(item => {
      const card = document.createElement("div");
      card.className = "card";
      card.dataset.itemId = item[sec.idField];

      let contentHtml = `<h3>${item[sec.fields[0]] || 'Sin Título'}</h3>`;
      // Usar displayFields para las tarjetas
      const fieldsToDisplayOnCard = sec.displayFields || sec.fields;

      fieldsToDisplayOnCard.slice(1).forEach(fKey => {
        if (sec.key === 'escenarios' && fKey === 'caso_uso_id') { // Mostrar nombre del CU en vez de ID
            const casoUso = casosUsoSectionDef.items.find(cu => cu.id === item.caso_uso_id);
            contentHtml += `<p><strong>Caso de Uso:</strong> ${casoUso ? casoUso.titulo : 'N/A (ID: ' + item.caso_uso_id + ')'}</p>`;
            return;
        }
        if (fKey === 'requisito_id' && sec.key === 'casos_uso') { // Mostrar nombre del Requisito
            const requisito = requisitosSectionDef.items.find(r => r.id === item.requisito_id);
            contentHtml += `<p><strong>Requisito Asociado:</strong> ${requisito ? requisito.nombre : 'N/A (ID: ' + item.requisito_id + ')'}</p>`;
            return;
        }
        if (fKey === 'requisito_padre_id' && sec.key === 'requisitos') {
            const padre = requisitosSectionDef.items.find(r => r.id === item.requisito_padre_id);
            contentHtml += `<p><strong>Padre:</strong> ${padre ? padre.nombre : 'Ninguno'}</p>`;
            return;
        }

        const label = fKey.replace(/_/g,' ').replace(/^\w/,c=>c.toUpperCase());
        let value = item[fKey] ?? 'N/A';
        if (fKey.startsWith('fecha_')) {
            value = formatDisplayDate(value);
        }
        contentHtml += `<p><strong>${label}:</strong> ${value}</p>`;
      });

      contentHtml += `
        <div class="actions">
          <button class="edit" title="Editar"><i class="fas fa-edit"></i></button>
          <button class="delete" title="Eliminar"><i class="fas fa-trash-alt"></i></button>
        </div>
      `;
      card.innerHTML = contentHtml;

      card.querySelector(".edit").addEventListener("click", (e) => {
        e.stopPropagation();
        handleShowModal(sec, item, el);
      });
      card.querySelector(".delete").addEventListener("click", (e) => {
        e.stopPropagation();
        handleDeleteItem(sec, item[sec.idField], el);
      });
      el.appendChild(card);
    });
  }

  // --- MODAL & CRUD FUNCTIONS ---
  function getEndpointForItem(section, itemId = null) {
    let endpoint = baseUrl;
     // Para desarrollo con dummy projectId
    if (projectId === "dummyProject123") {
        if (section.endpoint.includes("dummyProject123")) { // Endpoints específicos del proyecto dummy
             endpoint += `/projects/${projectId}/${section.key}`;
        } else { // Endpoints globales para dummy (actores, escenarios)
            endpoint += `/${section.key}`;
        }
    } else { // Lógica de producción
        endpoint += section.endpoint; // Ya tiene /projects/{projectId}/... o /global_path
    }

    if (itemId) endpoint += `/${itemId}`;
    return endpoint;
  }
  
  async function handleShowModal(section, item, sectionCardContainerElement) {
    currentEditData = { section, itemId: item ? item[section.idField] : null, sectionCardContainerElement };
    modalTitle.textContent = item ? `Editar ${section.title.slice(0,-1)}` : `Nuevo ${section.title.slice(0,-1)}`;
    modalForm.innerHTML = ''; 

    section.fields.forEach(fieldKey => {
      // Omitir campos gestionados por el backend en el formulario (ej: fechas de auditoría, a menos que se quieran mostrar como readonly)
      if (['fecha_creacion', 'fecha_actualizacion'].includes(fieldKey) && !item) return; // No mostrar en creación
      if (fieldKey === 'version' && !item) return; // No mostrar 'version' en creación, usualmente es 1 por defecto en backend
      if (fieldKey === 'proyecto_id') return; // Ya está en el endpoint

      const div = document.createElement('div');
      const label = document.createElement('label');
      label.setAttribute('for', `modal-${fieldKey}`);
      label.textContent = `${fieldKey.replace(/_/g,' ').replace(/^\w/,c=>c.toUpperCase())}:`;
      
      let inputElement;
      const fieldTypeLookupKey = fieldTypes[fieldKey];
      const specificTypeForSection = typeof fieldTypeLookupKey === 'object' && fieldTypeLookupKey !== null ? fieldTypeLookupKey[section.key] : fieldTypeLookupKey;
      
      const createSelect = (optionsArray, currentValue, placeholder = "Seleccione...") => {
          const select = document.createElement('select');
          if (placeholder) {
            const phOption = document.createElement('option');
            phOption.value = ""; 
            phOption.textContent = placeholder;
            phOption.disabled = true;
            if (!currentValue) phOption.selected = true;
            select.appendChild(phOption);
          }
          optionsArray.forEach(opt => {
              const option = document.createElement('option');
              if (typeof opt === 'object') { // Para {value, text}
                  option.value = opt.value;
                  option.textContent = opt.text;
                  if (currentValue == opt.value) option.selected = true; // Usar == para comparar string con number
              } else { // Para array de strings
                  option.value = opt;
                  option.textContent = opt;
                  if (currentValue === opt) option.selected = true;
              }
              select.appendChild(option);
          });
          return select;
      };

      if (specificTypeForSection && Array.isArray(specificTypeForSection)) { // Select para Enums
          inputElement = createSelect(specificTypeForSection, item ? item[fieldKey] : specificTypeForSection[0]);
      } else if (fieldTypeLookupKey === 'select-requisito') {
          const reqOptions = requisitosSectionDef.items.map(r => ({ value: r.id, text: r.nombre }));
          inputElement = createSelect(reqOptions, item ? item[fieldKey] : '', "Seleccione un requisito");
          if (fieldKey === 'requisito_padre_id' && item) { // Evitar que un requisito sea su propio padre
            inputElement.querySelectorAll('option').forEach(opt => {
                if (opt.value == item.id) opt.disabled = true;
            });
          }
      } else if (fieldTypeLookupKey === 'select-caso_uso') {
          const cuOptions = casosUsoSectionDef.items.map(cu => ({ value: cu.id, text: cu.titulo }));
          inputElement = createSelect(cuOptions, item ? item[fieldKey] : '', "Seleccione un caso de uso");
      } else if (specificTypeForSection === 'textarea' || fieldTypeLookupKey === 'textarea') {
        inputElement = document.createElement('textarea');
        if (item) inputElement.value = item[fieldKey] || '';
      } else {
        inputElement = document.createElement('input');
        inputElement.type = specificTypeForSection || fieldTypeLookupKey || 'text';
        if (item) {
            if (inputElement.type === 'datetime-local' && item[fieldKey]) {
                 // Formatear para datetime-local: YYYY-MM-DDTHH:mm
                const d = new Date(item[fieldKey]);
                if (!isNaN(d)) {
                    const year = d.getFullYear();
                    const month = (d.getMonth() + 1).toString().padStart(2, '0');
                    const day = d.getDate().toString().padStart(2, '0');
                    const hours = d.getHours().toString().padStart(2, '0');
                    const minutes = d.getMinutes().toString().padStart(2, '0');
                    inputElement.value = `${year}-${month}-${day}T${hours}:${minutes}`;
                } else {
                    inputElement.value = '';
                }
            } else {
                 inputElement.value = item[fieldKey] || '';
            }
        }
        if (['fecha_creacion', 'fecha_actualizacion'].includes(fieldKey) && item) {
            inputElement.readOnly = true; // Fechas de auditoría no editables
        }
      }
      inputElement.id = `modal-${fieldKey}`;
      inputElement.name = fieldKey;

      
      if (!['fecha_creacion', 'fecha_actualizacion', 'version'].includes(fieldKey) || 
          (fieldKey === 'version' && item)) { 
        if (fieldKey !== 'requisito_padre_id' && fieldKey !== 'observaciones' && fieldKey !== 'fuente' &&
            fieldKey !== 'precondiciones' && fieldKey !== 'postcondiciones' && fieldKey !== 'flujo_alternativo') { // Campos opcionales
           
        }
      }
      // Campos obligatorios básicos
      if (['nombre', 'titulo', 'tipo', 'categoria', 'estado', 'descripcion'].includes(fieldKey) && fieldKey !== 'descripcion' && section.key === 'actores') {
          inputElement.required = true;
      }
      if(fieldKey === 'descripcion' && section.key !== 'actores') inputElement.required = true;


      div.appendChild(label);
      div.appendChild(inputElement);
      modalForm.appendChild(div);
    });

    genericModal.classList.add("visible");
  }

  modalForm.addEventListener("submit", async (event) => { // Escuchar el submit del form
    event.preventDefault(); // Prevenir el envío tradicional
    if (!modalForm.checkValidity()) {
      modalForm.reportValidity();
      return;
    }

    const { section, itemId, sectionCardContainerElement } = currentEditData;
    const formData = new FormData(modalForm);
    const data = {};
    formData.forEach((value, key) => {
        // Convertir a número si es un campo numérico o ID de relación
        if (fieldTypes[key] === 'number' || key.endsWith('_id')) {
            data[key] = value === '' ? null : Number(value); // Enviar null si está vacío, sino número
        } else {
            data[key] = value;
        }
    });
    
    // Asegurar que los IDs de relación vacíos se envíen como null
    ['requisito_padre_id', 'requisito_id', 'caso_uso_id'].forEach(relKey => {
        if (data.hasOwnProperty(relKey) && data[relKey] === "") {
            data[relKey] = null;
        }
    });


    let result;
    const endpoint = getEndpointForItem(section, itemId);

    if (itemId) { // Update (PUT)
      result = await authFetch(endpoint, {
        method: 'PUT',
        body: JSON.stringify(data)
      });
    } else { // Create (POST)
      // Para desarrollo con dummy, simular la creación
      if (projectId === "dummyProject123") {
          const newItem = { ...data, id: Date.now(), fecha_creacion: new Date().toISOString(), fecha_actualizacion: new Date().toISOString()};
          if (section.key === 'requisitos' || section.key === 'casos_uso') newItem.proyecto_id = projectId;
          section.items.push(newItem);
          result = newItem;
      } else {
          result = await authFetch(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
          });
      }
    }

    if (result) {
      genericModal.classList.remove("visible");
      // Recargar silenciosamente las dependencias si es necesario
      if (section.key === 'requisitos') await loadItems(requisitosSectionDef, document.createElement('div'), true);
      if (section.key === 'casos_uso') await loadItems(casosUsoSectionDef, document.createElement('div'), true);
      
      await loadItems(section, sectionCardContainerElement); 
    } else {
      alert(`No se pudo ${itemId ? 'actualizar' : 'crear'} el elemento.`);
    }
  });

  modalCancelButton.addEventListener("click", () => {
    genericModal.classList.remove("visible");
  });

  async function handleDeleteItem(section, itemId, sectionCardContainerElement) {
    if (!confirm(`¿Está seguro de que desea eliminar este elemento de ${section.title.toLowerCase()}?`)) return;

    const endpoint = getEndpointForItem(section, itemId);
    let success;

    if (projectId === "dummyProject123") { // Simular borrado para dummy
        section.items = section.items.filter(it => it.id != itemId);
        success = true;
    } else {
        success = await authFetch(endpoint, { method: 'DELETE' });
    }

    if (success) {
      // Recargar silenciosamente las dependencias si es necesario
      if (section.key === 'requisitos') await loadItems(requisitosSectionDef, document.createElement('div'), true);
      if (section.key === 'casos_uso') await loadItems(casosUsoSectionDef, document.createElement('div'), true);
      await loadItems(section, sectionCardContainerElement);
    } else {
      alert("No se pudo eliminar el elemento.");
    }
  }

  // 5) Exportar PDF
  document.getElementById("exportPdf").onclick = () => {
    if (!proj) { alert("Datos del proyecto no cargados."); return; }
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF({ orientation: 'p', unit: 'mm', format: 'a4' });
    let y = 20;
    doc.setFontSize(18); 
    doc.text(proj.nombre, doc.internal.pageSize.getWidth() / 2, y, { align: 'center' }); y += 8;
    doc.setFontSize(11);
    doc.text(`Descripción: ${proj.descripcion || 'N/A'}`, 14, y); y += 7;
    doc.text(`Estado: ${proj.estado}`, 14, y); y += 12;
    
    sections.forEach(sec => {
      if (!sec.items || sec.items.length === 0) return;
      doc.setFontSize(14);
      doc.setTextColor(0, 107, 179); 
      doc.text(sec.title, 14, y); y += 8;
      doc.setTextColor(0,0,0); 

      const head = [sec.fields // Usar todos los fields definidos en la sección para exportar
        .map(f => f.replace(/_/g,' ').replace(/^\w/,c=>c.toUpperCase()))
      ];
      const body = sec.items.map(it =>
        sec.fields
          .map(f => {
            let val = it[f];
            if (f === 'caso_uso_id' && sec.key === 'escenarios') {
                const casoUso = casosUsoSectionDef.items.find(cu => cu.id === it.caso_uso_id);
                val = casoUso ? casoUso.titulo : `ID: ${it.caso_uso_id}`;
            } else if (f === 'requisito_id' && sec.key === 'casos_uso') {
                const requisito = requisitosSectionDef.items.find(r => r.id === it.requisito_id);
                val = requisito ? requisito.nombre : `ID: ${it.requisito_id}`;
            } else if (f === 'requisito_padre_id' && sec.key === 'requisitos') {
                const padre = requisitosSectionDef.items.find(r => r.id === it.requisito_padre_id);
                val = padre ? padre.nombre : (it.requisito_padre_id ? `ID: ${it.requisito_padre_id}` : 'Ninguno');
            } else if (f.startsWith('fecha_')) {
                val = formatDisplayDate(val);
            }
            return val !== null && typeof val !== 'undefined' ? String(val) : '';
          })
      );
      doc.autoTable({ 
        startY: y, 
        head: head, 
        body, 
        theme: 'grid', 
        styles: { fontSize: 8, cellPadding: 1.5, overflow: 'linebreak' },
        headStyles: { fillColor: [0, 107, 179], textColor: 255, fontStyle: 'bold' },
        alternateRowStyles: { fillColor: [240, 240, 240] },
        columnStyles: { // Ajustar ancho de columnas si es necesario, ejemplo:
            // 0: { cellWidth: 30 }, // Primera columna
            // 1: { cellWidth: 'auto'} 
        }
      });
      y = doc.lastAutoTable.finalY + 10;
      if (y > doc.internal.pageSize.getHeight() - 20) { // Salto de página si no hay espacio
          doc.addPage();
          y = 20;
      }
    });
    doc.save(`${proj.nombre.replace(/\s+/g,'_') || 'proyecto'}_detalle.pdf`);
  };

  // 6) Exportar Word
  document.getElementById("exportWord").onclick = () => {
    if (!proj) { alert("Datos del proyecto no cargados."); return; }
    let html = `
      <html xmlns:o="urn:schemas-microsoft-com:office:office"
            xmlns:w="urn:schemas-microsoft-com:office:word"
            xmlns="http://www.w3.org/TR/REC-html40">
      <head><meta charset="utf-8"><title>Detalle ${proj.nombre}</title>
      <style>
        body { font-family: Arial, sans-serif; font-size: 10pt; }
        table { border-collapse: collapse; width: 100%; margin-bottom: 15px; page-break-inside: avoid; }
        th, td { border: 1px solid #ccc; padding: 5px; text-align: left; word-wrap: break-word; }
        th { background-color: #e0e0e0; font-weight: bold; }
        h1 { color: #006bb3; font-size: 16pt;}
        h2 { color: #004d80; font-size: 13pt; border-bottom: 1px solid #ddd; padding-bottom: 4px; margin-top: 20px;}
        p { margin-bottom: 8px; }
      </style>
      </head><body>
      <h1>${proj.nombre}</h1>
      <p><b>Descripción:</b> ${proj.descripcion || 'N/A'}</p>
      <p><b>Estado:</b> ${proj.estado}</p>`;
    sections.forEach(sec => {
      if (!sec.items || sec.items.length === 0) return;
      html += `<h2>${sec.title}</h2><table><thead><tr>`
        + sec.fields // Usar todos los fields definidos en la sección para exportar
            .map(f => `<th>${f.replace(/_/g,' ').replace(/^\w/,c=>c.toUpperCase())}</th>`).join('')
        + `</tr></thead><tbody>`;
      sec.items.forEach(it => {
        html += `<tr>`
          + sec.fields
              .map(f => {
                let val = it[f];
                if (f === 'caso_uso_id' && sec.key === 'escenarios') {
                    const casoUso = casosUsoSectionDef.items.find(cu => cu.id === it.caso_uso_id);
                    val = casoUso ? casoUso.titulo : `ID: ${it.caso_uso_id}`;
                } else if (f === 'requisito_id' && sec.key === 'casos_uso') {
                    const requisito = requisitosSectionDef.items.find(r => r.id === it.requisito_id);
                    val = requisito ? requisito.nombre : `ID: ${it.requisito_id}`;
                } else if (f === 'requisito_padre_id' && sec.key === 'requisitos') {
                    const padre = requisitosSectionDef.items.find(r => r.id === it.requisito_padre_id);
                    val = padre ? padre.nombre : (it.requisito_padre_id ? `ID: ${it.requisito_padre_id}` : 'Ninguno');
                } else if (f.startsWith('fecha_')) {
                    val = formatDisplayDate(val);
                }
                return `<td>${val !== null && typeof val !== 'undefined' ? String(val).replace(/</g, "&lt;").replace(/>/g, "&gt;") : ''}</td>`;
              }).join('')
          + `</tr>`;
      });
      html += `</tbody></table>`;
    });
    html += `</body></html>`;
    const blob = new Blob(["\ufeff", html], { type: 'application/msword' });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement("a"); a.href = url;
    a.download = `${proj.nombre.replace(/\s+/g,'_') || 'proyecto'}_detalle.doc`;
    document.body.appendChild(a);
    a.click(); 
    setTimeout(() => {
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }, 100);
  };

  // 7) Logout
  document.getElementById("logoutLink").addEventListener("click", e => {
    e.preventDefault(); 
    localStorage.clear(); 
    window.location.href = "index.html";
  });

  genericModal.addEventListener('click', (event) => {
    if (event.target === genericModal) {
        genericModal.classList.remove("visible");
    }
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && genericModal.classList.contains('visible')) {
        genericModal.classList.remove("visible");
    }
  });

});
