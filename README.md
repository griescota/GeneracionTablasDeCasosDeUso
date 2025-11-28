# Generador de Tablas de Casos de Uso (FastAPI + SQLite)

**Herramienta basada en la Metodología de Elicitación de Requisitos de Durán y Bernárdez**

Este proyecto es una aplicación web diseñada para la generación automática y estructurada de tablas de casos de uso. Soluciona el desafío de la creación manual, automatizando la captura de información detallada (actores, secuencias, escenarios) y transformándola en documentación estandarizada.

---

## 🎯 Objetivo Principal

Proporcionar una solución tecnológica para la fase de elicitación de requisitos, reduciendo el tiempo y minimizando errores en la documentación al automatizar la creación de tablas de casos de uso conforme a la metodología de Durán y Bernárdez.

---

## ⚙️ Arquitectura del Sistema (Modelo C4)

La arquitectura del sistema sigue un modelo de contenedores claro, separando las responsabilidades de la lógica de negocio, la persistencia de datos y la interfaz de usuario.

### Tecnologías Clave
- **Backend (API):** FastAPI (Python) para construir APIs rápidas y asíncronas.  
- **Base de Datos:** SQLite para almacenamiento local eficiente y sin servidor.  
- **Frontend (Cliente):** HTML, CSS y JavaScript para captura intuitiva de datos.  
- **Generación de Documentos:** Librerías para exportar tablas a PDF o formatos de texto estructurado.  

---

## ✨ Funcionalidades Destacadas

- **Creación Estructurada:** Formularios web para capturar:  
  - Actores, Precondiciones y Postcondiciones  
  - Flujo Principal de Eventos  
  - Escenarios Alternativos y Excepciones  

- **Persistencia:** Almacenamiento seguro en SQLite.  
- **Generación de Documentos:** Exportación a PDF, Markdown o Word.  
- **Autenticación:** Gestión de usuarios con JWT (JSON Web Tokens) para asegurar la API.  

---

## 🚀 Instalación y Ejecución Local

### Prerrequisitos
- Python 3.8+  
- Pip (Gestor de paquetes de Python)  
- Git  


