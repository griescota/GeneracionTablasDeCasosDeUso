
document.addEventListener("DOMContentLoaded", () => {
  
  const userName = localStorage.getItem("username") || "Usuario";
  document.getElementById("userName").textContent = userName;

  
  document.getElementById("logoutLink").addEventListener("click", e => {
    e.preventDefault();
    localStorage.clear();
    window.location.href = "index.html";
  });

  
  document.querySelectorAll(".card").forEach(card => {
    card.addEventListener("click", () => {
      const dest = card.dataset.dest;
      window.location.href = dest;
    });
  });

  
  document.getElementById("proyectosLink").addEventListener("click", e => {
    e.preventDefault();
    window.location.href = "proyectos.html";
  });
});



  