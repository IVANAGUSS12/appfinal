# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.routes import patients, ref  # tus routers

app = FastAPI(
    title="CEMIC · Backend",
    description="API interna para panel, QR e importaciones",
    version="2.0.0",
)

# ------------ CORS ------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # restringí si querés a tu dominio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------ API ------------
app.include_router(patients.router)   # /api/patients/...
app.include_router(ref.router)        # /api/ref/...

# ------------ Health (para probes) ------------
@app.get("/health")
def health():
    return {"status": "ok"}

# ------------ Static (FRONTEND) ------------
# Asegurá que estas carpetas existan en el contenedor
os.makedirs("frontend", exist_ok=True)
os.makedirs("uploads", exist_ok=True)

# Archivos subidos (si usás previews/descargas)
app.mount("/files", StaticFiles(directory="uploads"), name="files")

# Frontend (HTML/CSS/JS). Debe ir AL FINAL para no tapar la API.
# Sirve todo lo que haya en /frontend en la raíz del sitio (/, /login.html, /qr.html, /admin/importar.html, etc.)
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

