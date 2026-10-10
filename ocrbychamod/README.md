# ocrbychamod

Extract text from PNG and JPEG images using swappable OCR engines. Tesseract is the first built-in engine.

## Prerequisites

The Tesseract OCR program must be installed on your machine. `pip` cannot install it for you.

- **Windows:** install the UB Mannheim build, then add `C:\Program Files\Tesseract-OCR` to your PATH
- **macOS:** `brew install tesseract`
- **Ubuntu/Debian:** `sudo apt-get install tesseract-ocr`

Check it works:

```
tesseract --version
```

## Installation

```
pip install "ocrbychamod[tesseract]"
```

## Usage

```python
from ocrbychamod import extract_text

text = extract_text("receipt.png")
print(text)
```

If Tesseract is not on your PATH, or you want another language:

```python
text = extract_text(
    "receipt.jpg",
    engine="tesseract",
    lang="eng",
    tesseract_cmd=r"C:\Program Files\Tesseract-OCR\tesseract.exe",
)
```

Supported formats: `.png`, `.jpg`, `.jpeg`.

## Swappable engines

The core never depends on a specific OCR tool. Every engine implements the `OCREngine` interface, so you can plug in your own:

```python
from ocrbychamod import OCREngine, extract_text, register_engine

class MyEngine(OCREngine):
    name = "my-engine"

    def extract_text(self, image):
        # image is a PIL.Image.Image
        return "recognized text"

# Option 1: pass an instance directly
extract_text("img.png", engine=MyEngine())

# Option 2: register it and select it by name
register_engine("my-engine", MyEngine)
extract_text("img.png", engine="my-engine")
```

List the registered engines:

```python
from ocrbychamod import available_engines
print(available_engines())  # ['tesseract', ...]
```

## Development

```
git clone https://github.com/Chamodpw2000/ocr_extract_pip.git
cd ocrbychamod
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[tesseract]" pytest
pytest
```

## License

MIT. See [LICENSE](LICENSE).