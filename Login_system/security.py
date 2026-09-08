"""
Password hashing helpers.
Uses only Python's built-in hashlib — no external packages needed.
Passwords are never stored in plain text, only their salted hash.
"""

import hashlib
import os

# Higher = slower to compute = harder to brute-force.
# 100,000 is a reasonable default for a student project.
_PBKDF2_ITERATIONS = 100_000


def generate_salt() -> str:
    """Generates a random salt, unique per user, stored alongside the hash."""
    return os.urandom(16).hex()


def hash_password(password: str, salt: str) -> str:
    """Hashes a password together with its salt."""
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        _PBKDF2_ITERATIONS,
    ).hex()


def verify_password(password: str, salt: str, expected_hash: str) -> bool:
    """Returns True if the given password matches the stored hash."""
    return hash_password(password, salt) == expected_hash
