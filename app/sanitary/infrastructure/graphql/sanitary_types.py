import datetime
import strawberry
from typing import Optional, List


# =========================
# Tipos básicos
# =========================

@strawberry.type
class SanitaryPolicyType:
    """
    Política de sanidad (PoliticaSanidad).
    Se usa para el listado de políticas y el encabezado del detalle.
    """

    id: strawberry.ID
    name: str
    description: Optional[str]
    is_active: bool


@strawberry.type
class SanitaryCompanyType:
    """
    Empresa especializada de sanidad (Empresa).
    Se muestra cuando la revisión es INCONFORME.
    """

    id: strawberry.ID
    business_name: str
    ruc: str
    phone: Optional[str]
    email: Optional[str]


@strawberry.type
class IncidentTypeType:
    """
    Tipo de incidencia (TipoIncidencia) asociado a una política.
    Se usa para poblar el combo 'Tipo de incidencia'.
    """

    id: strawberry.ID
    policy_id: strawberry.ID
    name: str
    description: Optional[str]
    is_active: bool


@strawberry.type
class SanitaryReviewType:
    """
    Revisión de sanidad (RevisionSanidad).
    Se usa en el historial y como resultado de la mutation de registro.
    """

    id: strawberry.ID
    policy_id: strawberry.ID
    user_id: strawberry.ID
    date: datetime.date
    is_conform: bool
    observation: Optional[str]
    incident_type_id: Optional[strawberry.ID]
    company_id: Optional[strawberry.ID]


# =========================
# Inputs
# =========================

@strawberry.input
class RegisterSanitaryReviewInput:
    """
    Input para registrar una revisión de sanidad.

    Campos alineados con:
      - E-R (RevisionSanidad)
      - Tus pantallas (Conforme/Inconforme).
    """

    policy_id: strawberry.ID
    date: datetime.date
    is_conform: bool
    observation: Optional[str] = None
    incident_type_id: Optional[strawberry.ID] = None
    company_id: Optional[strawberry.ID] = None


@strawberry.input
class SanitaryPolicyHistoryFilterInput:
    """
    Filtro para obtener el historial de una política.

    months_back: 6, 12, 24 (6 meses, 1 año, 2 años)
    """

    policy_id: strawberry.ID
    months_back: int  # 6, 12, 24, etc.


# =========================
# Respuestas (payloads)
# =========================

@strawberry.type
class SanitaryPoliciesResponse:
    success: bool
    message: str
    policies: List[SanitaryPolicyType]


@strawberry.type
class SanitaryPolicyHistoryResponse:
    success: bool
    message: str
    policy: Optional[SanitaryPolicyType]
    history: List[SanitaryReviewType]
    last_review_date: Optional[datetime.date]
    next_review_date: Optional[datetime.date]


@strawberry.type
class RegisterSanitaryReviewResponse:
    success: bool
    message: str
    review: Optional[SanitaryReviewType]
