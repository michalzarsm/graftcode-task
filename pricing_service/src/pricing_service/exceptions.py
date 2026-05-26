from __future__ import annotations


class PricingError(Exception):
    """Base class for pricing domain errors."""


class PricingValidationError(PricingError, ValueError):
    """Base class for caller-correctable pricing validation errors."""

    error_code = "INVALID_REQUEST"


class InvalidPricingRequestError(PricingValidationError):
    """Raised when a pricing request has invalid input values."""

    error_code = "INVALID_REQUEST"

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"Invalid pricing request: {reason}")


class UnknownProductError(PricingValidationError):
    """Raised when a requested product is not configured."""

    error_code = "UNKNOWN_PRODUCT"

    def __init__(self, product_id: str) -> None:
        self.product_id = product_id
        super().__init__(f"Unknown product_id: {product_id}")


class UnsupportedCustomerTypeError(PricingValidationError):
    """Raised when customer_type has no configured pricing rule."""

    error_code = "UNSUPPORTED_CUSTOMER_TYPE"

    def __init__(self, customer_type: str) -> None:
        self.customer_type = customer_type
        super().__init__(f"Unsupported customer_type: {customer_type}")
