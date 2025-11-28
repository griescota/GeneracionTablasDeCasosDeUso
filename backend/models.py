from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func, Enum as SQLEnum
from sqlalchemy.orm import relationship, backref
from backend.database import Base 
import enum

# Enumerados existentes
class TipoRequisitoEnum(enum.Enum):
    FUNCIONAL = "FUNCIONAL"
    NO_FUNCIONAL = "NO_FUNCIONAL"

class CategoriaCasoUsoEnum(enum.Enum):
    PRINCIPAL = "Principal"
    SECUNDARIO = "Secundario"
    EXCEPCIONAL = "Excepcional"

class TipoEscenarioEnum(enum.Enum):
    NORMAL = "NORMAL"
    ALTERNATIVO = "ALTERNATIVO"
    EXCEPCION = "EXCEPCION"



class EstadoProyectoEnum(enum.Enum):
    ACTIVO = "Activo"
    COMPLETADO = "Completado"
    CANCELADO = "Cancelado"

class EstadoRequisitoEnum(enum.Enum):
    PROPUESTO = "Propuesto"
    APROBADO = "Aprobado"
    IMPLEMENTADO = "Implementado"
    VERIFICADO = "Verificado"
    RECHAZADO = "Rechazado"

class EstadoCasoUsoEnum(enum.Enum):
    PROPUESTO = "Propuesto"
    EN_DESARROLLO = "En Desarrollo"
    IMPLEMENTADO = "Implementado"
    VALIDADO = "Validado"

# Modelo Usuario
class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    # Un usuario tiene muchos proyectos
    proyectos = relationship("Proyecto", back_populates="usuario", cascade="all, delete-orphan")

# Modelo Proyecto
class Proyecto(Base):
    __tablename__ = "proyectos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False, unique=True)
    descripcion = Column(Text)
    fecha_creacion = Column(DateTime, default=func.now(), nullable=False)
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    estado = Column(SQLEnum(EstadoProyectoEnum), default=EstadoProyectoEnum.ACTIVO, nullable=False)

    # Cada proyecto pertenece a un usuario
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario = relationship("Usuario", back_populates="proyectos")

    # Relaciones internas
    requisitos = relationship("Requisito", back_populates="proyecto", cascade="all, delete-orphan")
    casos_uso = relationship("CasoUso", back_populates="proyecto", cascade="all, delete-orphan")

class Requisito(Base):
    __tablename__ = "requisitos"
    id                   = Column(Integer, primary_key=True, index=True)
    nombre               = Column(String(255), nullable=False)
    descripcion          = Column(Text, nullable=False)
    tipo                 = Column(SQLEnum(TipoRequisitoEnum, native_enum=False), nullable=False)
    proyecto_id          = Column(Integer, ForeignKey("proyectos.id"))
    prioridad            = Column(Integer, nullable=False, default=1)
    fuente               = Column(String(255))
    observaciones        = Column(Text)
    fecha_creacion       = Column(DateTime, default=func.now(), nullable=False)
    fecha_actualizacion  = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    estado               = Column(
                              SQLEnum(
                                EstadoRequisitoEnum,
                                native_enum=False,                # <— usa valores, no nombres
                                create_constraint=True,           # opcional
                                values_callable=lambda enum_cls: [e.value for e in enum_cls]
                              ),
                              default=EstadoRequisitoEnum.PROPUESTO,
                              nullable=False
                            )
    version              = Column(Integer, default=1)

    # Dependencia jerárquica
    requisito_padre_id   = Column(Integer, ForeignKey("requisitos.id"), nullable=True)
    dependientes         = relationship(
                             "Requisito",
                             backref=backref("padre", remote_side=[id]),
                             cascade="all, delete-orphan"
                           )

    proyecto             = relationship("Proyecto", back_populates="requisitos")
    casos_uso            = relationship("CasoUso", back_populates="requisito", cascade="all, delete-orphan")
# Modelo CasoUso
class CasoUso(Base):
    __tablename__ = "casos_uso"
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(255), nullable=False)
    descripcion = Column(Text)
    actores = Column(Text)  # Lista separada por comas (o se puede modelar con una relación N-N)
    precondiciones = Column(Text)
    postcondiciones = Column(Text)
    flujo_normal = Column(Text)
    flujo_alternativo = Column(Text)
    categoria = Column(SQLEnum(CategoriaCasoUsoEnum), nullable=False)
    requisito_id = Column(Integer, ForeignKey("requisitos.id"))
    proyecto_id = Column(Integer, ForeignKey("proyectos.id"))
    fecha_creacion = Column(DateTime, default=func.now(), nullable=False)
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    estado = Column(SQLEnum(EstadoCasoUsoEnum), default=EstadoCasoUsoEnum.PROPUESTO, nullable=False)

    requisito = relationship("Requisito", back_populates="casos_uso")
    proyecto = relationship("Proyecto", back_populates="casos_uso")
    escenarios = relationship("Escenario", back_populates="caso_uso", cascade="all, delete-orphan")

# Modelo Actor
class Actor(Base):
    __tablename__ = "actores"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    tipo = Column(String(50), nullable=False)  # Humano o Sistema Externo
    descripcion = Column(Text)

# Modelo RelacionRequisito
class RelacionRequisito(Base):
    __tablename__ = "relaciones_requisitos"
    id = Column(Integer, primary_key=True, index=True)
    requisito_id = Column(Integer, ForeignKey("requisitos.id"))
    caso_uso_id = Column(Integer, ForeignKey("casos_uso.id"))

    requisito = relationship("Requisito")
    caso_uso = relationship("CasoUso")

# Modelo Escenario
class Escenario(Base):
    __tablename__ = "escenarios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text)
    tipo = Column(SQLEnum(TipoEscenarioEnum), nullable=False)
    caso_uso_id = Column(Integer, ForeignKey("casos_uso.id"))
    fecha_creacion = Column(DateTime, default=func.now(), nullable=False)
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    resultado_esperado = Column(Text)  # Campo agregado para definir el resultado esperado

    caso_uso = relationship("CasoUso", back_populates="escenarios")


