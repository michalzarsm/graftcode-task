from __future__ import annotations

import logging
from collections.abc import Callable
from uuid import uuid4

from .exceptions import (
    OrderNotFoundError,
    OrderValidationError,
    PricingUnavailableError,
)
from .models import OrderResult
from .pricing import PricingProvider, build_pricing_provider_from_env
from .store import DEFAULT_ORDER_STORE, InMemoryOrderStore

CONFIRMED_STATUS = "CONFIRMED"

logger = logging.getLogger(__name__)


class OrderService:
    def __init__(
        self,
        pricing_provider: PricingProvider | None = None,
        order_store: InMemoryOrderStore | None = None,
        order_id_factory: Callable[[], str] | None = None,
    ) -> None:
        self._pricing_provider = pricing_provider or build_pricing_provider_from_env()
        self._order_store = order_store or DEFAULT_ORDER_STORE
        self._order_id_factory = order_id_factory or _new_order_id

    def place_order(
        self,
        product_id: str,
        quantity: int,
        customer_type: str,
    ) -> OrderResult:
        _validate_order_request(product_id, quantity, customer_type)

        try:
            pricing = self._pricing_provider.calculate_price(
                product_id,
                quantity,
                customer_type,
            )
        except (OrderValidationError, PricingUnavailableError):
            raise
        except Exception as exc:
            logger.exception("Pricing dependency failed with an unexpected error")
            raise PricingUnavailableError("Pricing service failed") from exc

        order = OrderResult(
            order_id=self._order_id_factory(),
            product_id=pricing.product_id,
            product_name=pricing.product_name,
            customer_type=pricing.customer_type,
            quantity=pricing.quantity,
            status=CONFIRMED_STATUS,
            currency=pricing.currency,
            unit_price_cents=pricing.unit_price_cents,
            unit_price=pricing.unit_price,
            subtotal_cents=pricing.subtotal_cents,
            subtotal=pricing.subtotal,
            discount_bps=pricing.discount_bps,
            discount_amount_cents=pricing.discount_amount_cents,
            discount_amount=pricing.discount_amount,
            total_price_cents=pricing.total_price_cents,
            total_price=pricing.total_price,
        )

        self._order_store.save(order)

        logger.info("Order confirmed: %s", order.order_id)

        return order

    def get_order(self, order_id: str) -> OrderResult:
        _require_non_empty_string(order_id, "order_id")

        order = self._order_store.get(order_id)

        if order is None:
            raise OrderNotFoundError(order_id)

        return order


def _new_order_id() -> str:
    return uuid4().hex


def _validate_order_request(
    product_id: str,
    quantity: int,
    customer_type: str,
) -> None:
    _require_non_empty_string(product_id, "product_id")
    _require_positive_int(quantity, "quantity")
    _require_non_empty_string(customer_type, "customer_type")


def _require_non_empty_string(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise OrderValidationError(f"{field_name} must be a string")

    if not value.strip():
        raise OrderValidationError(f"{field_name} must be a non-empty string")

    return value


def _require_positive_int(value: object, field_name: str) -> int:
    if type(value) is not int:
        raise OrderValidationError(f"{field_name} must be an integer")

    if value < 1:
        raise OrderValidationError(f"{field_name} must be greater than zero")

    return value
