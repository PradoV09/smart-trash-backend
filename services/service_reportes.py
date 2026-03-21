from sqlalchemy.orm import Session
from models.model_reportes import ReporteActividad
from schemas.schema_reportes import ReporteCreate

def get_reportes(db: Session):
    return db.query(ReporteActividad).all()

def get_reporte_by_id(db: Session, id_registro: int):
    return db.query(ReporteActividad).filter(ReporteActividad.id_registro == id_registro).first()

def create_reporte(db: Session, reporte: ReporteCreate):
    db_reporte = ReporteActividad(
        id_usuario=reporte.id_usuario,
        u_gmail_cache=reporte.u_gmail_cache,
        descripcion=reporte.descripcion,
        asunto=reporte.asunto,
        evidencia_url=reporte.evidencia_url,
        u_rol_cache=reporte.u_rol_cache
    )
    db.add(db_reporte)
    db.commit()
    db.refresh(db_reporte)
    return db_reporte