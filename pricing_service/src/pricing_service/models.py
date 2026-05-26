from dataclasses import dataclass
from decimal import Decimal
from typing import Self

from .basis_points import validate_basis_points
from .money import DEFAULT_CURRENCY, Money, cents_to_major_string

PRICING_STATUS_OK = "OK"
PRICING_STATUS_VALIDATION_ERROR = "VALIDATION_ERROR"


@dataclass(frozen=True, slots=True)
class Product:
    id: str
    name: str
    unit_price_cents: int
    currency: str = DEFAULT_CURRENCY

    @classmethod
    def from_major_price(
        cls,
        id: str,
        name: str,
        price: Decimal | int | str,
        currency: str = DEFAULT_CURRENCY,
    ) -> Self:
        unit_price = Money.from_major(price, currency=currency)

        return cls(
            id=id,
            name=name,
            unit_price_cents=unit_price.cents,
            currency=unit_price.currency,
        )

    def __post_init__(self) -> None:
        _require_identifier(self.id, "Product.id")
        _require_non_empty_string(self.name, "Product.name")
        _require_non_negative_int(self.unit_price_cents, "Product.unit_price_cents")
        _require_non_empty_string(self.currency, "Product.currency")

    @property
    def unit_price(self) -> Money:
        return Money(cents=self.unit_price_cents, currency=self.currency)


@dataclass(frozen=True, slots=True)
class PricingRequest:
    product_id: str
    quantity: int
    customer_type: str

    def __post_init__(self) -> None:
        _require_identifier(self.product_id, "product_id")
        _require_positive_int(self.quantity, "quantity")
        _require_identifier(self.customer_type, "customer_type")

    @property
    def normalized_product_id(self) -> str:
        return normalize_identifier(self.product_id)

    @property
    def normalized_customer_type(self) -> str:
        return normalize_identifier(self.customer_type)


@dataclass(frozen=True, slots=True)
class QuantityDiscountRule:
    min_quantity: int
    discount_bps: int

    def __post_init__(self) -> None:
        _require_positive_int(self.min_quantity, "QuantityDiscountRule.min_quantity")
        validate_basis_points(self.discount_bps)


@dataclass(frozen=True, slots=True)
class PriceQuote:
    product_id: str
    product_name: str
    customer_type: str
    quantity: int
    currency: str
    unit_price_cents: int
    unit_price: str
    subtotal_cents: int
    subtotal: str
    discount_bps: int
    discount_amount_cents: int
    discount_amount: str
    total_price_cents: int
    total_price: str

    def __post_init__(self) -> None:
        _require_identifier(self.product_id, "product_id")
        _require_non_empty_string(self.product_name, "product_name")
        _require_identifier(self.customer_type, "customer_type")
        _require_positive_int(self.quantity, "quantity")
        _require_non_empty_string(self.currency, "currency")

        for field_name, value in (
            ("unit_price_cents", self.unit_price_cents),
            ("subtotal_cents", self.subtotal_cents),
            ("discount_amount_cents", self.discount_amount_cents),
            ("total_price_cents", self.total_price_cents),
        ):
            _require_non_negative_int(value, field_name)

        validate_basis_points(self.discount_bps)

        expected_total = self.subtotal_cents - self.discount_amount_cents
        if self.total_price_cents != expected_total:
            raise ValueError("total_price_cents must equal subtotal minus discount")

        expected_display_values = (
            ("unit_price", self.unit_price, self.unit_price_cents),
            ("subtotal", self.subtotal, self.subtotal_cents),
            ("discount_amount", self.discount_amount, self.discount_amount_cents),
            ("total_price", self.total_price, self.total_price_cents),
        )

        for field_name, value, cents in expected_display_values:
            _require_string(value, field_name)
            if value != cents_to_major_string(cents):
                raise ValueError(f"{field_name} must match its cents value")


