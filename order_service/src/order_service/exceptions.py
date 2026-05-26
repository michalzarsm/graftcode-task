class OrderError(Exception):
    """Base class for order service errors."""


class OrderValidationError(OrderError, ValueError):
    """Raised when an order request is invalid or rejected by pricing rules."""


class PricingUnavailableError(OrderError, RuntimeError):
    """Raised when the pricing dependency cannot be reached or used."""


class OrderNotFoundError(OrderError, LookupError):
    """Raised when an order cannot be found."""

    def __init__(self, order_id: str) -> None:
        self.order_id = order_id
        super().__init__(f"Order not found: {order_id}")
