from typing import Callable
from .base import OCREngine

_ENGINES: dict[str, Callable[..., OCREngine]] = {}


def register_engine(name: str, factory: Callable[..., OCREngine]) -> None:
    _ENGINES[name] = factory


def get_engine(name: str, **options) -> OCREngine:
    try:
        factory = _ENGINES[name]
    except KeyError:
        raise ValueError(f"Unknown engine '{name}'. Available: {available_engines()}") from None
    return factory(**options)


def available_engines() -> list[str]:
    return sorted(_ENGINES)


def _register_builtin() -> None:
    from .engines import TesseractEngine
    register_engine("tesseract", TesseractEngine)


_register_builtin()