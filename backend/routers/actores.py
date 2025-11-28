
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .dependencies import get_db
from ..models import Actor, Usuario
from ..schemas import ActorResponse, ActorCreate
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from ..security import SECRET_KEY, ALGORITHM

router = APIRouter()
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

@router.get("/", response_model=List[ActorResponse])
def get_actores(db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    return db.query(Actor).all()

@router.post("/", response_model=ActorResponse)
def create_actor(actor: ActorCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    nuevo_actor = Actor(
        nombre=actor.nombre,
        tipo=actor.tipo,
        descripcion=actor.descripcion
    )
    db.add(nuevo_actor)
    db.commit()
    db.refresh(nuevo_actor)
    return nuevo_actor

@router.get("/{actor_id}", response_model=ActorResponse)
def get_actor(actor_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    actor = db.query(Actor).filter(Actor.id == actor_id).first()
    if not actor:
        raise HTTPException(status_code=404, detail="Actor no encontrado")
    return actor

@router.put("/{actor_id}", response_model=ActorResponse)
def update_actor(actor_id: int, actor: ActorCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    db_actor = db.query(Actor).filter(Actor.id == actor_id).first()
    if not db_actor:
        raise HTTPException(status_code=404, detail="Actor no encontrado")
    db_actor.nombre = actor.nombre
    db_actor.tipo = actor.tipo
    db_actor.descripcion = actor.descripcion
    db.commit()
    db.refresh(db_actor)
    return db_actor

@router.delete("/{actor_id}")
def delete_actor(actor_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    db_actor = db.query(Actor).filter(Actor.id == actor_id).first()
    if not db_actor:
        raise HTTPException(status_code=404, detail="Actor no encontrado")
    db.delete(db_actor)
    db.commit()
    return {"detail": "Actor eliminado"}
