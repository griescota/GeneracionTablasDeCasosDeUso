# backend/main.py
from fastapi import FastAPI
from .database import Base, engine , SessionLocal
from . import models
from .auth import router as auth_router
from .crud import router as crud_router
from .routers import proyectos, requisitos, casos_uso, actores,escenarios,relaciones
from .mock_data import insertar_datos_mock
from fastapi.middleware.cors import CORSMiddleware

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)
# Insertar datos de prueba (mock) solo si la base de datos está vacía
with SessionLocal() as db:
    insertar_datos_mock(db)

app = FastAPI(title="API TFG")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          
    allow_credentials=True,
    allow_methods=["*"],          
    allow_headers=["*"],
)


app.include_router(auth_router, prefix="/auth", tags=["auth"])

# Rutas CRUD
app.include_router(proyectos.router, prefix="/projects", tags=["Proyectos"])
app.include_router(requisitos.router, prefix="/projects", tags=["Requisitos"])
app.include_router(casos_uso.router, prefix="/projects", tags=["Casos de Uso"])
app.include_router(actores.router, prefix="/actores", tags=["Actores"])
app.include_router(escenarios.router, prefix="/escenarios", tags=["Escenarios"])
app.include_router(relaciones.router, prefix="/relaciones", tags=["Relaciones"])

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de gestión de proyectos"}