@dataclass(frozen=True)
class PricingResponse:
    status: str
    error_code: str
    error_message: str
    product_id: str
    product_name: str
    customer_type: str
    quantity: int
    currency: str
    unit_price_cents: int
    unit_price: str
    subtotal_cents: int
    subtotal: str
    discount_bps: int
    discount_amount_cents: int
    discount_amount: str
    total_price_cents: int
    total_price: str

    def __post_init__(self) -> None:
        _require_non_empty_string(self.status, "status")
        _require_string(self.error_code, "error_code")
        _require_string(self.error_message, "error_message")

        if self.status == PRICING_STATUS_OK:
            if self.error_code or self.error_message:
                raise ValueError("successful pricing responses must not include errors")

            PriceQuote(
                product_id=self.product_id,
                product_name=self.product_name,
                customer_type=self.customer_type,
                quantity=self.quantity,
                currency=self.currency,
                unit_price_cents=self.unit_price_cents,
                unit_price=self.unit_price,
                subtotal_cents=self.subtotal_cents,
                subtotal=self.subtotal,
                discount_bps=self.discount_bps,
                discount_amount_cents=self.discount_amount_cents,
                discount_amount=self.discount_amount,
                total_price_cents=self.total_price_cents,
                total_price=self.total_price,
            )
        elif self.status == PRICING_STATUS_VALIDATION_ERROR:
            _require_non_empty_string(self.error_code, "error_code")
            _require_non_empty_string(self.error_message, "error_message")

            expected_defaults = {
                "product_id": "",
                "product_name": "",
                "customer_type": "",
                "quantity": 0,
                "currency": "",
                "unit_price_cents": 0,
                "unit_price": "",
                "subtotal_cents": 0,
                "subtotal": "",
                "discount_bps": 0,
                "discount_amount_cents": 0,
                "discount_amount": "",
                "total_price_cents": 0,
                "total_price": "",
            }

            for field_name, expected_value in expected_defaults.items():
                if getattr(self, field_name) != expected_value:
                    raise ValueError(
                        "validation error pricing responses must use empty quote fields"
                    )
        else:
            raise ValueError(f"Unsupported pricing response status: {self.status}")

    @classmethod
    def from_quote(cls, quote: PriceQuote) -> Self:
        return cls(
            status=PRICING_STATUS_OK,
            error_code="",
            error_message="",
            product_id=quote.product_id,
            product_name=quote.product_name,
            customer_type=quote.customer_type,
            quantity=quote.quantity,
            currency=quote.currency,
            unit_price_cents=quote.unit_price_cents,
            unit_price=quote.unit_price,
            subtotal_cents=quote.subtotal_cents,
            subtotal=quote.subtotal,
            discount_bps=quote.discount_bps,
            discount_amount_cents=quote.discount_amount_cents,
            discount_amount=quote.discount_amount,
            total_price_cents=quote.total_price_cents,
            total_price=quote.total_price,
        )

    @classmethod
    def validation_error(cls, error_code: str, error_message: str) -> Self:
        return cls(
            status=PRICING_STATUS_VALIDATION_ERROR,
            error_code=error_code,
            error_message=error_message,
            product_id="",
            product_name="",
            customer_type="",
            quantity=0,
            currency="",
            unit_price_cents=0,
            unit_price="",
            subtotal_cents=0,
            subtotal="",
            discount_bps=0,
            discount_amount_cents=0,
            discount_amount="",
            total_price_cents=0,
            total_price="",
        )


ProductCatalog = dict[str, Product]


def normalize_identifier(value: object) -> str:
    return value.strip().lower() if isinstance(value, str) else ""


def _require_string(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")

    return value


def _require_non_empty_string(value: object, field_name: str) -> str:
    text = _require_string(value, field_name)

    if not text.strip():
        raise ValueError(f"{field_name} must be a non-empty string")

    return text


def _require_identifier(value: object, field_name: str) -> str:
    text = _require_string(value, field_name)

    if not normalize_identifier(text):
        raise ValueError(f"{field_name} must be a non-empty string")

    return text


def _require_int(value: object, field_name: str) -> int:
    if type(value) is not int:
        raise TypeError(f"{field_name} must be an integer")

    return value


def _require_non_negative_int(value: object, field_name: str) -> int:
    integer = _require_int(value, field_name)

    if integer < 0:
        raise ValueError(f"{field_name} must not be negative")

    return integer


def _require_positive_int(value: object, field_name: str) -> int:
    integer = _require_int(value, field_name)

    if integer < 1:
        raise ValueError(f"{field_name} must be greater than zero")

    return integer
