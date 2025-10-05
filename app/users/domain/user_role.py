from enum import Enum

class UserRole(Enum):
    """Roles de usuario en el sistema de catering"""
    EMPLOYEE = "employee"
    COOK = "cook"
    NUTRITIONIST = "nutritionist"
    WAREHOUSE = "warehouse"
    ADMIN = "admin"     # Hace las veces de RRHH y gestor del sistema

    @classmethod
    def from_string(cls, role_str: str) -> "UserRole":
        """Convierte un string a UserRole"""
        try:
            return cls(role_str.lower())
        except ValueError as exc:
            valid_roles = [role.value for role in cls]
            raise ValueError(
                f"Rol inválido: {role_str}. Roles válidos: {', '.join(valid_roles)}"
            ) from exc
