from fastapi import APIRouter, Depends, Form, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from ..db import SessionLocal
from ..models.patient import Patient
from ..models.attachment import Attachment
from ..utils import now_str
import os
router = APIRouter(prefix="/api", tags=["patients"])
def get_db():
    db=SessionLocal()
    try: yield db
    finally: db.close()
@router.get("/patients")
def list_patients(q: str = "", cobertura: str = "", medico: str = "", estado: str = "", sector_code: str = "", page: int = 1, pageSize: int = 50, db: Session = Depends(get_db)):
    query = db.query(Patient)
    if q:
        k=f"%{q}%"; query=query.filter((Patient.nombre.ilike(k)) | (Patient.dni.ilike(k)) | (Patient.cobertura.ilike(k)) | (Patient.medico.ilike(k)))
    if cobertura: query=query.filter(Patient.cobertura==cobertura)
    if medico:    query=query.filter(Patient.medico==medico)
    if estado:    query=query.filter(Patient.estado==estado)
    if sector_code: query=query.filter(Patient.sector_code==sector_code)
    total = query.count()
    rows = query.offset((page-1)*pageSize).limit(pageSize).all()
    def to_row(p):
        return {"_row": p.id, "nombre": p.nombre, "dni": p.dni, "email": p.email, "telefono": p.telefono, "cobertura": p.cobertura, "medico": p.medico, "sector_code": p.sector_code, "fecha_cx": p.fecha_cx or "", "estado": p.estado or "Pendiente", "presupuesto": p.presupuesto or "", "fecha_carga": p.fecha_carga, "subcarpeta_url": p.subcarpeta_url or "", "reprogramacion": p.reprogramacion or "", "observaciones_reprogramacion": p.observaciones_reprogramacion or "", "obs_proveedores": p.obs_proveedores or ""}
    return {"ok": True, "total": total, "rows": [to_row(p) for p in rows]}
@router.post("/patients")
async def create_patient(
    nombre: str = Form(...), dni: str = Form(...), email: str = Form(""), telefono: str = Form(""),
    cobertura: str = Form(""), medico: str = Form(""), sector_code: str = Form(""), fecha_cx: str = Form(""),
    observaciones: str = Form(""),
    orden_medica: UploadFile = File(...), dni_file: UploadFile = File(...), credencial: UploadFile = File(...), orden_materiales: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    p = Patient(nombre=nombre,dni=dni,email=email,telefono=telefono,cobertura=cobertura,medico=medico,sector_code=sector_code,fecha_cx=fecha_cx,fecha_carga=now_str(),estado="Pendiente")
    db.add(p); db.commit(); db.refresh(p)
    up_dir=os.path.abspath(os.path.join(os.path.dirname(__file__),"..","..","uploads")); os.makedirs(up_dir, exist_ok=True)
    async def save(up):
        data=await up.read()
        path=os.path.join(up_dir, f"{p.id}_{up.filename}")
        open(path,"wb").write(data)
        return "/files/"+os.path.basename(path)
    files=[("Orden",orden_medica),("DNI",dni_file),("Credencial",credencial)]
    if orden_materiales is not None: files.append(("Materiales",orden_materiales))
    for kind, up in files:
        url=await save(up); db.add(Attachment(patient_id=p.id, kind=kind, filename=up.filename, url=url, preview_url=url))
    db.commit()
    return {"ok": True, "patient_id": p.id}
@router.patch("/patients/{pid}")
def update_patient(pid: int, patch: dict, db: Session = Depends(get_db)):
    p=db.get(Patient, pid)
    if not p: raise HTTPException(404, "Paciente no encontrado")
    for k,v in patch.items():
        if hasattr(p,k): setattr(p, k, v or "")
    db.commit(); return {"ok": True}
@router.get("/calendar-month")
def calendar_month(desde: str, hasta: str, db: Session = Depends(get_db)):
    rows = db.query(Patient).all()
    from collections import Counter
    counts = Counter([p.fecha_cx for p in rows if p.fecha_cx])
    return {"events": [{"start":k,"count":v} for k,v in counts.items()]}
@router.get("/calendar-day")
def calendar_day(fechaExacta: str, db: Session = Depends(get_db)):
    rows = db.query(Patient).filter(Patient.fecha_cx==fechaExacta).all()
    def to_row(p):
        return {"_row": p.id, "nombre": p.nombre, "dni": p.dni, "email": p.email, "telefono": p.telefono, "cobertura": p.cobertura, "medico": p.medico, "sector_code": p.sector_code, "fecha_cx": p.fecha_cx or "", "estado": p.estado or "Pendiente", "presupuesto": p.presupuesto or "", "fecha_carga": p.fecha_carga}
    return {"total": len(rows), "rows": [to_row(p) for p in rows]}
@router.get("/stats")
def stats(q: str = "", cobertura: str = "", medico: str = "", estado: str = "", db: Session = Depends(get_db)):
    def filt(p: Patient) -> bool:
        ok=True
        if q: k=q.lower(); ok = ok and (k in (p.nombre or '').lower() or k in (p.dni or '').lower())
        if cobertura: ok = ok and p.cobertura==cobertura
        if medico: ok = ok and p.medico==medico
        if estado: ok = ok and p.estado==estado
        return ok
    rows = [p for p in db.query(Patient).all() if filt(p)]
    from collections import Counter
    by=lambda k: dict(Counter([getattr(p,k) or "" for p in rows]))
    return {"estado": by("estado"), "cobertura": by("cobertura"), "medico": by("medico")}
@router.get("/patients/{pid}/attachments")
def list_attachments(pid: int, db: Session = Depends(get_db)):
  from ..models.attachment import Attachment
  files = db.query(Attachment).where(Attachment.patient_id == pid).all()
  out = []
  for f in files:
      out.append({
          "id": f.id,
          "name": f.filename,
          "kind": f.kind,
          "previewUrl": f.preview_url or f.url,
          "downloadUrl": f.url,
      })
  return {"files": out}

