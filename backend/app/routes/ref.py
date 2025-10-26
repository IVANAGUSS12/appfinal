from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from bs4 import BeautifulSoup
from ..db import SessionLocal
from ..models.refdata import Medico, Cobertura, Sector
import csv, io
router = APIRouter(prefix="/api/ref", tags=["ref"])
def get_db():
    db=SessionLocal()
    try: yield db
    finally: db.close()
@router.get("/lists")
def get_lists(db: Session = Depends(get_db)):
    med=[m.nombre for m in db.query(Medico).order_by(Medico.nombre).all()]
    cob=[c.nombre for c in db.query(Cobertura).order_by(Cobertura.nombre).all()]
    sec=[{'codigo':s.codigo,'nombre':s.nombre} for s in db.query(Sector).order_by(Sector.nombre).all()]
    return {"medicos": med, "coberturas": cob, "sectores": sec}
def _norm(x: str) -> str:
    x=(x or "").strip().upper().replace(".","").replace("-"," ")
    return " ".join(x.split())
def _upsert(db, med:set, esp:set, obr:set):
    for n in sorted(filter(None, med)):
        if not db.query(Medico).filter(Medico.nombre==n).first(): db.add(Medico(nombre=n))
    for n in sorted(filter(None, obr)):
        if not db.query(Cobertura).filter(Cobertura.nombre==n).first(): db.add(Cobertura(nombre=n))
    for n in sorted(filter(None, esp)):
        code = n.lower().replace(' ','_')[:40]
        if not db.query(Sector).filter(Sector.codigo==code).first(): db.add(Sector(codigo=code, nombre=n))
    db.commit()
@router.post("/import/csv")
async def import_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    text = (await file.read())
    try: text = text.decode("utf-8")
    except UnicodeDecodeError: text = text.decode("latin-1", errors="ignore")
    reader = csv.DictReader(io.StringIO(text))
    med, esp, obr = set(), set(), set()
    for row in reader:
        med.add(_norm(row.get("cirujano")))
        esp.add(_norm(row.get("especialidad")))
        obr.add(_norm(row.get("obra_social")))
    _upsert(db, med, esp, obr)
    return {"ok": True, "medicos": len(med), "coberturas": len(obr), "sectores": len(esp)}
@router.post("/import/xls-html")
async def import_xls_html(file: UploadFile = File(...), db: Session = Depends(get_db)):
    raw = (await file.read()).decode("latin-1", errors="ignore")
    # El XLS de Excel puede ser frameset; buscamos cualquier <table> y los headers Cirujano/Especialidad/Obra Social
    soup = BeautifulSoup(raw, "lxml")
    med, esp, obr = set(), set(), set()
    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        if not rows: continue
        headers = [ (th.get_text(strip=True) or "").lower() for th in rows[0].find_all(["td","th"]) ]
        # mapear indices
        idx_c = next((i for i,h in enumerate(headers) if "ciruj" in h or "médico" in h or "medico" in h), None)
        idx_e = next((i for i,h in enumerate(headers) if "especial" in h or "sector" in h or "servicio" in h), None)
        idx_o = next((i for i,h in enumerate(headers) if "obra" in h and "social" in h or "cobertura" in h), None)
        if idx_c is None and idx_e is None and idx_o is None: continue
        for tr in rows[1:]:
            cols = tr.find_all(["td","th"])
            if idx_c is not None and idx_c < len(cols): med.add(_norm(cols[idx_c].get_text(strip=True)))
            if idx_e is not None and idx_e < len(cols): esp.add(_norm(cols[idx_e].get_text(strip=True)))
            if idx_o is not None and idx_o < len(cols): obr.add(_norm(cols[idx_o].get_text(strip=True)))
    _upsert(db, med, esp, obr)
    return {"ok": True, "medicos": len(med), "coberturas": len(obr), "sectores": len(esp)}
@router.post("/import/xls")
async def import_xls(file: UploadFile = File(...), db: Session = Depends(get_db)):
    import pandas as pd, io, unicodedata
    content = await file.read()
    try:
        df = pd.read_excel(io.BytesIO(content))  # openpyxl
    except Exception as e:
        return {"ok": False, "detail": f"No se pudo leer Excel: {e}"}

    # normalizar cabeceras
    df.columns = [unicodedata.normalize('NFKD', str(c)).encode('ascii','ignore').decode().strip().lower()
                  for c in df.columns]

    def pick(*cands):
        for c in cands:
            if c in df.columns: return c
        return None

    col_cir = pick('cirujano','medico','cirugia','cirujano/a')
    col_esp = pick('especialidad','sector')
    col_obs = pick('obra_social','cobertura','os')

    if not all([col_cir, col_esp, col_obs]):
        return {"ok": False, "detail": "Faltan columnas: cirujano / especialidad / obra_social"}

    def clean(s):
        s = str(s).strip()
        return s if s and s.lower() not in ('nan','none','null') else ''

    meds = { clean(x) for x in df[col_cir].dropna().astype(str) }
    esps = { clean(x) for x in df[col_esp].dropna().astype(str) }
    obras = { clean(x) for x in df[col_obs].dropna().astype(str) }
    meds.discard(''); esps.discard(''); obras.discard('')

    # usa tus funciones/helpers actuales de guardado/dedup
    # asumimos existen: save_reference_sets(db, medicos=set(), especialidades=set(), coberturas=set())
    from .ref import save_reference_sets as _save
    added = _save(db, medicos=meds, especialidades=esps, coberturas=obras)
    return {"ok": True, **added}
