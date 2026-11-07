"""Erro de aplicação com código e status HTTP (contrato dos handlers da API)."""


class AuthError(Exception):
    def __init__(
        self,
        code: str,
        status: int = 401,
        retry_after: int | None = None,
        manual_entry_permitted: bool = False,
    ):
        self.code = code
        self.status = status
        self.retry_after = retry_after
        self.manual_entry_permitted = manual_entry_permitted
