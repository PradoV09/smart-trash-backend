"""Controlador para reportes públicos de ciudadanos.

Permite a usuarios no autenticados reportar problemas de recolección de basura.
"""

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependecies import get_db
from core.response_builders import success_response
from schemas.schema_reportes_publico import ReportePublicoCreate, ReportePublicoResponse
from schemas.schema_reportes import ReporteCreate
from services.service_reportes import ReporteService
import logging

logger = logging.getLogger(__name__)

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
    try:
        # Procesar Base64 a archivo si es necesario
        final_url = data.evidencia_url
        if final_url and final_url.startswith("data:image"):
            import base64
            import os
            import uuid
            
            try:
                header, encoded = final_url.split(",", 1)
                ext = header.split(";")[0].split("/")[1]
                if ext == "jpeg": ext = "jpg"
                
                file_name = f"public_report_{uuid.uuid4().hex}.{ext}"
                file_path = os.path.join("uploads", "fotos", file_name)
                
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, "wb") as f:
                    f.write(base64.b64decode(encoded))
                    
                final_url = f"/uploads/fotos/{file_name}"
            except Exception as ex:
                logger.error(f"Error procesando imagen base64: {ex}")
                final_url = None

        # Convertir a ReporteCreate interno
        reporte_data = ReporteCreate(
            id_usuario=None,  # No está autenticado
            u_gmail_cache=data.correo,  # Guardamos el correo para contacto
            u_rol_cache="ciudadano",  # Marcamos como reporte de ciudadano
            descripcion=f"[{data.nombre}] {data.descripcion}",  # Incluimos nombre en descripción
            asunto=data.asunto,
            evidencia_url=final_url,
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
    except Exception as e:
        logger.error(f"Error al crear reporte público: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al enviar el reporte. Por favor intente más tarde."
        )
