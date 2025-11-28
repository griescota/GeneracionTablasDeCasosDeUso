document.addEventListener("DOMContentLoaded", () => {
  // Elementos de los botones
  const loginBtn = document.getElementById("loginBtn");
  const registerBtn = document.getElementById("registerBtn");
  // Formularios
  const loginForm = document.getElementById("loginForm");
  const registerForm = document.getElementById("registerForm");

  // Alternar formularios
  loginBtn.addEventListener("click", () => {
    loginBtn.classList.add("active");
    registerBtn.classList.remove("active");
    loginForm.classList.remove("hidden");
    registerForm.classList.add("hidden");
  });

  registerBtn.addEventListener("click", () => {
    registerBtn.classList.add("active");
    loginBtn.classList.remove("active");
    registerForm.classList.remove("hidden");
    loginForm.classList.add("hidden");
  });

  // Manejo del formulario de login
  const formLogin = document.getElementById("form-login");
  formLogin.addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = document.getElementById("login-username").value;
    const password = document.getElementById("login-password").value;

    try {
      const response = await fetch("http://127.0.0.1:8000/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded"
        },
        body: new URLSearchParams({ username, password })
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Error al iniciar sesión");
      }
      const data = await response.json();
      document.getElementById("login-message").textContent = "Login exitoso.";
      // Guarda el token y el nombre de usuario en localStorage
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("username", username);
      // Redirige al dashboard (página principal)
      window.location.href = "dashboard.html";
    } catch (error) {
      document.getElementById("login-message").textContent = error.message;
    }
  });

  // Manejo del formulario de registro
  const formRegister = document.getElementById("form-register");
  formRegister.addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = document.getElementById("register-username").value;
    const email = document.getElementById("register-email").value;
    const password = document.getElementById("register-password").value;

    try {
      const response = await fetch("http://127.0.0.1:8000/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ username, email, password })
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Error al registrar");
      }
      const data = await response.json();
      document.getElementById("register-message").textContent = "Registro exitoso. Ahora inicia sesión.";
      // Limpia el formulario de registro
      formRegister.reset();
    } catch (error) {
      document.getElementById("register-message").textContent = error.message;
    }
  });
});

