"""Security utilities for authentication and authorization."""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from backend.utils.errors import AuthenticationError, AuthorizationError


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
    
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against
    
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def generate_api_key() -> str:
    """
    Generate a secure random API key.
    
    Returns:
        32-character hexadecimal API key
    """
    return secrets.token_hex(32)


def hash_api_key(api_key: str) -> str:
    """
    Hash an API key for secure storage.
    
    Args:
        api_key: Plain API key
    
    Returns:
        SHA256 hash of the API key
    """
    return hashlib.sha256(api_key.encode()).hexdigest()


def create_access_token(
    data: Dict[str, Any],
    secret_key: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in the token
        secret_key: Secret key for signing
        expires_delta: Token expiration time
    
    Returns:
        JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm="HS256")
    return encoded_jwt


def decode_access_token(token: str, secret_key: str) -> Dict[str, Any]:
    """
    Decode and verify a JWT access token.
    
    Args:
        token: JWT token to decode
        secret_key: Secret key for verification
    
    Returns:
        Decoded token data
    
    Raises:
        AuthenticationError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return payload
    except JWTError as e:
        raise AuthenticationError(f"Invalid or expired token: {str(e)}")


def validate_api_key(
    provided_key: str,
    stored_hash: str
) -> bool:
    """
    Validate an API key against its stored hash.
    
    Args:
        provided_key: API key provided by the user
        stored_hash: Stored hash of the valid API key
    
    Returns:
        True if API key is valid, False otherwise
    """
    provided_hash = hash_api_key(provided_key)
    return secrets.compare_digest(provided_hash, stored_hash)


def sanitize_input(input_str: str, max_length: int = 1000) -> str:
    """
    Sanitize user input to prevent injection attacks.
    
    Args:
        input_str: Input string to sanitize
        max_length: Maximum allowed length
    
    Returns:
        Sanitized string
    """
    # Trim to max length
    sanitized = input_str[:max_length]
    
    # Remove null bytes
    sanitized = sanitized.replace('\x00', '')
    
    # Strip leading/trailing whitespace
    sanitized = sanitized.strip()
    
    return sanitized


def check_rate_limit(
    identifier: str,
    max_requests: int,
    window_seconds: int,
    current_count: int
) -> bool:
    """
    Check if a rate limit has been exceeded.
    
    Args:
        identifier: Unique identifier (user ID, API key, IP address)
        max_requests: Maximum allowed requests in the window
        window_seconds: Time window in seconds
        current_count: Current request count in the window
    
    Returns:
        True if within rate limit, False if exceeded
    """
    return current_count < max_requests


def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """
    Mask sensitive data for logging (e.g., API keys, tokens).
    
    Args:
        data: Sensitive data to mask
        visible_chars: Number of characters to keep visible at the end
    
    Returns:
        Masked string
    """
    if len(data) <= visible_chars:
        return "*" * len(data)
    
    return "*" * (len(data) - visible_chars) + data[-visible_chars:]
