# services/service_tripulacionasignada.py

"""Servicios del módulo de tripulación.

Se encarga de agregar integrantes, confirmar su participación y retirarlos
cuando la asignación todavía está en estado pendiente.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from datetime import datetime, timezone

from models.model_asignacionrutas import AsignacionRutas, EstadoAsignacion
from models.model_tripulacion import Tripulacion, TripulacionMiembro
from models.model_usuarios import Usuario
from schemas.schema_asignaciontripulacion import TripulacionCreate
from core.websocket_manager import ws_manager


class TripulacionService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def _verificar_asignacion_pendiente(self, id_asignacion: int) -> AsignacionRutas:
        """Asegura que la asignación exista y aún pueda modificarse."""
        result = await self.db.execute(
            select(AsignacionRutas).where(
                AsignacionRutas.id_asignacion == id_asignacion
            )
        )
        asignacion = result.scalar_one_or_none()
        if not asignacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró la asignación {id_asignacion}.",
            )
        if asignacion.estado != EstadoAsignacion.pendiente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La asignación {id_asignacion} no está pendiente; no se puede modificar su tripulación.",
            )
        return asignacion

    async def _obtener_o_crear_equipo(self, asignacion: AsignacionRutas) -> Tripulacion:
        """Obtiene el equipo asociado a la asignación o crea uno nuevo si no existe."""
        if asignacion.id_tripulacion:
            result = await self.db.execute(
                select(Tripulacion).where(Tripulacion.id_tripulacion == asignacion.id_tripulacion)
            )
            return result.scalar_one()
        
        nuevo_equipo = Tripulacion(nombre=f"Equipo Asignación {asignacion.id_asignacion}")
        self.db.add(nuevo_equipo)
        await self.db.flush()
        
        asignacion.id_tripulacion = nuevo_equipo.id_tripulacion
        await self.db.flush()
        return nuevo_equipo

    async def agregar_miembro(self, id_asignacion: int, data: TripulacionCreate) -> TripulacionMiembro:
        """Agrega un integrante nuevo a la tripulación del equipo de la asignación."""
        asignacion = await self._verificar_asignacion_pendiente(id_asignacion)
        equipo = await self._obtener_o_crear_equipo(asignacion)

        # Obtener miembros actuales del equipo
        tripulacion_actual = await self.obtener_tripulacion_asignacion(id_asignacion)

        if len(tripulacion_actual) >= 4:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La tripulación ya está completa (máximo 4 personas)."
            )

        if any(m.id_usuario == data.id_usuario for m in tripulacion_actual):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El usuario {data.id_usuario} ya pertenece a esta tripulación."
            )

        rol_valor = data.rol_tripulacion.value if hasattr(data.rol_tripulacion, 'value') else str(data.rol_tripulacion)
        
        if rol_valor == "conductor":
            if any(m.rol_tripulacion.value == "conductor" for m in tripulacion_actual):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe un conductor asignado."
                )
        elif rol_valor == "recolector":
            count_recolectores = sum(1 for m in tripulacion_actual if m.rol_tripulacion.value == "recolector")
            if count_recolectores >= 3:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya se han asignado los 3 recolectores."
                )

        miembro = TripulacionMiembro(
            id_tripulacion=equipo.id_tripulacion,
            id_usuario=data.id_usuario,
            rol_tripulacion=data.rol_tripulacion,
        )
        self.db.add(miembro)
        await self.db.flush()
        
        # Cargar usuario y sus relaciones para la respuesta
        result = await self.db.execute(
            select(TripulacionMiembro)
            .options(
                selectinload(TripulacionMiembro.usuario).selectinload(Usuario.perfil),
                selectinload(TripulacionMiembro.usuario).selectinload(Usuario.rol)
            )
            .where(TripulacionMiembro.id == miembro.id)
        )
        miembro_cargado = result.scalar_one()
        
        # Inyectar id_asignacion para compatibilidad con el esquema de respuesta
        setattr(miembro_cargado, 'id_asignacion', id_asignacion)
        return miembro_cargado

    async def confirmar_asignacion(self, id_asignacion: int, id_usuario: int) -> TripulacionMiembro:
        """Marca la participación del integrante como confirmada."""
        asignacion = await self.db.get(AsignacionRutas, id_asignacion)
        if not asignacion or not asignacion.id_tripulacion:
             raise HTTPException(status_code=404, detail="Asignación o equipo no encontrado.")

        result = await self.db.execute(
            select(TripulacionMiembro).where(
                TripulacionMiembro.id_tripulacion == asignacion.id_tripulacion,
                TripulacionMiembro.id_usuario     == id_usuario,
            )
        )
        miembro = result.scalar_one_or_none()
        if not miembro:
            raise HTTPException(status_code=404, detail="Usuario no encontrado en la tripulación.")

        if miembro.confirmado:
            raise HTTPException(status_code=400, detail="Ya confirmado.")

        miembro.confirmado    = True
        miembro.confirmado_at = datetime.now(timezone.utc)
        await self.db.flush()

        await ws_manager.broadcast(id_asignacion, {
            "evento":        "tripulacion_confirmo",
            "id_asignacion": id_asignacion,
            "id_usuario":    id_usuario,
            "rol":           miembro.rol_tripulacion.value,
        })
        
        # Recargar con relaciones para la respuesta
        result = await self.db.execute(
            select(TripulacionMiembro)
            .options(
                selectinload(TripulacionMiembro.usuario).selectinload(Usuario.perfil),
                selectinload(TripulacionMiembro.usuario).selectinload(Usuario.rol)
            )
            .where(TripulacionMiembro.id == miembro.id)
        )
        miembro_cargado = result.scalar_one()
        setattr(miembro_cargado, 'id_asignacion', id_asignacion)
        return miembro_cargado

    async def eliminar_miembro_asignacion(self, id_asignacion: int, id_usuario: int):
        """Elimina un miembro de la tripulación."""
        asignacion = await self._verificar_asignacion_pendiente(id_asignacion)
        if not asignacion.id_tripulacion:
             raise HTTPException(status_code=404, detail="No hay equipo asignado.")

        result = await self.db.execute(
            select(TripulacionMiembro).where(
                TripulacionMiembro.id_tripulacion == asignacion.id_tripulacion,
                TripulacionMiembro.id_usuario     == id_usuario
            )
        )
        miembro = result.scalar_one_or_none()
        if not miembro:
            raise HTTPException(status_code=404, detail="Miembro no encontrado.")

        await self.db.delete(miembro)
        await self.db.flush()

    async def obtener_todas_tripulaciones(self) -> list[TripulacionMiembro]:
        """Obtiene todos los miembros de tripulación del sistema."""
        # Nota: En el nuevo modelo, los miembros están en grupos. 
        # Si queremos "todas", listamos todos los TripulacionMiembro.
        result = await self.db.execute(
            select(TripulacionMiembro)
            .options(
                selectinload(TripulacionMiembro.usuario).selectinload(Usuario.rol),
                selectinload(TripulacionMiembro.usuario).selectinload(Usuario.perfil)
            )
        )
        miembros = list(result.scalars().all())
        # Inyectar id_asignacion es difícil aquí sin un join complejo, 
        # pero para el listado global quizás no sea crítico o se use id_tripulacion.
        return miembros

    async def obtener_tripulacion_asignacion(self, id_asignacion: int) -> list[TripulacionMiembro]:
        """Obtiene los miembros de la tripulación de una asignación específica."""
        result = await self.db.execute(
            select(AsignacionRutas).where(AsignacionRutas.id_asignacion == id_asignacion)
        )
        asignacion = result.scalar_one_or_none()
        if not asignacion or not asignacion.id_tripulacion:
            return []

        result = await self.db.execute(
            select(TripulacionMiembro)
            .options(
                selectinload(TripulacionMiembro.usuario).selectinload(Usuario.rol),
                selectinload(TripulacionMiembro.usuario).selectinload(Usuario.perfil)
            )
            .where(TripulacionMiembro.id_tripulacion == asignacion.id_tripulacion)
        )
        miembros = list(result.scalars().all())
        for m in miembros:
            setattr(m, 'id_asignacion', id_asignacion)
        return miembros
