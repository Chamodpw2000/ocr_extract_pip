import shutil
import pytest
from PIL import Image, ImageDraw, ImageFont

from ocrbychamod import extract_text, OCREngine, register_engine, available_engines


class FakeEngine(OCREngine):
    name = "fake"

    def extract_text(self, image):
        return "fake text"


@pytest.fixture
def png(tmp_path):
    p = tmp_path / "a.png"
    Image.new("RGB", (50, 50), "white").save(p)
    return p


def test_custom_engine_instance(png):
    assert extract_text(png, engine=FakeEngine()) == "fake text"


def test_registered_engine_by_name(png):
    register_engine("fake", FakeEngine)
    assert "fake" in available_engines()
    assert extract_text(png, engine="fake") == "fake text"


def test_unknown_engine(png):
    with pytest.raises(ValueError):
        extract_text(png, engine="nope")


def test_unsupported_extension(tmp_path):
    p = tmp_path / "a.gif"
    p.write_bytes(b"x")
    with pytest.raises(ValueError):
        extract_text(p, engine=FakeEngine())


def test_missing_file():
    with pytest.raises(FileNotFoundError):
        extract_text("missing.png", engine=FakeEngine())


@pytest.mark.skipif(shutil.which("tesseract") is None, reason="tesseract not installed")
def test_real_tesseract(tmp_path):
    img = Image.new("RGB", (400, 120), "white")
    ImageDraw.Draw(img).text((20, 30), "HELLO", fill="black",
                             font=ImageFont.load_default(size=60))
    p = tmp_path / "hello.png"
    img.save(p)
    assert "HELLO" in extract_text(p).upper()
