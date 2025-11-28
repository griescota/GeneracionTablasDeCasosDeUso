

document.addEventListener("DOMContentLoaded", () => {
  const baseUrl     = "http://127.0.0.1:8000";
  const token       = localStorage.getItem("token");
  const projectsList= document.getElementById("projects-list");
  const newBtn      = document.getElementById("btn-new-project");
  const modal       = document.getElementById("modal-new");
  const form        = document.getElementById("form-new-project");
  const closeBtn    = document.getElementById("modal-close");
  const filters     = document.querySelectorAll(".filter-btn");

  let projects = [];
  let currentFilter = "ACTIVO";

  // Hacer petición autenticada
  const authFetch = (url, opts = {}) =>
    fetch(url, {
      ...opts,
      headers: {
        "Authorization": `Bearer ${token}`,
        ...opts.body && { "Content-Type": "application/json" }
      }
    });

  function fmtDate(s) {
    const d = new Date(s);
    return d.toLocaleDateString() + " " + d.toLocaleTimeString();
  }

  // Carga inicial
  async function loadProjects() {
    try {
      const res = await authFetch(`${baseUrl}/projects/`);
      if (!res.ok) throw new Error(res.status);
      projects = await res.json();
      render();
    } catch (e) {
      projectsList.innerHTML = `<p class="error">Error al cargar proyectos.</p>`;
    }
  }

  // Render de tarjetas
  function render() {
    projectsList.innerHTML = "";
    const filtered = projects.filter(p =>
      currentFilter === "ALL" ? true :
      p.estado.toUpperCase() === currentFilter
    );
    if (filtered.length === 0) {
      projectsList.innerHTML = `<p>No hay proyectos "${currentFilter}".</p>`;
      return;
    }
    filtered.forEach(p => {
      const card = document.createElement("div");
      card.className = "card";
      card.innerHTML = `
        <div class="card-header">
          <h3>${p.nombre}</h3>
          <span class="status-badge status-${p.estado.toLowerCase()}">
            ${p.estado.toUpperCase()}
          </span>
        </div>
        <small>ID: ${p.id} | Creado: ${fmtDate(p.fecha_creacion)}</small>
        <p class="desc">${p.descripcion||"—"}</p>
        <div class="actions">
          <button data-action="view"   data-id="${p.id}" class="btn-view">Ver</button>
          <button data-action="edit"   data-id="${p.id}" class="btn-edit">✎</button>
          <button data-action="delete" data-id="${p.id}" class="btn-del">🗑</button>
        </div>`;
      projectsList.appendChild(card);
    });
  }

  // Filtrar
  filters.forEach(btn => {
    btn.addEventListener("click", () => {
      filters.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      currentFilter = btn.dataset.filter;
      render();
    });
  });

  // Abrir modal
  newBtn.addEventListener("click", () => modal.classList.add("open"));
  closeBtn.addEventListener("click", () => {
    modal.classList.remove("open");
    form.reset();
  });

  // Crear proyecto
  form.addEventListener("submit", async e => {
    e.preventDefault();
    const data = {
      nombre:      form["project-name"].value,
      descripcion: form["project-description"].value,
      estado:      form["project-status"].value
    };
    try {
      const res = await authFetch(`${baseUrl}/projects/`, {
        method: "POST",
        body: JSON.stringify(data)
      });
      if (!res.ok) throw new Error(res.status);
      const created = await res.json();
      projects.push(created);
      render();
      form.reset();
      modal.classList.remove("open");
    } catch {
      alert("Error al crear proyecto.");
    }
  });

  // Delegar acciones
  projectsList.addEventListener("click", async e => {
    const btn = e.target.closest("button");
    if (!btn) return;
    const id = btn.dataset.id;
    const act= btn.dataset.action;

    if (act === "view") {
      return window.location.href = `proyecto_detalle.html?project_id=${id}`;
    }
    if (act === "delete" && confirm("Eliminar proyecto?")) {
      await authFetch(`${baseUrl}/projects/${id}`, { method: "DELETE" });
      projects = projects.filter(p => p.id != id);
      render();
    }
    if (act === "edit") {
      const p = projects.find(x => x.id == id);
      const n = prompt("Nuevo nombre:", p.nombre);
      if (!n) return;
      const d = prompt("Nueva descripción:", p.descripcion);
      if (d == null) return;
      let s = "";
      const opts = ["ACTIVO","COMPLETADO","CANCELADO"];
      while (!opts.includes(s)) {
        s = prompt(`Estado (${opts.join("/")})`, p.estado.toUpperCase());
        if (s == null) return;
      }
      const res = await authFetch(`${baseUrl}/projects/${id}`, {
        method:"PUT",
        body: JSON.stringify({ nombre:n, descripcion:d, estado:s })
      });
      const up = await res.json();
      projects = projects.map(x=> x.id==id?up:x);
      render();
    }
  });

  // Logout
  document.getElementById("logoutLink").addEventListener("click", e=>{
    e.preventDefault();
    localStorage.clear();
    window.location.href="index.html";
  });

  // Arranca
  if (!token) return window.location.href="index.html";
  loadProjects();
});

