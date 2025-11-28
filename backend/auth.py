from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from . import models, schemas, security
from .routers.dependencies import get_db
from jose import JWTError, jwt

router = APIRouter()

@router.post("/register", response_model=schemas.UsuarioResponse)
def register_user(user: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    # Verificar si el usuario o el email ya existen
    existing_user = db.query(models.Usuario).filter(
        (models.Usuario.username == user.username) | (models.Usuario.email == user.email)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Usuario o email ya existe")

    hashed_password = security.hash_password(user.password)
    nuevo_usuario = models.Usuario(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.Usuario).filter(models.Usuario.username == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    access_token = security.create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}