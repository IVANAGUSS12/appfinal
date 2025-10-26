from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

from .db import init_db
from .routes import auth, ref, patients  # ✅ Importa las rutas

# Crear carpetas necesarias
os.makedirs("uploads", exist_ok=True)
os.makedirs("frontend", exist_ok=True)

# Inicializar DB
init_db()

# Crear app principal
app = FastAPI(title="CEMIC Autorizaciones")

# ✅ Incluir rutas de API
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(ref.router, prefix="/api/ref", tags=["ref"])
app.include_router(patients.router, prefix="/api/patients", tags=["patients"])

# ✅ Montar los archivos estáticos del frontend
app.mount("/files", StaticFiles(directory="uploads"), name="files")
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
