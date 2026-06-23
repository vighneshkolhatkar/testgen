# testgen

Agentic unit test generator for Java and Python.

![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-MIT-green)

## What it does

- Parses Java and Python source files to extract class structure, method signatures, type hints, and docstrings
- Generates framework-native tests — pytest + unittest.mock for Python, JUnit 5 + Mockito for Java — using LLM-powered analysis
- Streams generated output in real-time and writes a runnable test file to disk

## Install

**From PyPI:**
```bash
pip install testgen-ai
```

**From source:**
```bash
git clone https://github.com/your-org/testgen.git
cd testgen
pip install -e .
```

## Setup

Set your Anthropic API key:
```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

Or create a `.env` file in your working directory (copy from `.env.example`):
```
ANTHROPIC_API_KEY=sk-ant-...
```

## Usage

```bash
# Generate tests for a Python file
testgen generate examples/payment_service.py

# Target a specific method
testgen generate examples/payment_service.py --function charge

# Write to a custom output directory
testgen generate examples/PaymentService.java --output tests/

# Use faster/cheaper model (Claude Haiku)
testgen generate examples/payment_service.py --fast
```

## Output Example

Running `testgen generate examples/payment_service.py --function charge` produces a file like `test_payment_service.py`:

```python
import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

from examples.payment_service import PaymentService, CardDetails, Transaction


@pytest.fixture
def db():
    return MagicMock()


@pytest.fixture
def gateway():
    return MagicMock()


@pytest.fixture
def service(db, gateway):
    return PaymentService(db=db, gateway_client=gateway)


def test_charge_returns_transaction_on_success(service, db, gateway):
    card = CardDetails(token="tok_test", last_four="4242", expiry="12/99")
    gateway.charge.return_value = {"id": "txn_001"}
    db.get.return_value = MagicMock(amount=100.0)
    txn = service.charge(card, 100.0, "USD")
    assert txn.status == "completed"
    assert txn.amount == 100.0


def test_charge_raises_for_zero_amount(service, db, gateway):
    card = CardDetails(token="tok_test", last_four="4242", expiry="12/99")
    with pytest.raises(ValueError, match="positive"):
        service.charge(card, 0, "USD")


def test_charge_raises_for_negative_amount(service, db, gateway):
    card = CardDetails(token="tok_test", last_four="4242", expiry="12/99")
    with pytest.raises(ValueError, match="positive"):
        service.charge(card, -50.0, "USD")


def test_charge_raises_for_invalid_card(service, db, gateway):
    card = CardDetails(token="", last_four="4242", expiry="12/99")
    with pytest.raises(ValueError, match="Invalid card details"):
        service.charge(card, 100.0, "USD")


def test_charge_persists_transaction(service, db, gateway):
    card = CardDetails(token="tok_test", last_four="4242", expiry="12/99")
    gateway.charge.return_value = {"id": "txn_002"}
    service.charge(card, 50.0, "USD")
    db.save.assert_called_once()
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CLI (Typer)                          │
│   testgen generate <file> [--function X] [--output dir]     │
└───────────────────┬─────────────────────────────────────────┘
                    │
          ┌─────────▼──────────┐
          │  Language Detector  │
          └─────────┬──────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
  ┌─────▼──────┐         ┌──────▼──────┐
  │ Python AST │         │ Java Parser │
  │  (stdlib)  │         │ (javalang)  │
  └─────┬──────┘         └──────┬──────┘
        └───────────┬───────────┘
                    │
          ┌─────────▼──────────┐
          │   Context Builder   │
          └─────────┬──────────┘
                    │
          ┌─────────▼──────────┐
          │   Prompt Builder    │
          └─────────┬──────────┘
                    │
          ┌─────────▼──────────┐
          │  Anthropic Claude   │  Streaming + Prompt Caching
          └─────────┬──────────┘
                    │
          ┌─────────▼──────────┐
          │   Output Writer     │  Writes test file to disk
          └────────────────────┘
```

## Supported Languages

| Language | Test Framework | Parser |
|---|---|---|
| Python | pytest + unittest.mock | stdlib ast |
| Java | JUnit 5 + Mockito | javalang |

## Contributing

Fork the repo, create a feature branch, and open a pull request. All contributions must include tests — run `pytest --cov=testgen` before submitting. For larger changes, open an issue first to discuss the approach. The project follows the existing code style: type hints on all public signatures, Rich for all terminal output, no bare print statements.
