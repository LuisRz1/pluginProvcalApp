from dataclasses import dataclass
from typing import Dict, Any, List

from app.sanitary.application.ports.sanitary_policy_repository import (
    SanitaryPolicyRepository,
)


@dataclass
class ListSanitaryPoliciesCommand:
    """
    Comando para listar políticas de sanidad.

    Por ahora no recibe filtros adicionales porque en tu E-R
    y pantallas sólo se ve un listado general de políticas activas.
    """
    include_inactive: bool = False


class ListSanitaryPoliciesUseCase:
    """
    Caso de uso para obtener la lista de políticas de sanidad.

    - Si include_inactive = False:
        devuelve sólo las activas (lo que ve el nutricionista).
    - Si include_inactive = True:
        devuelve todas (útil si luego quieres una pantalla de administración).
    """

    def __init__(self, policy_repo: SanitaryPolicyRepository) -> None:
        self._policy_repo = policy_repo

    async def execute(self, cmd: ListSanitaryPoliciesCommand) -> Dict[str, Any]:
        if cmd.include_inactive:
            policies = await self._policy_repo.list_all()
        else:
            policies = await self._policy_repo.list_active()

        items: List[Dict[str, Any]] = []
        for p in policies:
            items.append(
                {
                    "id": str(p.id),
                    "name": p.name,
                    "description": p.description,
                    "is_active": p.is_active,
                }
            )

        return {
            "success": True,
            "message": "Lista de políticas de sanidad obtenida correctamente.",
            "policies": items,
        }
