from pathlib import Path
from PIL import Image

from .base import OCREngine
from .kv_extractor import pairs_from_words
from .models import Pair, Word
from .registry import get_engine

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg"}


def _prepare(image_path, engine, engine_options) -> "tuple[Path, OCREngine]":
    path = Path(image_path)
    if not path.is_file():
        raise FileNotFoundError(f"Image not found: {path}")
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type '{path.suffix}'. Use PNG or JPEG.")
    ocr = engine if isinstance(engine, OCREngine) else get_engine(engine, **engine_options)
    return path, ocr


def extract_text(image_path, engine: "str | OCREngine" = "tesseract", **engine_options) -> str:
    path, ocr = _prepare(image_path, engine, engine_options)
    with Image.open(path) as img:
        img.load()
        return ocr.extract_text(img)


def extract_words(image_path, engine: "str | OCREngine" = "tesseract", **engine_options) -> list[Word]:
    path, ocr = _prepare(image_path, engine, engine_options)
    with Image.open(path) as img:
        img.load()
        return ocr.extract_words(img)


def extract_pairs(image_path, engine: "str | OCREngine" = "tesseract", *,
                  gap_factor: float = 1.5, keep_empty: bool = False,
                  **engine_options) -> list[Pair]:
    words = extract_words(image_path, engine, **engine_options)
    return pairs_from_words(words, gap_factor=gap_factor, keep_empty=keep_empty)