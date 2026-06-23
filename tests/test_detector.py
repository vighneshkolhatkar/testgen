import pytest
from testgen.detector import detect_language


def test_detects_python():
    assert detect_language("payment_service.py") == "python"


def test_detects_java():
    assert detect_language("PaymentService.java") == "java"


def test_raises_for_unsupported_extension():
    with pytest.raises(ValueError, match="Unsupported file type"):
        detect_language("script.ts")


def test_raises_for_no_extension():
    with pytest.raises(ValueError, match="Unsupported file type"):
        detect_language("Makefile")
