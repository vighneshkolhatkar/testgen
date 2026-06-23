from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class CardDetails:
    token: str
    last_four: str
    expiry: str


@dataclass
class Transaction:
    id: str
    amount: float
    currency: str
    status: str
    created_at: datetime


class PaymentService:
    """Core payment processing service."""

    def __init__(self, db, gateway_client) -> None:
        self._db = db
        self._gateway = gateway_client

    def charge(self, card: CardDetails, amount: float, currency: str = "USD") -> Transaction:
        """Charge a card and persist the transaction."""
        if not self.validate_card(card):
            raise ValueError("Invalid card details")
        if amount <= 0:
            raise ValueError("Amount must be positive")

        result = self._gateway.charge(card.token, amount, currency)
        txn = Transaction(
            id=result["id"],
            amount=amount,
            currency=currency,
            status="completed",
            created_at=datetime.utcnow(),
        )
        self._db.save(txn)
        return txn

    def refund(self, transaction_id: str, amount: Optional[float] = None) -> bool:
        """Refund a transaction fully or partially."""
        txn = self._db.get(transaction_id)
        if txn is None:
            raise ValueError(f"Transaction not found: {transaction_id}")
        refund_amount = amount or txn.amount
        if refund_amount > txn.amount:
            raise ValueError("Refund amount exceeds original charge")
        return self._gateway.refund(transaction_id, refund_amount)

    def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
        """Fetch a transaction by ID. Returns None if not found."""
        return self._db.get(transaction_id)

    def validate_card(self, card: CardDetails) -> bool:
        """Validate card token is non-empty and expiry is in the future."""
        if not card.token or not card.expiry:
            return False
        try:
            expiry = datetime.strptime(card.expiry, "%m/%y")
            return expiry > datetime.utcnow()
        except ValueError:
            return False
