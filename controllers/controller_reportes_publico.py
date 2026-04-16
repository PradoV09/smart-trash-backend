"""Controlador para reportes públicos de ciudadanos.

Permite a usuarios no autenticados reportar problemas de recolección de basura.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependecies import get_db
from core.response_builders import success_response
from schemas.schema_reportes_publico import ReportePublicoCreate, ReportePublicoResponse
from schemas.schema_reportes import ReporteCreate
from services.service_reportes import ReporteService


async def crear_reporte_publico(
    data: ReportePublicoCreate = Depends(ReportePublicoCreate.as_form),
    db: AsyncSession = Depends(get_db),
) -> ReportePublicoResponse:
    """Crea un reporte público de ciudadano sobre problemas de recolección.
    
    No requiere autenticación. Los ciudadanos pueden reportar:
    - Camiones que no pasaron
    - Basura acumulada
    - Problemas con horarios
    - Otros incidentes
    """
    # Convertir a ReporteCreate interno
    reporte_data = ReporteCreate(
        id_usuario=None,  # No está autenticado
        u_gmail_cache=data.correo,  # Guardamos el correo para contacto
        u_rol_cache="ciudadano",  # Marcamos como reporte de ciudadano
        descripcion=f"[{data.nombre}] {data.descripcion}",  # Incluimos nombre en descripción
        asunto=data.asunto,
        evidencia_url=data.evidencia_url,
    )
    
    reporte = await ReporteService(db).registrar_reporte(reporte_data)
    
    # Convertir respuesta a formato público
    response_data = ReportePublicoResponse(
        id_registro=reporte.id_registro,
        nombre=data.nombre,
        correo=data.correo,
        descripcion=data.descripcion,
        asunto=reporte.asunto,
        evidencia_url=reporte.evidencia_url,
        fecha=reporte.fecha,
    )
    
    return success_response(
        data=response_data,
        message="Reporte enviado exitosamente. Gracias por tu colaboración!"
    )
