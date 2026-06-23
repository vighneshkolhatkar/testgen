import os
import pytest
from testgen.parser.python_parser import PythonParser

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "sample.py")


@pytest.fixture
def ctx():
    return PythonParser().parse(FIXTURE)


def test_language(ctx):
    assert ctx.language == "python"


def test_class_name(ctx):
    assert ctx.class_name == "PaymentProcessor"


def test_method_count(ctx):
    method_names = {m.name for m in ctx.methods}
    assert {"process_payment", "refund", "get_status", "validate_amount", "fetch_exchange_rate"}.issubset(method_names)


def test_process_payment_params(ctx):
    method = next(m for m in ctx.methods if m.name == "process_payment")
    param_names = [p[0] for p in method.params]
    assert "amount" in param_names
    assert "card_token" in param_names


def test_process_payment_return_type(ctx):
    method = next(m for m in ctx.methods if m.name == "process_payment")
    assert method.return_type == "Transaction"


def test_validate_amount_return_type(ctx):
    method = next(m for m in ctx.methods if m.name == "validate_amount")
    assert method.return_type == "bool"


def test_async_method_detected(ctx):
    method = next(m for m in ctx.methods if m.name == "fetch_exchange_rate")
    assert method.is_async is True


def test_docstrings_extracted(ctx):
    method = next(m for m in ctx.methods if m.name == "process_payment")
    assert "payment" in method.docstring.lower()
