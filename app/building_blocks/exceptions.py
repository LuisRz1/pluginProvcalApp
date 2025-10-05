"""
Excepciones del dominio y aplicación.
Siguiendo los principios de DDD (Domain-Driven Design).
"""


class DomainException(Exception):
    """
    Excepción base del dominio.
    Representa violaciones de reglas de negocio.
    """
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class ValidationException(DomainException):
    """
    Excepción para errores de validación de datos.
    """


class AuthorizationException(Exception):
    """
    Excepción para errores de autorización.
    """
    def __init__(self, message: str = "No autorizado"):
        self.message = message
        super().__init__(self.message)


class AuthenticationException(Exception):
    """
    Excepción para errores de autenticación.
    """
    def __init__(self, message: str = "Credenciales inválidas"):
        self.message = message
        super().__init__(self.message)


class NotFoundException(Exception):
    """
    Excepción cuando no se encuentra un recurso.
    """
    def __init__(self, resource: str, identifier: str):
        self.message = f"{resource} con identificador '{identifier}' no encontrado"
        super().__init__(self.message)


class ConflictException(DomainException):
    """
    Excepción cuando hay un conflicto (ej: recurso ya existe).
    """
