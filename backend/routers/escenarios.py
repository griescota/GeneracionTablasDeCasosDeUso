from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .dependencies import get_db
from ..models import Escenario, Usuario
from ..schemas import EscenarioResponse, EscenarioCreate
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from ..security import SECRET_KEY, ALGORITHM

router = APIRouter( tags=["Escenarios"])
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

@router.get("/", response_model=List[EscenarioResponse])
def get_escenarios(db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    return db.query(Escenario).all()

@router.post("/", response_model=EscenarioResponse, status_code=status.HTTP_201_CREATED)
def create_escenario(escenario: EscenarioCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    nuevo_escenario = Escenario(
        nombre=escenario.nombre,
        descripcion=escenario.descripcion,
        tipo=escenario.tipo,
        caso_uso_id=escenario.caso_uso_id,
        resultado_esperado=escenario.resultado_esperado
    )
    db.add(nuevo_escenario)
    db.commit()
    db.refresh(nuevo_escenario)
    return nuevo_escenario

@router.get("/{escenario_id}", response_model=EscenarioResponse)
def get_escenario(escenario_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    escenario = db.query(Escenario).filter(Escenario.id == escenario_id).first()
    if not escenario:
        raise HTTPException(status_code=404, detail="Escenario no encontrado")
    return escenario

@router.put("/{escenario_id}", response_model=EscenarioResponse)
def update_escenario(escenario_id: int, escenario: EscenarioCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    db_escenario = db.query(Escenario).filter(Escenario.id == escenario_id).first()
    if not db_escenario:
        raise HTTPException(status_code=404, detail="Escenario no encontrado")
    db_escenario.nombre = escenario.nombre
    db_escenario.descripcion = escenario.descripcion
    db_escenario.tipo = escenario.tipo
    db_escenario.caso_uso_id = escenario.caso_uso_id
    db_escenario.resultado_esperado = escenario.resultado_esperado
    db.commit()
    db.refresh(db_escenario)
    return db_escenario

@router.delete("/{escenario_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_escenario(escenario_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    db_escenario = db.query(Escenario).filter(Escenario.id == escenario_id).first()
    if not db_escenario:
        raise HTTPException(status_code=404, detail="Escenario no encontrado")
    db.delete(db_escenario)
    db.commit()
    return None
