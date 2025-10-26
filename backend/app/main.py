# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import patients, ref

# --------------------------
# Inicialización principal
# --------------------------
app = FastAPI(
    title="CEMIC · Backend",
    description="API interna para panel, QR e importaciones",
    version="2.0.0"
)

# --------------------------
# Configuración de CORS
# --------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # podés restringir luego a tus dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------
# Rutas principales
# --------------------------
app.include_router(patients.router)
app.include_router(ref.router)

# --------------------------
# Ruta raíz (ping test)
# --------------------------
@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "API CEMIC corriendo correctamente",
        "routes": ["/api/patients", "/api/ref"]
    }
