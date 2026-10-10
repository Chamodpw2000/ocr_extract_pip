from ..base import OCREngine

class TesseractEngine(OCREngine):
    name = "tesseract"

    def __init__(self, lang: str = "eng", config: str = "", tesseract_cmd: str | None = None):
        try:
            import pytesseract
        except ImportError as e:
            raise ImportError(
                "Tesseract engine needs extra deps: pip install ocrbychamod[tesseract]"
            ) from e
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        self._pt = pytesseract
        self.lang = lang
        self.config = config

    def extract_text(self, image) -> str:
        return self._pt.image_to_string(image, lang=self.lang, config=self.config)
    
    
