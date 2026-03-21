from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config.connection import get_db
from schemas.schema_reportes import ReporteCreate, ResponseReporte
from services.service_reportes import get_reportes, get_reporte_by_id, create_reporte

router = APIRouter(prefix="/reportes", tags=["Reportes"])

@router.get("/", response_model=list[ResponseReporte])
def list_reportes(db: Session = Depends(get_db)):
    return get_reportes(db)

@router.get("/{id_registro}", response_model=ResponseReporte)
def get_reporte(id_registro: int, db: Session = Depends(get_db)):
    reporte = get_reporte_by_id(db, id_registro)
    if not reporte:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    return reporte

@router.post("/", response_model=ResponseReporte, status_code=201)
def add_reporte(reporte: ReporteCreate, db: Session = Depends(get_db)):
    try:
        return create_reporte(db, reporte)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))