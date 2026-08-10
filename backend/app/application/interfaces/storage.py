"""
Storage port. Business logic (use cases) depends on this Protocol, never
on a concrete backend. LocalStorage is the implementation for now; an
S3/Supabase implementation can be added in infrastructure/storage later
and swapped in via dependency injection with zero changes to use cases.
"""
from typing import Protocol


class StorageInterface(Protocol):
    def save(self, *, key: str, content: bytes) -> str:
        """Persists content under `key`. Returns the storage key actually used."""
        ...

    def read(self, *, key: str) -> bytes:
        ...

    def delete(self, *, key: str) -> None:
        ...
