from sqlalchemy.orm import Session
from backend.models import (
    Usuario,
    Proyecto,
    Requisito,
    CasoUso,
    Escenario,
    RelacionRequisito,
    Actor,
    EstadoProyectoEnum,
    EstadoRequisitoEnum,
    EstadoCasoUsoEnum,
    TipoRequisitoEnum,
    CategoriaCasoUsoEnum,
    TipoEscenarioEnum,
)
from backend.security import hash_password

def insertar_datos_mock(db: Session):
    if db.query(Usuario).count() > 0:
        return

   
    u1 = Usuario(
        username="travel_admin",
        email="viajes@empresa.com",
        hashed_password=hash_password("viaje123")
    )
    db.add(u1); db.commit(); db.refresh(u1)

  
    actores = [
        Actor(nombre="Cliente", tipo="Humano", descripcion="Usuario final"),
        Actor(nombre="PasarelaPago", tipo="Sistema Externo", descripcion="Servicio de pago"),
        Actor(nombre="Soporte", tipo="Humano", descripcion="Atención al cliente"),
        Actor(nombre="Notificador", tipo="Sistema Externo", descripcion="Servicio de notificaciones"),
    ]
    db.add_all(actores); db.commit()

  
    p = Proyecto(
        nombre="Sistema de Reservas Online",
        descripcion="Reserva vuelos, hoteles y coches.",
        usuario_id=u1.id,
        estado=EstadoProyectoEnum.ACTIVO
    )
    db.add(p); db.commit(); db.refresh(p)


    r_busqueda = Requisito(
        nombre="Búsqueda Multimodal",
        descripcion="Buscar vuelos/hoteles/coches a la vez.",
        tipo=TipoRequisitoEnum.FUNCIONAL,
        proyecto_id=p.id,
        estado=EstadoRequisitoEnum.APROBADO,
        version=1
    )
    r_pago = Requisito(
        nombre="Pago Seguro",
        descripcion="Tokenización en pasarela de pago.",
        tipo=TipoRequisitoEnum.FUNCIONAL,
        proyecto_id=p.id,
        estado=EstadoRequisitoEnum.IMPLEMENTADO,
        version=2
    )
    db.add_all([r_busqueda, r_pago]); db.commit()
    db.refresh(r_busqueda); db.refresh(r_pago)


    cu_reserva = CasoUso(
        titulo="Reservar Paquete Vacacional",
        descripcion="Vuela, reserva hotel y coche juntos.",
        actores="Cliente,PasarelaPago,Notificador",
        precondiciones="Usuario autenticado.",
        postcondiciones="Reserva completada y voucher enviado.",
        flujo_normal="Elige paquete y paga.",
        flujo_alternativo="Pago rechazado: error.",
        categoria=CategoriaCasoUsoEnum.PRINCIPAL,
        requisito_id=r_pago.id,
        proyecto_id=p.id,
        estado=EstadoCasoUsoEnum.EN_DESARROLLO
    )
    db.add(cu_reserva); db.commit(); db.refresh(cu_reserva)

    escenarios = [
        Escenario(
            nombre="Flujo Normal",
            descripcion="Todo correcto.",
            tipo=TipoEscenarioEnum.NORMAL,
            caso_uso_id=cu_reserva.id,
            resultado_esperado="Voucher enviado."
        ),
        Escenario(
            nombre="Hotel Agotado",
            descripcion="Sin plazas en hotel.",
            tipo=TipoEscenarioEnum.ALTERNATIVO,
            caso_uso_id=cu_reserva.id,
            resultado_esperado="Sugerir alternativa."
        ),
        Escenario(
            nombre="Pago Fallido",
            descripcion="Error en pasarela.",
            tipo=TipoEscenarioEnum.EXCEPCION,
            caso_uso_id=cu_reserva.id,
            resultado_esperado="Mostrar mensaje de error."
        ),
    ]
    db.add_all(escenarios); db.commit()

    db.add(RelacionRequisito(requisito_id=r_pago.id, caso_uso_id=cu_reserva.id))
    db.commit()

    print("Datos mock correctamente insertados.")
