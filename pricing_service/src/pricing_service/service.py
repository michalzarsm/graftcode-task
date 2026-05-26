from __future__ import annotations

import logging
from dataclasses import dataclass

from .basis_points import validate_basis_points
from .config import Config
from .exceptions import (
    InvalidPricingRequestError,
    UnknownProductError,
    UnsupportedCustomerTypeError,
)
from .models import PriceQuote, PricingRequest, ProductCatalog

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class _DiscountCandidate:
    code: str
    discount_bps: int
    tie_breaker_priority: int
    threshold: int = 0

    def __post_init__(self) -> None:
        validate_basis_points(self.discount_bps)


class PricingService:
    def __init__(
        self,
        config: Config | None = None,
        product_catalog: ProductCatalog | None = None,
    ) -> None:
        self.config = config or Config()

        self.product_catalog = (
            self.config.product_catalog if product_catalog is None else product_catalog
        )

        logger.info(
            "PricingService initialized with %d products",
            len(self.product_catalog),
        )

    def calculate_price(
        self,
        product_id: str,
        quantity: int,
        customer_type: str,
    ) -> PriceQuote:
        try:
            request = PricingRequest(
                product_id=product_id,
                quantity=quantity,
                customer_type=customer_type,
            )
        except (TypeError, ValueError) as exc:
            raise InvalidPricingRequestError(str(exc)) from exc

        product = self.product_catalog.get(request.normalized_product_id)

        if product is None:
            raise UnknownProductError(request.normalized_product_id)

        if request.normalized_customer_type not in self.config.customer_discount_bps:
            raise UnsupportedCustomerTypeError(request.normalized_customer_type)

        unit_price = product.unit_price

        subtotal = unit_price.multiply(request.quantity)

        selected_discount = self._select_discount(request)

        selected_discount_bps = (
            selected_discount.discount_bps if selected_discount is not None else 0
        )
        effective_discount_bps = min(
            selected_discount_bps,
            self.config.max_discount_bps,
        )

        discount_amount = subtotal.discount_amount(effective_discount_bps)

        total_price = subtotal.subtract(discount_amount)

        return PriceQuote(
            product_id=product.id,
            product_name=product.name,
            customer_type=request.normalized_customer_type,
            quantity=request.quantity,
            currency=product.currency,
            unit_price_cents=product.unit_price_cents,
            unit_price=unit_price.as_major_string(),
            subtotal_cents=subtotal.cents,
            subtotal=subtotal.as_major_string(),
            discount_bps=effective_discount_bps,
            discount_amount_cents=discount_amount.cents,
            discount_amount=discount_amount.as_major_string(),
            total_price_cents=total_price.cents,
            total_price=total_price.as_major_string(),
        )

    def _select_discount(self, request: PricingRequest) -> _DiscountCandidate | None:
        selected = _DiscountCandidate(
            code=f"customer:{request.normalized_customer_type}",
            discount_bps=self.config.customer_discount_bps[
                request.normalized_customer_type
            ],
            tie_breaker_priority=1,
        )

        for quantity_rule in self.config.quantity_discount_bps:
            if quantity_rule.min_quantity > request.quantity:
                break

            candidate = _DiscountCandidate(
                code=f"quantity:{quantity_rule.min_quantity}",
                discount_bps=quantity_rule.discount_bps,
                tie_breaker_priority=0,
                threshold=quantity_rule.min_quantity,
            )

            selected = max(selected, candidate, key=_discount_sort_key)

        return selected if selected.discount_bps > 0 else None


def _discount_sort_key(candidate: _DiscountCandidate) -> tuple[int, int, int]:
    return (
        candidate.discount_bps,
        candidate.tie_breaker_priority,
        candidate.threshold,
    )
