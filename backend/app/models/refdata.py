from sqlalchemy import Column, Integer, String, UniqueConstraint
from ..db import Base
class Medico(Base):
    __tablename__ = "medicos"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(200), unique=True, nullable=False)
class Cobertura(Base):
    __tablename__ = "coberturas"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(200), unique=True, nullable=False)
class Sector(Base):
    __tablename__ = "sectores"
    id = Column(Integer, primary_key=True)
    codigo = Column(String(60), nullable=False)
    nombre = Column(String(200), nullable=False)
    __table_args__ = (UniqueConstraint("codigo", name="uq_sector_codigo"),)
