from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import Final

from .basis_points import BASIS_POINTS_DENOMINATOR, validate_basis_points

CENTS_PER_UNIT: Final = 100
DEFAULT_CURRENCY: Final = "PLN"


@dataclass(frozen=True, slots=True)
class Money:
    cents: int
    currency: str = DEFAULT_CURRENCY

    def __post_init__(self) -> None:
        if not isinstance(self.cents, int):
            raise TypeError("Money.cents must be an integer")

        if self.cents < 0:
            raise ValueError("Money.cents must not be negative")

        if not self.currency.strip():
            raise ValueError("Money.currency must be a non-empty string")

    @classmethod
    def from_major(
        cls,
        amount: Decimal | int | str,
        currency: str = DEFAULT_CURRENCY,
    ) -> Money:
        decimal_amount = Decimal(str(amount))

        if decimal_amount < 0:
            raise ValueError("Money amount must not be negative")

        cents = int(
            (decimal_amount * CENTS_PER_UNIT).quantize(
                Decimal("1"),
                rounding=ROUND_HALF_UP,
            )
        )

        return cls(cents=cents, currency=currency)

    def multiply(self, quantity: int) -> Money:
        if quantity < 1:
            raise ValueError("Quantity must be greater than zero")

        return Money(cents=self.cents * quantity, currency=self.currency)

    def discount_amount(self, discount_bps: int) -> Money:
        validate_basis_points(discount_bps)

        cents = (self.cents * discount_bps + BASIS_POINTS_DENOMINATOR // 2) // (
            BASIS_POINTS_DENOMINATOR
        )

        return Money(cents=cents, currency=self.currency)

    def subtract(self, other: Money) -> Money:
        if self.currency != other.currency:
            raise ValueError("Cannot subtract money values in different currencies")

        if other.cents > self.cents:
            raise ValueError("Money subtraction cannot produce a negative amount")

        return Money(cents=self.cents - other.cents, currency=self.currency)

    def as_major_string(self) -> str:
        return cents_to_major_string(self.cents)


def cents_to_major_string(cents: int) -> str:
    if cents < 0:
        raise ValueError("cents must not be negative")

    return f"{Decimal(cents) / CENTS_PER_UNIT:.2f}"
