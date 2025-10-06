"""Caso de uso: Regularizar asistencia (Admin)"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from app.attendance.application.ports.attendance_repository import AttendanceRepository
from app.building_blocks.exceptions import DomainException

@dataclass
class RegularizeAttendanceCommand:
    attendance_id: str
    admin_id: str
    notes: str
    adjusted_check_in: Optional[datetime] = None

class RegularizeAttendanceUseCase:
    """
    Caso de uso: Regularizar asistencia (solo admin).

    Escenarios:
    - Olvido de marcar entrada (admin ajusta hora)
    - Olvido de marcar salida (admin cierra jornada)
    """

    def __init__(self, attendance_repository: AttendanceRepository):
        self.attendance_repository = attendance_repository

    async def execute(self, command: RegularizeAttendanceCommand) -> dict:
        # 1. Obtener asistencia
        attendance = await self.attendance_repository.find_by_id(command.attendance_id)

        if not attendance:
            raise DomainException("Asistencia no encontrada")

        # 2. Regularizar
        attendance.regularize(
            admin_id=command.admin_id,
            notes=command.notes,
            adjusted_check_in=command.adjusted_check_in
        )

        # 3. Guardar
        await self.attendance_repository.save(attendance)

        # 4. Respuesta
        return {
            "attendance_id": attendance.id,
            "regularized_by": attendance.regularized_by,
            "regularized_at": attendance.regularized_at.isoformat(),
            "notes": attendance.regularization_notes,
            "message": "Asistencia regularizada exitosamente"
        }