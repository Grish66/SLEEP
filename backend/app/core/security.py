from passlib.hash import argon2


def hash_password(password: str) -> str:
    """
    Return a secure Argon2 hash for storage in DB.
    """
    return argon2.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    """
    Check a plain password against the stored hash.
    """
    return argon2.verify(plain_password, password_hash)
