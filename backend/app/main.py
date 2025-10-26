from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .db import init_db
from .routes import auth, ref
from .routes import patients
init_db()
app = FastAPI(title="Autorizaciones")
app.mount("/files", StaticFiles(directory="uploads"), name="files")
app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")
app.include_router(auth.router)
app.include_router(ref.router)
app.include_router(patients.router)
