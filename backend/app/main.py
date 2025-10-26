from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

from .db import init_db
from .routes import auth, ref, patients  # routers ya traen sus propios prefix

# asegurar carpetas
os.makedirs("uploads", exist_ok=True)
os.makedirs("frontend", exist_ok=True)

init_db()

app = FastAPI(title="CEMIC Autorizaciones")

# ✅ incluir routers SIN prefix adicional
app.include_router(auth.router)
app.include_router(ref.router)
app.include_router(patients.router)

# ✅ montar estáticos al final
app.mount("/files", StaticFiles(directory="uploads"), name="files")
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
