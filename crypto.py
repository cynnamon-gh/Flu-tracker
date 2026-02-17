import os
from cryptography.fernet import Fernet

_fernet = None


def _get_fernet():
    global _fernet
    if _fernet is None:
        key = os.environ.get("ENCRYPTION_KEY")
        if not key:
            raise RuntimeError("ENCRYPTION_KEY environment variable not set")
        _fernet = Fernet(key.encode())
    return _fernet


def encrypt_phone(phone_number: str) -> str:
    return _get_fernet().encrypt(phone_number.encode()).decode()


def decrypt_phone(encrypted: str) -> str:
    return _get_fernet().decrypt(encrypted.encode()).decode()


def hash_phone(phone_number: str) -> str:
    """One-way hash for quick lookups without decrypting every row."""
    import hashlib
    salt = os.environ.get("ENCRYPTION_KEY", "")[:16]
    return hashlib.sha256((salt + phone_number).encode()).hexdigest()
