from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from .db import init_db
from .routes import auth, ref, patients

os.makedirs("uploads", exist_ok=True)
os.makedirs("frontend", exist_ok=True)

init_db()
app = FastAPI(title="CEMIC Autorizaciones")

# Routers ya tienen prefix por dentro → no repetir
app.include_router(auth.router)
app.include_router(ref.router)
app.include_router(patients.router)

# Static al final
app.mount("/files", StaticFiles(directory="uploads"), name="files")
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
