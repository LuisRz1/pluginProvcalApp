"""Estados y tipos de asistencia"""
from enum import Enum

class AttendanceStatus(Enum):
    """Estados de una jornada de asistencia"""
    IN_PROGRESS = "in_progress"  # Sesión activa
    ON_BREAK = "on_break"  # En descanso
    COMPLETED = "completed"  # Jornada completada
    INCOMPLETE = "incomplete"  # Falta marcar salida
    PENDING_REGULARIZATION = "pending_regularization"  # Requiere ajuste de RRHH

class AttendanceType(Enum):
    """Tipos de día de asistencia"""
    REGULAR = "regular"  # Día normal
    HOLIDAY = "holiday"  # Día festivo laborado
    OVERTIME = "overtime"  # Horas extra

class BreakStatus(Enum):
    """Estado de un período de descanso"""
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    EXCEEDED = "exceeded"  # Excedió tiempo permitido
