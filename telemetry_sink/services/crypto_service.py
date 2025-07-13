import logging
from cryptography.fernet import Fernet, InvalidToken

log = logging.getLogger(__name__)


class CryptoService:
    """A simple wrapper for symmetric encryption using Fernet."""

    def __init__(self, key: str):
        """Initializes the service with a URL-safe base64-encoded 32-byte key."""
        try:
            self._fernet = Fernet(key.encode("utf-8"))
            log.info("CryptoService initialized successfully.")
        except (ValueError, TypeError) as e:
            log.error("FATAL: Invalid encryption key. It must be a 32-byte URL-safe base64 string.")
            raise ValueError(f"Invalid encryption key: {e}")

    def encrypt(self, plaintext: bytes) -> bytes:
        """Encrypts a byte string."""
        return self._fernet.encrypt(plaintext)

    def decrypt(self, ciphertext: bytes) -> bytes:
        """Decrypts a byte string, raising InvalidToken on failure."""
        try:
            return self._fernet.decrypt(ciphertext)
        except InvalidToken:
            log.warning("Decryption failed: Invalid token or key.")
            raise
