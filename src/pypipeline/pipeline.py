"""Pipeline.

## Type Algebra

This module defines a strongly typed, composable pipeline system based on
ParamSpec and TypeVarTuple generics.

**Let**

* `P` denote the parameter specification of the current stage (the callable's input signature),
* `R` denote a single-value return type, and
* `RT` denote a variadic tuple of return types when the stage returns a tuple.
* `GR` denote a single-value return type of the next stage, and
* `GRT` denote a variadic tuple of return types when the next stage returns a tuple.

**Pipeline**

A pipeline can thus be represented as:

* `Pipe[P, R]`   === `Callable[P, R]`
* `Pipe[P, *RT]` === `Callable[P, tuple[*RT]]`

Composition rules are enforced by type relations:

* A `Pipe[P, R]` can compose with a function `Callable[[R], GR]` producing `Pipe[P, GR]`.
* A `Pipe[P, R]` can compose with a tuple-returning function `Callable[[R], tuple[*GRT]]`
  producing `Pipe[P, *GRT]`.
* A `Pipe[P, *RT]` (tuple-unpacking stage) can compose with a
  - function `Callable[[*RT], GR]` producing `Pipe[P, GR]`,
  - or with another tuple-returning function `Callable[[*RT], tuple[*GRT]]`
    producing `Pipe[P, *GRT]`.

**To Be Implemented**

* Unpacking `dict` return type into `kwargs`
* Unpackaing `tuple[tuple, dict]` return type into `args` and `kwargs`
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, cast, overload

from pypipeline._warnings import warning_unstable_feature_or_operator
from pypipeline.compose import _compose_no_ret_unpack, _compose_ret_tuple_unpack

if TYPE_CHECKING:
    from collections.abc import Callable


type ResultUnpack = Literal["tuple", "dict"]

type _ComposeType = Literal["no_compose", "regular", "tuple_unpack"]

type _Call[**P, R, *RT] = Callable[P, R] | Callable[P, tuple[*RT]]
type _Pipe[**P, R, *RT] = _PipeStd[P, R] | _PipeTUn[P, *RT]


class _PipeThenMixin:
    _compose_type: _ComposeType
    f: Callable | None = None

    def _then_impl[**P, R, *TR](self, f: _Call, *, result_unpack: ResultUnpack | None = None) -> _Pipe[P, R, *TR]:
        # * in @overload we trust - thus we cast
        if result_unpack is None:
            return _PipeStd[P, R](cast("Callable[P, R]", f))
        if result_unpack == "tuple":
            return _PipeTUn[P, *TR](cast("Callable[P, tuple[*TR]]", f))
        msg = f"Unsupported unpack result: {result_unpack}"
        raise ValueError(msg)

    def _then[**P, R, *RT](self, f: _Call, *, result_unpack: ResultUnpack | None = None) -> _Pipe[P, R, *RT]:
        func = self._compose_self_with(f)
        return self._then_impl(func, result_unpack=result_unpack)

    def _compose_self_with(self, f: Callable) -> Callable:
        if self._compose_type == "no_compose":
            return f
        if self.f is None:
            msg = f"Wrong compose type {self._compose_type} for {type(self)}"
            raise ValueError(msg)
        if self._compose_type == "regular":
            return _compose_no_ret_unpack(self.f, f)
        if self._compose_type == "tuple_unpack":
            return _compose_ret_tuple_unpack(self.f, f)
        msg = f"Unsupported compose type: {self._compose_type}"
        raise ValueError(msg)


@dataclass(slots=True, frozen=True)
class Pipeline(_PipeThenMixin):
    """Entry point for building a new pipeline chain.

    Supports `.then(f)` or `.then(f, result_unpack="tuple")`.
    """

    _compose_type = "no_compose"

    def __rshift__[**P, R](self, f: Callable[P, R]) -> _PipeStd[P, R]:
        return self.then(f)

    @overload
    def then[**P, R](self, f: Callable[P, R]) -> _PipeStd[P, R]: ...
    @overload
    def then[**P, *RT](self, f: Callable[P, tuple[*RT]], *, result_unpack: Literal["tuple"]) -> _PipeTUn[P, *RT]: ...

    def then[**P, R, *RT](self, f: _Call, *, result_unpack: ResultUnpack | None = None) -> _Pipe[P, R, *RT]:
        return self._then(f, result_unpack=result_unpack)


@dataclass(slots=True, frozen=True)
class _PipeBase[**P, R]:
    f: Callable[P, R]

    def call(self, *args: P.args, **kwargs: P.kwargs) -> R:
        return self.f(*args, **kwargs)


@dataclass(slots=True, frozen=True)
class _PipeStd[**P, R](_PipeBase[P, R], _PipeThenMixin):
    """Represents a pipeline stage whose wrapped function returns a single value."""

    _compose_type = "regular"

    def __rshift__[GR](self, f: Callable[[R], GR]) -> _PipeStd[P, GR]:
        return self.then(f)

    def __or__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        warning_unstable_feature_or_operator()
        return self.call(*args, **kwargs)

    @overload
    def then[GR](self, g: Callable[[R], GR]) -> _PipeStd[P, GR]: ...
    @overload
    def then[*GRT](self, g: Callable[[R], tuple[*GRT]], *, result_unpack: Literal["tuple"]) -> _PipeTUn[P, *GRT]: ...

    def then[GR, *GRT](self, g: _Call, result_unpack: ResultUnpack | None = None) -> _Pipe[P, GR, *GRT]:
        return self._then(g, result_unpack=result_unpack)


@dataclass(slots=True, frozen=True)
class _PipeTUn[**P, *TR](_PipeBase[P, tuple[*TR]], _PipeThenMixin):
    """Represents a pipeline stage whose return type (tuple) is to be unpacked."""

    _compose_type = "tuple_unpack"

    def __rshift__[GR](self, f: Callable[[*TR], GR]) -> _PipeStd[P, GR]:
        return self.then(f)

    def __or__(self, *args: P.args, **kwargs: P.kwargs) -> tuple[*TR]:
        warning_unstable_feature_or_operator()
        return self.call(*args, **kwargs)

    @overload
    def then[GR](self, g: Callable[[*TR], GR]) -> _PipeStd[P, GR]: ...
    @overload
    def then[*GRT](self, g: Callable[[*TR], tuple[*GRT]], *, result_unpack: Literal["tuple"]) -> _PipeTUn[P, *GRT]: ...

    def then[GR, *GRT](self, g: _Call, *, result_unpack: ResultUnpack | None = None) -> _Pipe[P, GR, *GRT]:
        return self._then(g, result_unpack=result_unpack)
