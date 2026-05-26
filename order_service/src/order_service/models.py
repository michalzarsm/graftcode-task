from dataclasses import dataclass


@dataclass(frozen=True)
class OrderResult:
    order_id: str
    product_id: str
    product_name: str
    customer_type: str
    quantity: int
    status: str
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
        _require_non_empty_string(self.order_id, "order_id")
        _require_identifier(self.product_id, "product_id")
        _require_non_empty_string(self.product_name, "product_name")
        _require_identifier(self.customer_type, "customer_type")
        _require_positive_int(self.quantity, "quantity")
        _require_non_empty_string(self.status, "status")
        _require_non_empty_string(self.currency, "currency")

        for field_name, value in (
            ("unit_price_cents", self.unit_price_cents),
            ("subtotal_cents", self.subtotal_cents),
            ("discount_amount_cents", self.discount_amount_cents),
            ("total_price_cents", self.total_price_cents),
        ):
            _require_non_negative_int(value, field_name)

        _require_basis_points(self.discount_bps)

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

            if value != _cents_to_major_string(cents):
                raise ValueError(f"{field_name} must match its cents value")


def _cents_to_major_string(cents: int) -> str:
    if cents < 0:
        raise ValueError("cents must not be negative")

    return f"{cents // 100}.{cents % 100:02d}"


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


def _require_positive_int(value: object, field_name: str) -> int:
    integer = _require_int(value, field_name)

    if integer < 1:
        raise ValueError(f"{field_name} must be greater than zero")

    return integer


def _require_non_negative_int(value: object, field_name: str) -> int:
    integer = _require_int(value, field_name)

    if integer < 0:
        raise ValueError(f"{field_name} must not be negative")

    return integer


def _require_basis_points(value: object) -> int:
    integer = _require_int(value, "discount_bps")

    if integer < 0 or integer > 10000:
        raise ValueError("discount_bps must be between 0 and 10000")

    return integer
