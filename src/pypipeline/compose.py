from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable


def compose[**P, R, R2](f: Callable[P, R], g: Callable[[R], R2]) -> Callable[P, R2]:
    return _compose_no_ret_unpack(f, g)


def _compose_no_ret_unpack[**P, R, R2](f: Callable[P, R], g: Callable[[R], R2]) -> Callable[P, R2]:
    """Compose two callables `f` and `g` as `g(f(*args, **kwargs))`."""

    def inner(*args: P.args, **kwargs: P.kwargs) -> R2:
        return g(f(*args, **kwargs))

    return inner


def _compose_ret_tuple_unpack[**P, *TR, R2](f: Callable[P, tuple[*TR]], g: Callable[[*TR], R2]) -> Callable[P, R2]:
    """Compose two callables where `f` returns a tuple to be transformed into positional arguments for `g`."""

    def inner(*args: P.args, **kwargs: P.kwargs) -> R2:
        return g(*f(*args, **kwargs))

    return inner
