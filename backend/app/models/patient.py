from sqlalchemy import Column, Integer, String
from ..db import Base
class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(200), nullable=False)
    dni = Column(String(32), nullable=False)
    email = Column(String(160), default="")
    telefono = Column(String(64), default="")
    cobertura = Column(String(200), default="")
    medico = Column(String(200), default="")
    sector_code = Column(String(60), default="")
    fecha_cx = Column(String(10), default="")
    estado = Column(String(60), default="Pendiente")
    presupuesto = Column(String(60), default="")
    fecha_carga = Column(String(19), default="")
    subcarpeta_url = Column(String(500), default="")
    reprogramacion = Column(String(10), default="")
    observaciones_reprogramacion = Column(String(300), default="")
    obs_proveedores = Column(String(300), default="")
