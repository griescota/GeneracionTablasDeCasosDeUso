from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .dependencies import get_db
from ..models import RelacionRequisito, Usuario
from ..schemas import RelacionRequisitoResponse, RelacionRequisitoCreate
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from ..security import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/relaciones", tags=["Relaciones"])
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

@router.get("/", response_model=List[RelacionRequisitoResponse])
def get_relaciones(db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    return db.query(RelacionRequisito).all()

@router.post("/", response_model=RelacionRequisitoResponse, status_code=status.HTTP_201_CREATED)
def create_relacion(relacion: RelacionRequisitoCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    nuevo_relacion = RelacionRequisito(
        requisito_id=relacion.requisito_id,
        caso_uso_id=relacion.caso_uso_id
    )
    db.add(nuevo_relacion)
    db.commit()
    db.refresh(nuevo_relacion)
    return nuevo_relacion

@router.delete("/{relacion_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_relacion(relacion_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    relacion = db.query(RelacionRequisito).filter(RelacionRequisito.id == relacion_id).first()
    if not relacion:
        raise HTTPException(status_code=404, detail="Relación no encontrada")
    db.delete(relacion)
    db.commit()
    return None

