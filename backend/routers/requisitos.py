from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .dependencies import get_db
from ..models import Proyecto, Requisito, Usuario
from ..schemas import RequisitoResponse, RequisitoCreate
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from ..security import SECRET_KEY, ALGORITHM

router = APIRouter(tags=["Requisitos"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
    user = db.query(Usuario).filter(Usuario.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return user

@router.get("/{project_id}/requisitos", response_model=List[RequisitoResponse])
def listar_requisitos(project_id: int,
                      db: Session = Depends(get_db),
                      current_user: Usuario = Depends(get_current_user)):
    project = db.query(Proyecto).filter(
        Proyecto.id == project_id,
        Proyecto.usuario_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return project.requisitos

@router.get("/{project_id}/requisitos/{requisito_id}", response_model=RequisitoResponse)
def obtener_requisito(project_id: int, requisito_id: int,
                      db: Session = Depends(get_db),
                      current_user: Usuario = Depends(get_current_user)):
    requisito = db.query(Requisito).join(Proyecto).filter(
        Proyecto.id == project_id,
        Proyecto.usuario_id == current_user.id,
        Requisito.id == requisito_id
    ).first()
    if not requisito:
        raise HTTPException(status_code=404, detail="Requisito no encontrado")
    return requisito

@router.post("/{project_id}/requisitos", response_model=RequisitoResponse, status_code=status.HTTP_201_CREATED)
def crear_requisito(project_id: int, req: RequisitoCreate,
                    db: Session = Depends(get_db),
                    current_user: Usuario = Depends(get_current_user)):
    project = db.query(Proyecto).filter(
        Proyecto.id == project_id,
        Proyecto.usuario_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    nuevo = Requisito(
        nombre=req.nombre,
        descripcion=req.descripcion,
        tipo=req.tipo,
        prioridad=req.prioridad,
        fuente=req.fuente,
        observaciones=req.observaciones,
        estado=req.estado,
        version=req.version,
        requisito_padre_id=req.requisito_padre_id,
        proyecto_id=project.id
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.put("/{project_id}/requisitos/{requisito_id}", response_model=RequisitoResponse)
def actualizar_requisito(project_id: int, requisito_id: int, req: RequisitoCreate,
                         db: Session = Depends(get_db),
                         current_user: Usuario = Depends(get_current_user)):
    db_req = db.query(Requisito).join(Proyecto).filter(
        Proyecto.id == project_id,
        Proyecto.usuario_id == current_user.id,
        Requisito.id == requisito_id
    ).first()
    if not db_req:
        raise HTTPException(status_code=404, detail="Requisito no encontrado")
    db_req.nombre = req.nombre
    db_req.descripcion = req.descripcion
    db_req.tipo = req.tipo
    db_req.prioridad = req.prioridad
    db_req.fuente = req.fuente
    db_req.observaciones = req.observaciones
    db_req.estado = req.estado
    db_req.version = req.version
    db_req.requisito_padre_id = req.requisito_padre_id
    db.commit()
    db.refresh(db_req)
    return db_req

@router.delete("/{project_id}/requisitos/{requisito_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_requisito(project_id: int, requisito_id: int,
                       db: Session = Depends(get_db),
                       current_user: Usuario = Depends(get_current_user)):
    db_req = db.query(Requisito).join(Proyecto).filter(
        Proyecto.id == project_id,
        Proyecto.usuario_id == current_user.id,
        Requisito.id == requisito_id
    ).first()
    if not db_req:
        raise HTTPException(status_code=404, detail="Requisito no encontrado")
    db.delete(db_req)
    db.commit()
    return None
