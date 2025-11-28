from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

# --- Usuario ---
class UsuarioCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UsuarioLogin(BaseModel):
    username: str
    password: str

class UsuarioResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True

# --- Proyecto ---
class ProyectoCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    estado: Optional[str] = "ACTIVO"  # Valores sugeridos: 'Activo', 'Completado', 'Cancelado'

    class Config:
        from_attributes = True

class ProyectoResponse(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None
    estado: str
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- Requisito ---
class RequisitoCreate(BaseModel):
    nombre: str
    descripcion: str
    tipo: str  # 'FUNCIONAL' o 'NO_FUNCIONAL'
    prioridad: Optional[int] = 1
    fuente: Optional[str] = None
    observaciones: Optional[str] = None
    estado: Optional[str] = "PROPUESTO"  # Valores sugeridos: 'Propuesto', 'Aprobado', 'Implementado', 'Verificado', 'Rechazado'
    version: Optional[int] = 1
    requisito_padre_id: Optional[int] = None
    class Config:
        from_attributes = True

class RequisitoResponse(BaseModel):
    id: int
    nombre: str
    descripcion: str
    tipo: str
    proyecto_id: int
    prioridad: int
    fuente: Optional[str] = None
    observaciones: Optional[str] = None
    requisito_padre_id: Optional[int]
    estado: str
    version: int
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- Caso de Uso ---
class CasoUsoCreate(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    actores: Optional[str] = None  # Lista separada por comas o, opcionalmente, manejar una relación N-N
    precondiciones: Optional[str] = None
    postcondiciones: Optional[str] = None
    flujo_normal: Optional[str] = None
    flujo_alternativo: Optional[str] = None
    categoria: str  # 'PRINCIPAL', 'SECUNDARIO' o 'EXCEPCIONAL'
    requisito_id: Optional[int] = None
    estado: Optional[str] = "PROPUESTO"  # Valores sugeridos: 'Propuesto', 'En Desarrollo', 'Implementado', 'Validado'

    class Config:
        from_attributes = True

class CasoUsoResponse(BaseModel):
    id: int
    titulo: str
    descripcion: Optional[str] = None
    actores: Optional[str] = None
    precondiciones: Optional[str] = None
    postcondiciones: Optional[str] = None
    flujo_normal: Optional[str] = None
    flujo_alternativo: Optional[str] = None
    categoria: str
    estado: str
    requisito_id: Optional[int] = None
    proyecto_id: Optional[int] = None
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- Actor ---
class ActorCreate(BaseModel):
    nombre: str
    tipo: str  # Ej.: "Humano" o "Sistema Externo"
    descripcion: Optional[str] = None

    class Config:
        from_attributes = True

class ActorResponse(BaseModel):
    id: int
    nombre: str
    tipo: str
    descripcion: Optional[str] = None

    class Config:
        from_attributes = True

# --- Escenario ---
class EscenarioCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    tipo: str  # 'NORMAL', 'ALTERNATIVO' o 'EXCEPCION'
    caso_uso_id: int
    resultado_esperado: Optional[str] = None  # Campo agregado

    class Config:
        from_attributes = True

class EscenarioResponse(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None
    tipo: str
    caso_uso_id: int
    resultado_esperado: Optional[str] = None
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- Relacion Requisito ---
class RelacionRequisitoCreate(BaseModel):
    requisito_id: int
    caso_uso_id: int

    class Config:
        from_attributes = True

class RelacionRequisitoResponse(BaseModel):
    id: int
    requisito_id: int
    caso_uso_id: int

    class Config:
        from_attributes = True
