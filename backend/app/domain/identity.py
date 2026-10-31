from dataclasses import dataclass
from uuid import UUID


def normalize_email(email: str) -> str:
    """The product treats the complete validated address as case insensitive."""
    return email.strip().casefold()


@dataclass(frozen=True)
class User:
    id: UUID
    name: str
    email: str
    role: str = "usuario"
    email_verified: bool = False
    investor_profile: str | None = None
