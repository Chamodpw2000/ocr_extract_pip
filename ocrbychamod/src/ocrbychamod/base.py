from abc import ABC, abstractmethod
from PIL import Image

from .layout import build_lines
from .models import Word


class OCREngine(ABC):
    name: str

    @abstractmethod
    def extract_words(self, image: Image.Image) -> list[Word]:
        """Return words with bounding boxes and 0-1 confidence."""

    def extract_text(self, image: Image.Image) -> str:
        lines = build_lines(self.extract_words(image))
        return "\n".join(" ".join(w.text for w in line) for line in lines)