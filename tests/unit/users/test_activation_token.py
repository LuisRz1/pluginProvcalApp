"""Tests unitarios para ActivationToken"""
import pytest
from datetime import datetime, timedelta
from app.users.domain.activation_token import ActivationToken
from app.building_blocks.exceptions import DomainException


def test_create_activation_token():
    """Debe crear token de activación"""
    token = ActivationToken(
        token="test-token-123",
        user_id="user-123",
        employee_id="EMP001"
    )

    assert token.token == "test-token-123"
    assert token.user_id == "user-123"
    assert token.is_used == False
    assert token.is_valid() == True


def test_token_expires_after_time():
    """Token debe expirar después del tiempo configurado"""
    token = ActivationToken(
        token="test-token-123",
        user_id="user-123",
        employee_id="EMP001",
        expires_at=datetime.utcnow() - timedelta(hours=1)  # Ya expirado
    )

    assert token.is_expired() == True
    assert token.is_valid() == False


def test_token_valid_before_expiration():
    """Token debe ser válido antes de expirar"""
    token = ActivationToken(
        token="test-token-123",
        user_id="user-123",
        employee_id="EMP001",
        expires_at=datetime.utcnow() + timedelta(hours=48)
    )

    assert token.is_expired() == False
    assert token.is_valid() == True


def test_mark_token_as_used():
    """Debe marcar token como usado"""
    token = ActivationToken(
        token="test-token-123",
        user_id="user-123",
        employee_id="EMP001"
    )

    assert token.is_valid() == True

    token.mark_as_used()

    assert token.is_used == True
    assert token.used_at is not None
    assert token.is_valid() == False


def test_cannot_use_token_twice():
    """No debe permitir usar token dos veces"""
    token = ActivationToken(
        token="test-token-123",
        user_id="user-123",
        employee_id="EMP001"
    )

    token.mark_as_used()

    with pytest.raises(DomainException, match="ya ha sido usado"):
        token.mark_as_used()


def test_generate_secure_token():
    """Debe generar token seguro"""
    token1 = ActivationToken.generate_secure_token()
    token2 = ActivationToken.generate_secure_token()

    assert len(token1) > 30  # Token largo
    assert token1 != token2  # Tokens únicos
