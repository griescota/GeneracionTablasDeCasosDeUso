# backend/crud.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas
from .routers.dependencies import get_db
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from .security import SECRET_KEY, ALGORITHM
from .models import Usuario

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Decodificar el token
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    user = db.query(Usuario).filter(Usuario.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return user

# Ejemplo CRUD para Proyectos
@router.get("/projects", response_model=list[schemas.ProyectoResponse])
def get_projects(db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    return db.query(models.Proyecto).filter(models.Proyecto.usuario_id == current_user.id).all()

@router.post("/projects", response_model=schemas.ProyectoResponse)
def create_project(proyecto: schemas.ProyectoResponse, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    nuevo_proyecto = models.Proyecto(
        nombre=proyecto.nombre,
        descripcion=proyecto.descripcion,
        usuario_id=current_user.id
    )
    db.add(nuevo_proyecto)
    db.commit()
    db.refresh(nuevo_proyecto)
    return nuevo_proyecto

@router.get("/projects/{project_id}", response_model=schemas.ProyectoResponse)
def get_project(project_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    project = db.query(models.Proyecto).filter(models.Proyecto.id == project_id, models.Proyecto.usuario_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado o no te pertenece")
    return project

@router.put("/projects/{project_id}", response_model=schemas.ProyectoResponse)
def update_project(project_id: int, proyecto: schemas.ProyectoResponse, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    db_proj = db.query(models.Proyecto).filter(models.Proyecto.id == project_id, models.Proyecto.usuario_id == current_user.id).first()
    if not db_proj:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado o no te pertenece")

    db_proj.nombre = proyecto.nombre
    db_proj.descripcion = proyecto.descripcion
    db.commit()
    db.refresh(db_proj)
    return db_proj

@router.delete("/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    db_proj = db.query(models.Proyecto).filter(models.Proyecto.id == project_id, models.Proyecto.usuario_id == current_user.id).first()
    if not db_proj:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado o no te pertenece")

    db.delete(db_proj)
    db.commit()
    return {"detail": "Proyecto eliminado"}
