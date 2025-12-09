from dataclasses import dataclass
from datetime import date
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class SanitaryReview:
    """
    Revisión/inspección de una política de sanidad.

    Equivale a la entidad RevisionSanidad del E-R:
      - revision_id
      - politica_id
      - tipo_incidencia_id
      - usuario_id
      - empresa_id
      - fecha
      - es_conforme
      - observacion

    Notas de dominio (según tus pantallas):
      - Si es_conforme = True:
          * tipo_incidencia_id y empresa_id normalmente quedan en None.
      - Si es_conforme = False:
          * tipo_incidencia_id y empresa_id deben venir informados.
          * empresa_id es la empresa ESPECIALIZADA a contactar,
            no la sede del cliente.
    """

    id: UUID                      # revision_id
    policy_id: UUID               # politica_id
    user_id: UUID                 # usuario_id (nutricionista que realiza la revisión)
    date: date                    # fecha
    is_conform: bool              # es_conforme
    observation: Optional[str]    # observacion

    incident_type_id: Optional[UUID] = None   # tipo_incidencia_id
    company_id: Optional[UUID] = None         # empresa_id (servicio especializado)

    # --------- Fábricas de conveniencia ---------

    @classmethod
    def create_conform(
        cls,
        policy_id: UUID,
        user_id: UUID,
        date_value: date,
        observation: Optional[str] = None,
    ) -> "SanitaryReview":
        """
        Crea una revisión conforme (sin incidencia).
        """
        return cls(
            id=uuid4(),
            policy_id=policy_id,
            user_id=user_id,
            date=date_value,
            is_conform=True,
            observation=observation,
            incident_type_id=None,
            company_id=None,
        )

    @classmethod
    def create_non_conform(
        cls,
        policy_id: UUID,
        user_id: UUID,
        date_value: date,
        incident_type_id: UUID,
        company_id: UUID,
        observation: Optional[str] = None,
    ) -> "SanitaryReview":
        """
        Crea una revisión inconforme (con incidencia y empresa a contactar).
        """
        return cls(
            id=uuid4(),
            policy_id=policy_id,
            user_id=user_id,
            date=date_value,
            is_conform=False,
            observation=observation,
            incident_type_id=incident_type_id,
            company_id=company_id,
        )
