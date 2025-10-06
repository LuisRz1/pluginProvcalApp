"""Mutations GraphQL para asistencia"""
import strawberry
from strawberry.types import Info
from datetime import datetime

from app.attendance.infrastructure.graphql.attendance_inputs import (
    CheckInInput,
    CheckOutInput,
    StartBreakInput,
    EndBreakInput,
    RegularizeAttendanceInput
)
from app.attendance.infrastructure.graphql.attendance_types import (
    CheckInResponse,
    CheckOutResponse,
    RegularizeAttendanceResponse,
    StartBreakResponse,
    EndBreakResponse
)
from app.attendance.application.use_cases.check_in import (
    CheckInUseCase,
    CheckInCommand
)
from app.attendance.application.use_cases.check_out import (
    CheckOutUseCase,
    CheckOutCommand
)
from app.attendance.application.use_cases.start_break import (
    StartBreakUseCase,
    StartBreakCommand
)
from app.attendance.application.use_cases.end_break import (
    EndBreakUseCase,
    EndBreakCommand
)
from app.attendance.application.use_cases.regularize_attendance import (
    RegularizeAttendanceUseCase,
    RegularizeAttendanceCommand
)
from app.building_blocks.exceptions import DomainException, AuthenticationException


@strawberry.type
class AttendanceMutations:

    @strawberry.mutation
    async def check_in(
        self,
        info: Info,
        input: CheckInInput
    ) -> CheckInResponse:
        """
        Registra la entrada del empleado.
        Requiere autenticación.
        """
        try:
            # Verificar autenticación
            if not info.context.get("current_user"):
                raise AuthenticationException("Debes estar autenticado")

            user = info.context["current_user"]

            # Crear comando
            command = CheckInCommand(
                user_id=user.id,
                latitude=input.latitude,
                longitude=input.longitude,
                accuracy=input.accuracy,
                workplace_latitude=input.workplace_latitude,
                workplace_longitude=input.workplace_longitude,
                workplace_radius_meters=input.workplace_radius_meters
            )

            # Ejecutar caso de uso
            use_case = CheckInUseCase(
                attendance_repository=info.context["attendance_repository"],
                holiday_service=info.context["holiday_service"]
            )

            result = await use_case.execute(command)

            return CheckInResponse(
                success=True,
                message=result["message"],
                attendance_id=result["attendance_id"],
                check_in_time=datetime.fromisoformat(result["check_in_time"]),
                is_late=result["is_late"],
                late_minutes=result["late_minutes"],
                is_holiday=result["is_holiday"]
            )

        except (DomainException, AuthenticationException) as e:
            return CheckInResponse(
                success=False,
                message=str(e),
                attendance_id=None,
                check_in_time=None,
                is_late=False,
                late_minutes=0,
                is_holiday=False
            )

    @strawberry.mutation
    async def check_out(
        self,
        info: Info,
        input: CheckOutInput
    ) -> CheckOutResponse:
        """
        Registra la salida del empleado.
        Requiere autenticación.
        """
        try:
            if not info.context.get("current_user"):
                raise AuthenticationException("Debes estar autenticado")

            user = info.context["current_user"]

            command = CheckOutCommand(
                user_id=user.id,
                latitude=input.latitude,
                longitude=input.longitude,
                accuracy=input.accuracy
            )

            use_case = CheckOutUseCase(
                attendance_repository=info.context["attendance_repository"]
            )

            result = await use_case.execute(command)

            return CheckOutResponse(
                success=True,
                message=result["message"],
                attendance_id=result["attendance_id"],
                check_out_time=datetime.fromisoformat(result["check_out_time"]),
                total_work_hours=result["total_work_hours"],
                no_breaks_registered=result["no_breaks_registered"]
            )

        except (DomainException, AuthenticationException) as e:
            return CheckOutResponse(
                success=False,
                message=str(e),
                attendance_id="",
                check_out_time=datetime.now(),
                total_work_hours=0.0,
                no_breaks_registered=False
            )

    @strawberry.mutation
    async def start_break(
        self,
        info: Info,
        input: StartBreakInput
    ) -> StartBreakResponse:
        """
        Inicia un período de descanso.
        Requiere autenticación.
        """
        try:
            if not info.context.get("current_user"):
                raise AuthenticationException("Debes estar autenticado")

            user = info.context["current_user"]

            command = StartBreakCommand(
                user_id=user.id,
                latitude=input.latitude,
                longitude=input.longitude,
                accuracy=input.accuracy
            )

            use_case = StartBreakUseCase(
                attendance_repository=info.context["attendance_repository"]
            )

            result = await use_case.execute(command)

            return StartBreakResponse(
                success=True,
                message=result["message"],
                break_id=result["break_id"],
                start_time=datetime.fromisoformat(result["start_time"]),
                allowed_duration_minutes=result["allowed_duration_minutes"]
            )

        except (DomainException, AuthenticationException) as e:
            return StartBreakResponse(
                success=False,
                message=str(e),
                break_id=None,
                start_time=datetime.now(),
                allowed_duration_minutes=30
            )

    @strawberry.mutation
    async def end_break(
        self,
        info: Info,
        input: EndBreakInput
    ) -> EndBreakResponse:
        """
        Finaliza el período de descanso actual.
        Requiere autenticación.
        """
        try:
            if not info.context.get("current_user"):
                raise AuthenticationException("Debes estar autenticado")

            user = info.context["current_user"]

            command = EndBreakCommand(
                user_id=user.id,
                latitude=input.latitude,
                longitude=input.longitude,
                accuracy=input.accuracy
            )

            use_case = EndBreakUseCase(
                attendance_repository=info.context["attendance_repository"]
            )

            result = await use_case.execute(command)

            return EndBreakResponse(
                success=True,
                message=result["message"],
                end_time=datetime.fromisoformat(result["end_time"]),
                duration_minutes=result["duration_minutes"],
                is_exceeded=result["is_exceeded"]
            )

        except (DomainException, AuthenticationException) as e:
            return EndBreakResponse(
                success=False,
                message=str(e),
                end_time=datetime.now(),
                duration_minutes=0,
                is_exceeded=False
            )

    @strawberry.mutation
    async def regularize_attendance(
        self,
        info: Info,
        input: RegularizeAttendanceInput
    ) -> RegularizeAttendanceResponse:
        """
        Regulariza una asistencia (solo admin).
        Requiere autenticación y rol admin.
        """
        try:
            if not info.context.get("current_user"):
                raise AuthenticationException("Debes estar autenticado")

            user = info.context["current_user"]

            # Verificar que sea admin
            from app.users.domain.user_role import UserRole
            if user.role != UserRole.ADMIN:
                raise AuthenticationException("Solo administradores pueden regularizar asistencias")

            command = RegularizeAttendanceCommand(
                attendance_id=input.attendance_id,
                admin_id=user.id,
                notes=input.notes,
                adjusted_check_in=input.adjusted_check_in
            )

            use_case = RegularizeAttendanceUseCase(
                attendance_repository=info.context["attendance_repository"]
            )

            result = await use_case.execute(command)

            return RegularizeAttendanceResponse(
                success=True,
                message=result["message"]
            )

        except (DomainException, AuthenticationException) as e:
            return RegularizeAttendanceResponse(
                success=False,
                message=str(e)
            )