from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

# asegurar carpetas al arrancar
os.makedirs("uploads", exist_ok=True)
os.makedirs("frontend", exist_ok=True)

from .db import init_db
from .routes import auth, ref, patients

init_db()

app = FastAPI(title="Autorizaciones")

# ahora montamos rutas internas en /app
app.mount("/files", StaticFiles(directory="uploads"), name="files")
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

app.include_router(auth.router)
app.include_router(ref.router)
app.include_router(patients.router)
