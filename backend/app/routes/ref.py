# backend/app/routes/ref.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import ref as models

router = APIRouter(prefix="/api/ref", tags=["ref"])

# -------- Helpers --------
def _norm(s: str) -> str:
    s = (s or "").strip()
    return s if s and s.lower() not in ("nan", "none", "null") else ""

def _upsert_text_set(db: Session, Model, field: str, values: set[str]) -> int:
    """Inserta valores únicos (ignora existentes). Devuelve cantidad insertada."""
    if not values:
        return 0
    existing = {getattr(r, field) for r in db.query(Model).all()}
    inserted = 0
    for v in values:
        if not v or v in existing:
            continue
        db.add(Model(**{field: v}))
        inserted += 1
    db.commit()
    return inserted

# -------- API: listas --------
@router.get("/lists")
def lists(db: Session = Depends(get_db)):
    """
    Devuelve las listas maestras para QR/menú:
    {
      "medicos": ["A", "B", ...],
      "coberturas": ["OSDE", "Swiss", ...],
      "sectores": [{"codigo":"TRAUMA","nombre":"Traumatología"}, ...]
    }
    """
    medicos = [r.nombre for r in db.query(models.RefMedico).order_by(models.RefMedico.nombre).all()]
    coberturas = [r.nombre for r in db.query(models.RefCobertura).order_by(models.RefCobertura.nombre).all()]

    sectores = []
    for s in db.query(models.RefSector).all():
        codigo = getattr(s, "codigo", None)
        nombre = getattr(s, "nombre", None) or getattr(s, "descripcion", None) or ""
        if codigo:
            sectores.append({"codigo": codigo, "nombre": nombre or codigo})
        else:
            sectores.append({"codigo": nombre, "nombre": nombre})

    return {"medicos": medicos, "coberturas": coberturas, "sectores": sectores}


# -------- API: import CSV --------
@router.post("/import/csv")
async def import_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    CSV con cabeceras: cirujano, especialidad, obra_social
    (o variantes: medico, sector, cobertura, os)
    """
    import csv, io

    raw = await file.read()
    try:
        txt = raw.decode("utf-8-sig")
    except Exception:
        txt = raw.decode("latin-1")

    reader = csv.DictReader(io.StringIO(txt))
    scanned = 0
    meds, esps, obras = set(), set(), set()
    samples = {"cirujano": [], "especialidad": [], "obra_social": []}

    for row in reader:
        scanned += 1
        cir = _norm(row.get("cirujano") or row.get("medico") or row.get("cirugia"))
        esp = _norm(row.get("especialidad") or row.get("sector"))
        obs = _norm(row.get("obra_social") or row.get("cobertura") or row.get("os"))

        if cir:
            meds.add(cir)
            if len(samples["cirujano"]) < 5:
                samples["cirujano"].append(cir)
        if esp:
            esps.add(esp)
            if len(samples["especialidad"]) < 5:
                samples["especialidad"].append(esp)
        if obs:
            obras.add(obs)
            if len(samples["obra_social"]) < 5:
                samples["obra_social"].append(obs)

    m = _upsert_text_set(db, models.RefMedico, "nombre", meds)
    c = _upsert_text_set(db, models.RefCobertura, "nombre", obras)
    s = _upsert_text_set(db, models.RefSector, "nombre", esps)

    return {
        "ok": True,
        "scanned": scanned,
        "parsed": {"medicos": len(meds), "coberturas": len(obras), "sectores": len(esps)},
        "inserted": {"medicos": m, "coberturas": c, "sectores": s},
        "samples": samples,
    }


# -------- API: debug --------
@router.get("/debug")
def debug_ref(db: Session = Depends(get_db)):
    meds = db.query(models.RefMedico).all()
    obras = db.query(models.RefCobertura).all()
    sects = db.query(models.RefSector).all()

    def to_name(x):
        return getattr(x, "nombre", None) or getattr(x, "descripcion", None) or ""

    return {
        "counts": {
            "medicos": len(meds),
            "coberturas": len(obras),
            "sectores": len(sects),
        },
        "samples": {
            "medicos": [to_name(m) for m in meds[:10]],
            "coberturas": [to_name(o) for o in obras[:10]],
            "sectores": [
                {
                    "codigo": getattr(s, "codigo", None) or to_name(s),
                    "nombre": to_name(s) or getattr(s, "codigo", None),
                }
                for s in sects[:10]
            ],
        },
    }
