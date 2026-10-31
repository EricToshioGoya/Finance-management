import base64
import hashlib
import hmac
import secrets

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError
from cryptography.fernet import Fernet


class Security:
    def __init__(self, data_key: str):
        self.cipher = Fernet(data_key.encode())
        self.lookup_key = hmac.digest(base64.urlsafe_b64decode(data_key), b"lookup-v1", "sha256")
        self.hasher = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4)
        self.dummy_hash = self.hasher.hash(secrets.token_urlsafe(32))

    def lookup(self, value: str) -> str:
        return hmac.new(self.lookup_key, value.encode(), hashlib.sha256).hexdigest()

    def encrypt(self, value: str) -> bytes:
        return self.cipher.encrypt(value.encode())

    def decrypt(self, value: bytes) -> str:
        return self.cipher.decrypt(value).decode()

    def verify(self, password_hash: str, password: str) -> bool:
        try:
            return self.hasher.verify(password_hash, password)
        except VerificationError:
            return False


def token_digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()
