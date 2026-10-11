from ..base import OCREngine
from ..models import Word


class TesseractEngine(OCREngine):
    name = "tesseract"

    def __init__(self, lang: str = "eng", psm: int | None = 6,
                 config: str = "", tesseract_cmd: str | None = None):
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
        parts = [f"--psm {psm}"] if psm is not None else []
        if config:
            parts.append(config)
        self.config = " ".join(parts)

    def extract_text(self, image) -> str:
        # Raw Tesseract output, as in v0.1
        return self._pt.image_to_string(image, lang=self.lang, config=self.config)

    def extract_words(self, image) -> list[Word]:
        data = self._pt.image_to_data(
            image, lang=self.lang, config=self.config,
            output_type=self._pt.Output.DICT,
        )
        words = []
        for i, raw in enumerate(data["text"]):
            text = str(raw).strip()
            conf = float(data["conf"][i])
            if not text or conf < 0:      # -1 marks non-word rows
                continue
            x, y = data["left"][i], data["top"][i]
            w, h = data["width"][i], data["height"][i]
            words.append(Word(text, x, y, x + w, y + h, conf / 100))
        return words