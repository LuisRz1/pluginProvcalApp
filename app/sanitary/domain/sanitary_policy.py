from dataclasses import dataclass
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class SanitaryPolicy:
    """
    Política de sanidad que se evalúa periódicamente.
    Equivale a la entidad PoliticaSanidad del E-R:
      - politica_id
      - nombre
      - descripcion
      - esta_activa
    """

    id: UUID          # politica_id
    name: str         # nombre
    description: Optional[str]  # descripcion
    is_active: bool   # esta_activa

    @classmethod
    def create(
        cls,
        name: str,
        description: Optional[str] = None,
        is_active: bool = True,
    ) -> "SanitaryPolicy":
        return cls(
            id=uuid4(),
            name=name,
            description=description,
            is_active=is_active,
        )

    def rename(self, new_name: str) -> None:
        self.name = new_name

    def change_description(self, new_description: Optional[str]) -> None:
        self.description = new_description

    def activate(self) -> None:
        self.is_active = True

    def deactivate(self) -> None:
        self.is_active = False
