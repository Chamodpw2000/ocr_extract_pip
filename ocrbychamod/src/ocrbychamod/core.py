from pathlib import Path
from PIL import Image
from .base import OCREngine
from .registry import get_engine

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg"}


def extract_text(image_path, engine: "str | OCREngine" = "tesseract", **engine_options) -> str:
    path = Path(image_path)
    if not path.is_file():
        raise FileNotFoundError(f"Image not found: {path}")
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type '{path.suffix}'. Use PNG or JPEG.")

    ocr = engine if isinstance(engine, OCREngine) else get_engine(engine, **engine_options)

    with Image.open(path) as img:
        img.load()
        return ocr.extract_text(img)