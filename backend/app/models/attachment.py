from sqlalchemy import Column, Integer, String
from ..db import Base
class Attachment(Base):
    __tablename__ = "attachments"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, index=True)
    kind = Column(String(60), default="Otro")
    filename = Column(String(300), nullable=False)
    url = Column(String(800), nullable=False)
    preview_url = Column(String(800), default="")
    icon_url = Column(String(400), default="")
