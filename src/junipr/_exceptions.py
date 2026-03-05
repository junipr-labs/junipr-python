"""Junipr API exceptions."""

from __future__ import annotations


class JuniprError(Exception):
    """Raised when the Junipr API returns an error response."""

    def __init__(
        self,
        message: str,
        code: str,
        request_id: str,
        status_code: int,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.request_id = request_id
        self.status_code = status_code

    def __repr__(self) -> str:
        return (
            f"JuniprError(code={self.code!r}, message={self.message!r}, "
            f"request_id={self.request_id!r}, status_code={self.status_code})"
        )
