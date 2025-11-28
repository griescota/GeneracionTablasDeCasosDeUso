from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .dependencies import get_db
from ..models import Proyecto, Usuario
from ..schemas import ProyectoResponse, ProyectoCreate
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from ..security import SECRET_KEY, ALGORITHM

router = APIRouter( tags=["Proyectos"])
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

@router.get("/", response_model=List[ProyectoResponse])
def get_projects(db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    proyectos = db.query(Proyecto).filter(Proyecto.usuario_id == current_user.id).all()
    return proyectos

@router.post("/", response_model=ProyectoResponse, status_code=status.HTTP_201_CREATED)
def create_project(proyecto: ProyectoCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    nuevo_proyecto = Proyecto(
        nombre=proyecto.nombre,
        descripcion=proyecto.descripcion,
        estado=proyecto.estado,
        usuario_id=current_user.id
    )
    db.add(nuevo_proyecto)
    db.commit()
    db.refresh(nuevo_proyecto)
    return nuevo_proyecto

@router.get("/{project_id}", response_model=ProyectoResponse)
def get_project(project_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    project = db.query(Proyecto).filter(
        Proyecto.id == project_id,
        Proyecto.usuario_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado o no te pertenece")
    return project

@router.put("/{project_id}", response_model=ProyectoResponse)
def update_project(project_id: int, proyecto: ProyectoCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    db_proj = db.query(Proyecto).filter(
        Proyecto.id == project_id,
        Proyecto.usuario_id == current_user.id
    ).first()
    if not db_proj:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado o no te pertenece")
    db_proj.nombre = proyecto.nombre
    db_proj.descripcion = proyecto.descripcion
    db_proj.estado = proyecto.estado
    db.commit()
    db.refresh(db_proj)
    return db_proj

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    db_proj = db.query(Proyecto).filter(
        Proyecto.id == project_id,
        Proyecto.usuario_id == current_user.id
    ).first()
    if not db_proj:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado o no te pertenece")
    db.delete(db_proj)
    db.commit()
    return None
