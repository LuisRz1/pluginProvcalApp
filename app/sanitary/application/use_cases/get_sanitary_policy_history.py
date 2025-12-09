from dataclasses import dataclass
from datetime import date, timedelta
from typing import Dict, Any, List
from uuid import UUID

from app.sanitary.application.ports.sanitary_policy_repository import (
    SanitaryPolicyRepository,
)
from app.sanitary.application.ports.sanitary_review_repository import (
    SanitaryReviewRepository,
)


@dataclass
class GetSanitaryPolicyHistoryCommand:
    """
    Comando para consultar el historial de una política de sanidad.

    Campos alineados con tus pantallas:
      - policy_id    -> política seleccionada (ej. 'Control de plagas')
      - months_back  -> periodo a mostrar en el historial:
                        6, 12, 24 meses (6m, 1 año, 2 años)
    """

    policy_id: UUID
    months_back: int  # 6, 12, 24, etc.


class GetSanitaryPolicyHistoryUseCase:
    """
    Caso de uso para obtener la información que se ve en la pantalla de detalle
    de una política:

      - Datos básicos de la política.
      - Historial de revisiones en un periodo (6m, 1 año, 2 años).
      - Fecha de la última revisión.
      - Próxima revisión (= última + 30 días) si existe alguna.

    *No añadimos ningún campo nuevo a la BD; todo se calcula a partir de las revisiones.*
    """

    def __init__(
        self,
        policy_repo: SanitaryPolicyRepository,
        review_repo: SanitaryReviewRepository,
    ) -> None:
        self._policy_repo = policy_repo
        self._review_repo = review_repo

    async def execute(self, cmd: GetSanitaryPolicyHistoryCommand) -> Dict[str, Any]:
        # 1) Validar que la política exista
        policy = await self._policy_repo.get_by_id(cmd.policy_id)
        if not policy:
            return {
                "success": False,
                "message": "La política de sanidad seleccionada no existe.",
                "policy": None,
                "history": [],
                "last_review_date": None,
                "next_review_date": None,
            }

        # 2) Calcular rango de fechas del historial
        today = date.today()

        # months_back lo convertimos a días aproximados (30 días por mes),
        # suficiente para el filtro de historial 6m, 1 año, 2 años.
        days_back = cmd.months_back * 30
        start_date = today - timedelta(days=days_back)
        end_date = today

        # 3) Obtener historial en ese rango
        reviews = await self._review_repo.list_by_policy_and_period(
            policy_id=cmd.policy_id,
            start_date=start_date,
            end_date=end_date,
        )

        # 4) Obtener última revisión (para calcular próxima)
        last_review = await self._review_repo.get_last_by_policy(cmd.policy_id)
        if last_review:
            last_review_date = last_review.date
            next_review_date = last_review_date + timedelta(days=30)
        else:
            last_review_date = None
            next_review_date = None

        # 5) Mapear historial a un formato simple para la UI
        history: List[Dict[str, Any]] = []
        for r in reviews:
            history.append(
                {
                    "id": str(r.id),
                    "date": r.date.isoformat(),
                    "is_conform": r.is_conform,
                    "observation": r.observation,
                    "incident_type_id": str(r.incident_type_id) if r.incident_type_id else None,
                    "company_id": str(r.company_id) if r.company_id else None,
                }
            )

        # 6) Armar respuesta
        return {
            "success": True,
            "message": "Historial de la política obtenido correctamente.",
            "policy": {
                "id": str(policy.id),
                "name": policy.name,
                "description": policy.description,
                "is_active": policy.is_active,
            },
            "history": history,
            "last_review_date": last_review_date.isoformat() if last_review_date else None,
            "next_review_date": next_review_date.isoformat() if next_review_date else None,
        }
