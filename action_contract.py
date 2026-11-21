"""Common action contract. Providers register operations, never combinations."""
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Operation:
    name: str
    label: str
    describe: Callable
    valid: Callable
    run: Callable
    delayed: bool = False
    accepts_result: bool = False
    qq_only: bool = False
    autonomous_available: Callable | None = None
    owner: bool = True
    owner_available: Callable | None = None


class Unavailable(ValueError):
    """Safe provider-authored explanation to return to the owner."""
