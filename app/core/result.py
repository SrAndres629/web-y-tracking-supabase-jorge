"""
🎯 Result Type - Manejo explícito de éxito/error.

Inspirado en Rust's Result<T, E> y Haskell's Either.
Fuerza al desarrollador (humano o IA) a considerar ambos casos.

Patrón Silicon Valley: Usado en Google, Stripe, Netflix para
reducir errores de null/exception handling en producción.

Example:
    >>> result = await repository.find_by_id("123")
    >>> if result.is_ok:
    ...     user = result.unwrap()
    ... else:
    ...     error = result.unwrap_err()
    ...     logger.error(f"Failed: {error}")
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, Generic, TypeVar, Union, final

T = TypeVar("T")  # Success type
E = TypeVar("E")  # Error type
U = TypeVar("U")  # Mapped type


@final
@dataclass(frozen=True, slots=True)
class Ok(Generic[T]):
    """
    Variant exitoso de Result.
    Inmutable y con slots para performance (menos memoria, más rápido).
    """

    value: T

    def __repr__(self) -> str:
        return f"Ok({self.value!r})"

    def __bool__(self) -> bool:
        return True


@final
@dataclass(frozen=True, slots=True)
class Err(Generic[E]):
    """
    Variant de error de Result.
    Contiene información sobre el fallo.
    """

    error: E

    def __repr__(self) -> str:
        return f"Err({self.error!r})"

    def __bool__(self) -> bool:
        return False


class Result(Generic[T, E]):
    """
    Result type para manejo explícito de operaciones que pueden fallar.

    REGLAS DE USO:
    1. SIEMPRE verificar is_ok o is_err antes de unwrap
    2. NUNCA hacer unwrap sin verificar (lanzará UnwrapError)
    3. Preferir unwrap_or/unwrap_or_else para valores por defecto
    4. Usar map/and_then para encadenar operaciones

    Attributes:
        _inner: Either Ok(value) or Err(error)
    """

    __slots__ = ("_inner",)

    def __init__(self, inner: Union[Ok[T], Err[E]]) -> None:
        self._inner = inner

    # ===== Constructores =====

    @staticmethod
    def ok(value: T) -> Result[T, Any]:
        """Crea un Result exitoso."""
        return Result(Ok(value))

    @staticmethod
    def err(error: E) -> Result[Any, E]:
        """Crea un Result con error."""
        return Result(Err(error))

    # ===== Propiedades =====

    @property
    def is_ok(self) -> bool:
        """True si es Ok."""
        return isinstance(self._inner, Ok)

    @property
    def is_err(self) -> bool:
        """True si es Err."""
        return isinstance(self._inner, Err)

    # ===== Unwrap (requiere verificación previa) =====

    def unwrap(self) -> T:
        """
        Obtiene el valor Ok. Lanza UnwrapError si es Err.

        ⚠️ Solo usar después de verificar is_ok.
        """
        if isinstance(self._inner, Ok):
            return self._inner.value
        raise UnwrapError(f"Called unwrap on Err: {self._inner.error}")

    def unwrap_err(self) -> E:
        """
        Obtiene el error. Lanza UnwrapError si es Ok.

        ⚠️ Solo usar después de verificar is_err.
        """
        if isinstance(self._inner, Err):
            return self._inner.error
        raise UnwrapError(f"Called unwrap_err on Ok: {self._inner.value}")

    # ===== Unwrap seguro (con defaults) =====

    def unwrap_or(self, default: T) -> T:
        """Obtiene valor o retorna default si es Err."""
        return self._inner.value if isinstance(self._inner, Ok) else default

    def unwrap_or_else(self, op: Callable[[E], T]) -> T:
        """Obtiene valor o computa uno del error."""
        return self._inner.value if isinstance(self._inner, Ok) else op(self._inner.error)

    def expect(self, msg: str) -> T:
        """Unwrap con mensaje de error personalizado."""
        if isinstance(self._inner, Ok):
            return self._inner.value
        raise UnwrapError(f"{msg}: {self._inner.error}")

    # ===== Transformaciones =====

    def map(self, op: Callable[[T], U]) -> Result[U, E]:
        """Transforma el valor Ok, preserva Err."""
        if isinstance(self._inner, Ok):
            return Result.ok(op(self._inner.value))
        return Result(self._inner)  # type: ignore

    def map_err(self, op: Callable[[E], Any]) -> Result[T, Any]:
        """Transforma el error, preserva Ok."""
        if isinstance(self._inner, Err):
            return Result.err(op(self._inner.error))
        return Result(self._inner)  # type: ignore

    def and_then(self, op: Callable[[T], Result[U, E]]) -> Result[U, E]:
        """
        Encadena otra operación que retorna Result (monadic bind).

        Example:
            >>> find_user(id).and_then(lambda u: validate_active(u))
        """
        if isinstance(self._inner, Ok):
            return op(self._inner.value)
        return Result(self._inner)  # type: ignore

    def or_else(self, op: Callable[[E], Result[T, Any]]) -> Result[T, Any]:
        """Computa alternativa si es Err."""
        if isinstance(self._inner, Err):
            return op(self._inner.error)
        return Result(self._inner)  # type: ignore

    # ===== Pattern Matching helpers =====

    def match(self, ok_fn: Callable[[T], U], err_fn: Callable[[E], U]) -> U:
        """Ejecuta función según el caso (exhaustivo)."""
        if isinstance(self._inner, Ok):
            return ok_fn(self._inner.value)
        return err_fn(self._inner.error)

    # ===== Python conveniences =====

    def __repr__(self) -> str:
        return repr(self._inner)

    def __bool__(self) -> bool:
        return self.is_ok

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Result):
            return NotImplemented
        return self._inner == other._inner  # type: ignore

    def __hash__(self) -> int:
        return hash(self._inner)


class UnwrapError(Exception):
    """Error lanzado al hacer unwrap incorrecto."""

    pass


# ===== Decorator para convertir excepciones en Result =====


def as_result(*exceptions: type[Exception]) -> Callable:
    """
    Decorator que convierte excepciones en Result.err().

    Example:
        >>> @as_result(ValueError, KeyError)
        ... def parse_int(s: str) -> Result[int, Exception]:
        ...     return Result.ok(int(s))
    """
    exceptions = exceptions or (Exception,)

    def decorator(func: Callable[..., T]) -> Callable[..., Result[T, Exception]]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Result[T, Exception]:
            try:
                result = func(*args, **kwargs)
                # Si ya retorna Result, pasar través
                if isinstance(result, Result):
                    return result
                return Result.ok(result)
            except exceptions as e:
                return Result.err(e)

        return wrapper

    return decorator


# ===== Async version =====


def as_result_async(*exceptions: type[Exception]) -> Callable:
    """Versión async de as_result."""
    exceptions = exceptions or (Exception,)

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Result[Any, Exception]:
            try:
                result = await func(*args, **kwargs)
                if isinstance(result, Result):
                    return result
                return Result.ok(result)
            except exceptions as e:
                return Result.err(e)

        return wrapper

    return decorator
