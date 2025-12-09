from dataclasses import dataclass
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class SanitaryCompany:
    """
    Empresa especializada a la que se contacta cuando
    una revisión de sanidad es INCONFORME.

    Equivale a la entidad Empresa del E-R de sanidad:
      - empresa_id
      - razon_social
      - ruc
      - telefono
      - correo
    """

    id: UUID              # empresa_id
    business_name: str    # razon_social
    ruc: str              # ruc
    phone: Optional[str]  # telefono
    email: Optional[str]  # correo

    @classmethod
    def create(
        cls,
        business_name: str,
        ruc: str,
        phone: Optional[str] = None,
        email: Optional[str] = None,
    ) -> "SanitaryCompany":
        return cls(
            id=uuid4(),
            business_name=business_name,
            ruc=ruc,
            phone=phone,
            email=email,
        )

    def update_data(
        self,
        business_name: Optional[str] = None,
        ruc: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
    ) -> None:
        """
        Actualiza los datos básicos de la empresa especializada.
        Solo cambia los campos que se envíen.
        """
        if business_name is not None:
            self.business_name = business_name
        if ruc is not None:
            self.ruc = ruc
        if phone is not None:
            self.phone = phone
        if email is not None:
            self.email = email
