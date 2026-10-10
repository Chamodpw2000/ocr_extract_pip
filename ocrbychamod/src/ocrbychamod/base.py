from abc import ABC, abstractmethod
from PIL import Image


class OCREngine(ABC):
    name: str

    @abstractmethod
    def extract_text(self, image: Image.Image) -> str:
        """Return the raw text found in the image."""


