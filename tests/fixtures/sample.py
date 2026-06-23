from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Optional


@dataclass
class Transaction:
    id: str
    amount: float
    status: str


class PaymentProcessor:
    """Handles payment processing operations."""

    def __init__(self, gateway_url: str, api_key: str) -> None:
        self._gateway_url = gateway_url
        self._api_key = api_key

    def process_payment(self, amount: float, card_token: str) -> Transaction:
        """Process a payment and return the resulting transaction."""
        validated = self.validate_amount(amount)
        if not validated:
            raise ValueError(f"Invalid amount: {amount}")
        return Transaction(id="txn_001", amount=amount, status="completed")

    def refund(self, transaction_id: str, amount: Optional[float] = None) -> bool:
        """Refund a transaction. If amount is None, refunds the full amount."""
        if not transaction_id:
            raise ValueError("transaction_id cannot be empty")
        return True

    def get_status(self, transaction_id: str) -> str:
        """Return the current status of a transaction."""
        return "completed"

    def validate_amount(self, amount: float) -> bool:
        """Return True if amount is positive and within limits."""
        return 0 < amount <= 10_000


async def fetch_exchange_rate(currency: str) -> float:
    """Fetch the current exchange rate for a currency asynchronously."""
    await asyncio.sleep(0)
    return 1.0
