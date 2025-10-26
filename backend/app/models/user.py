from sqlalchemy import Column, Integer, String, Boolean
from ..db import Base
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(120), nullable=False)
    email = Column(String(160), unique=True, index=True, nullable=False)
    hashed_password = Column(String(256), nullable=False)
    rol = Column(String(20), default="operador")
    telefono = Column(String(64), default="")
    centro = Column(String(128), default="")
    is_active = Column(Boolean, default=True)
