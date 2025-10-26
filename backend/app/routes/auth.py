from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..db import SessionLocal
from ..models.user import User
from ..utils import verify_password, hash_password, create_token
router = APIRouter(prefix="/api/auth", tags=["auth"])
class LoginReq(BaseModel):
    email: str
    password: str
def get_db():
    db=SessionLocal()
    try: yield db
    finally: db.close()
@router.post("/login")
def login(payload: LoginReq, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email==payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    token = create_token({"sub": user.email, "rol": user.rol, "nombre": user.nombre})
    return {"ok": True, "token": token, "rol": user.rol, "nombre": user.nombre, "email": user.email}
@router.post("/seed-admin")
def seed_admin(db: Session = Depends(get_db)):
    if db.query(User).count()==0:
        u=User(nombre="Admin", email="admin@cemic.local", hashed_password=hash_password("admin"), rol="admin")
        db.add(u); db.commit(); return {"ok": True, "created": True}
    return {"ok": True, "created": False}
