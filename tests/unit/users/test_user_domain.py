"""Tests unitarios para la entidad User"""
import pytest
from app.users.domain.user import User, UserRole, UserStatus
from app.building_blocks.exceptions import DomainException


def test_create_user_with_valid_data():
    """Debe crear un usuario con datos válidos"""
    user = User(
        employee_id="EMP001",
        email="test@catering.com",
        full_name="Test User",
        dni="12345678",
        role=UserRole.EMPLOYEE
    )

    assert user.employee_id == "EMP001"
    assert user.email == "test@catering.com"
    assert user.status == UserStatus.PENDING_ACTIVATION
    assert user.data_processing_consent == False


def test_create_user_with_invalid_email():
    """Debe fallar al crear usuario con email inválido"""
    with pytest.raises(DomainException, match="Email inválido"):
        User(
            employee_id="EMP001",
            email="invalid-email",
            full_name="Test User",
            dni="12345678"
        )


def test_set_password_with_valid_policy():
    """Debe establecer contraseña que cumple política"""
    user = User(
        employee_id="EMP001",
        email="test@catering.com",
        full_name="Test User",
        dni="12345678"
    )

    user.set_password("MySecure123!")

    assert user.password_hash is not None
    assert user.verify_password("MySecure123!")
    assert not user.verify_password("WrongPassword")


def test_set_password_too_short():
    """Debe fallar con contraseña muy corta"""
    user = User(
        employee_id="EMP001",
        email="test@catering.com",
        full_name="Test User",
        dni="12345678"
    )

    with pytest.raises(DomainException, match="al menos 8 caracteres"):
        user.set_password("Short1!")


def test_set_password_missing_uppercase():
    """Debe fallar sin mayúsculas"""
    user = User(
        employee_id="EMP001",
        email="test@catering.com",
        full_name="Test User",
        dni="12345678"
    )

    with pytest.raises(DomainException, match="al menos una mayúscula"):
        user.set_password("mysecure123!")


def test_set_password_missing_number():
    """Debe fallar sin números"""
    user = User(
        employee_id="EMP001",
        email="test@catering.com",
        full_name="Test User",
        dni="12345678"
    )

    with pytest.raises(DomainException, match="al menos un número"):
        user.set_password("MySecurePass!")


def test_cannot_reuse_previous_password():
    """No debe permitir reutilizar contraseña anterior"""
    user = User(
        employee_id="EMP001",
        email="test@catering.com",
        full_name="Test User",
        dni="12345678"
    )

    user.set_password("FirstPassword123!")

    with pytest.raises(DomainException, match="contraseña que hayas usado anteriormente"):
        user.set_password("FirstPassword123!")


def test_activate_user_account():
    """Debe activar cuenta correctamente"""
    user = User(
        employee_id="EMP001",
        email="test@catering.com",
        full_name="Test User",
        dni="12345678",
        status=UserStatus.PENDING_ACTIVATION
    )

    user.activate(
        password="NewPassword123!",
        personal_email="personal@gmail.com",
        data_consent=True
    )

    assert user.status == UserStatus.ACTIVE
    assert user.personal_email == "personal@gmail.com"
    assert user.data_processing_consent == True
    assert user.activated_at is not None
    assert user.password_hash is not None


def test_cannot_activate_without_consent():
    """No debe activar sin consentimiento"""
    user = User(
        employee_id="EMP001",
        email="test@catering.com",
        full_name="Test User",
        dni="12345678",
        status=UserStatus.PENDING_ACTIVATION
    )

    with pytest.raises(DomainException, match="aceptar el tratamiento de datos"):
        user.activate(
            password="NewPassword123!",
            personal_email="personal@gmail.com",
            data_consent=False
        )


def test_cannot_activate_already_active_user():
    """No debe activar usuario ya activo"""
    user = User(
        employee_id="EMP001",
        email="test@catering.com",
        full_name="Test User",
        dni="12345678",
        status=UserStatus.ACTIVE  # Ya activo
    )

    with pytest.raises(DomainException, match="no está pendiente de activación"):
        user.activate(
            password="NewPassword123!",
            personal_email="personal@gmail.com",
            data_consent=True
        )