from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .dependencies import get_db
from ..models import Proyecto, CasoUso, Usuario
from ..schemas import CasoUsoResponse, CasoUsoCreate
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from ..security import SECRET_KEY, ALGORITHM

router = APIRouter( tags=["Casos de Uso"])
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

@router.get("/{project_id}/casos_uso", response_model=List[CasoUsoResponse])
def listar_casos_uso(project_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    project = db.query(Proyecto).filter(
        Proyecto.id == project_id,
        Proyecto.usuario_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado o no te pertenece")
    return project.casos_uso

@router.get("/{project_id}/casos_uso/{caso_uso_id}", response_model=CasoUsoResponse)
def obtener_caso_uso(project_id: int, caso_uso_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    project = db.query(Proyecto).filter(
        Proyecto.id == project_id,
        Proyecto.usuario_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado o no te pertenece")
    caso = db.query(CasoUso).filter(
        CasoUso.id == caso_uso_id,
        CasoUso.proyecto_id == project_id
    ).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso de uso no encontrado en este proyecto")
    return caso

@router.post("/{project_id}/casos_uso", response_model=CasoUsoResponse, status_code=status.HTTP_201_CREATED)
def crear_caso_uso(project_id: int, cu: CasoUsoCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    project = db.query(Proyecto).filter(
        Proyecto.id == project_id,
        Proyecto.usuario_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado o no te pertenece")
    nuevo_caso = CasoUso(
        titulo=cu.titulo,
        descripcion=cu.descripcion,
        actores=cu.actores,
        precondiciones=cu.precondiciones,
        postcondiciones=cu.postcondiciones,
        flujo_normal=cu.flujo_normal,
        flujo_alternativo=cu.flujo_alternativo,
        categoria=cu.categoria,
        estado=cu.estado,
        requisito_id=cu.requisito_id,
        proyecto_id=project.id
    )
    db.add(nuevo_caso)
    db.commit()
    db.refresh(nuevo_caso)
    return nuevo_caso

@router.put("/{project_id}/casos_uso/{caso_uso_id}", response_model=CasoUsoResponse)
def actualizar_caso_uso(project_id: int, caso_uso_id: int, cu: CasoUsoCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    project = db.query(Proyecto).filter(
        Proyecto.id == project_id,
        Proyecto.usuario_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado o no te pertenece")
    db_caso = db.query(CasoUso).filter(
        CasoUso.id == caso_uso_id,
        CasoUso.proyecto_id == project.id
    ).first()
    if not db_caso:
        raise HTTPException(status_code=404, detail="Caso de uso no encontrado en este proyecto")
    db_caso.titulo = cu.titulo
    db_caso.descripcion = cu.descripcion
    db_caso.actores = cu.actores
    db_caso.precondiciones = cu.precondiciones
    db_caso.postcondiciones = cu.postcondiciones
    db_caso.flujo_normal = cu.flujo_normal
    db_caso.flujo_alternativo = cu.flujo_alternativo
    db_caso.categoria = cu.categoria
    db_caso.estado = cu.estado
    db_caso.requisito_id = cu.requisito_id
    db.commit()
    db.refresh(db_caso)
    return db_caso

@router.delete("/{project_id}/casos_uso/{caso_uso_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_caso_uso(project_id: int, caso_uso_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    project = db.query(Proyecto).filter(
        Proyecto.id == project_id,
        Proyecto.usuario_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado o no te pertenece")
    db_caso = db.query(CasoUso).filter(
        CasoUso.id == caso_uso_id,
        CasoUso.proyecto_id == project.id
    ).first()
    if not db_caso:
        raise HTTPException(status_code=404, detail="Caso de uso no encontrado en este proyecto")
    db.delete(db_caso)
    db.commit()
    return None


