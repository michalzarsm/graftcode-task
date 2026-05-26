from __future__ import annotations

import tomllib
from collections.abc import Callable
from dataclasses import fields
from inspect import isclass, iscoroutinefunction, signature
from pathlib import Path
from typing import cast, get_origin

import pytest

import pricing_service
import pricing_service.facade as facade_module
from pricing_service.config import Config
from pricing_service.exceptions import (
    InvalidPricingRequestError,
    PricingValidationError,
    UnknownProductError,
    UnsupportedCustomerTypeError,
)
from pricing_service.facade import PricingFacade
from pricing_service.models import PriceQuote, PricingResponse
from pricing_service.service import PricingService


def test_regular_customer_has_no_discount() -> None:
    result = PricingService().calculate_price("mouse", 1, "regular")

    assert result == PriceQuote(
        product_id="mouse",
        product_name="Mouse",
        customer_type="regular",
        quantity=1,
        currency="PLN",
        unit_price_cents=15000,
        unit_price="150.00",
        subtotal_cents=15000,
        subtotal="150.00",
        discount_bps=0,
        discount_amount_cents=0,
        discount_amount="0.00",
        total_price_cents=15000,
        total_price="150.00",
    )


def test_premium_customer_discount() -> None:
    result = PricingService().calculate_price("keyboard", 1, "premium")

    assert result.discount_bps == 1000
    assert result.discount_amount_cents == 3000
    assert result.total_price_cents == 27000


def test_quantity_discount() -> None:
    result = PricingService().calculate_price("mouse", 10, "regular")

    assert result.subtotal_cents == 150000
    assert result.discount_bps == 500
    assert result.discount_amount_cents == 7500
    assert result.total_price_cents == 142500


def test_quantity_below_threshold_has_no_quantity_discount() -> None:
    result = PricingService().calculate_price("mouse", 9, "regular")

    assert result.discount_bps == 0
    assert result.discount_amount_cents == 0


def test_discounts_do_not_stack() -> None:
    result = PricingService().calculate_price("mouse", 10, "premium")

    assert result.discount_bps == 1000
    assert result.discount_amount_cents == 15000
    assert result.total_price_cents == 135000


def test_max_discount_caps_selected_discount(
    write_config: Callable[..., Config],
) -> None:
    config = write_config(
        discounts_yaml="""
customer_discount_bps:
  premium: 3000
quantity_discount_bps: []
max_discount_bps: 2000
""",
    )

    result = PricingService(config=config).calculate_price("mouse", 1, "premium")

    assert result.discount_bps == 2000
    assert result.discount_amount_cents == 3000
    assert result.total_price_cents == 12000


def test_discount_tie_prefers_customer_discount(
    write_config: Callable[..., Config],
) -> None:
    config = write_config(
        discounts_yaml="""
customer_discount_bps:
  premium: 1000
quantity_discount_bps:
  - min_quantity: 10
    discount_bps: 1000
max_discount_bps: 2000
""",
    )

    result = PricingService(config=config).calculate_price("mouse", 10, "premium")

    assert result.discount_bps == 1000


def test_quantity_discount_tie_prefers_highest_threshold(
    write_config: Callable[..., Config],
) -> None:
    config = write_config(
        discounts_yaml="""
customer_discount_bps:
  regular: 0
quantity_discount_bps:
  - min_quantity: 10
    discount_bps: 500
  - min_quantity: 20
    discount_bps: 500
max_discount_bps: 2000
""",
    )

    result = PricingService(config=config).calculate_price("mouse", 20, "regular")

    assert result.discount_bps == 500


def test_product_and_customer_identifiers_are_normalized() -> None:
    result = PricingService().calculate_price(" MOUSE ", 1, " Premium ")

    assert result.product_id == "mouse"
    assert result.customer_type == "premium"
    assert result.discount_bps == 1000


def test_unknown_product_raises_domain_error() -> None:
    with pytest.raises(UnknownProductError, match="Unknown product_id: desk") as exc:
        PricingService().calculate_price("desk", 1, "regular")

    assert exc.value.product_id == "desk"
    assert isinstance(exc.value, PricingValidationError)


def test_discount_amount_uses_half_up_rounding(
    write_config: Callable[..., Config],
) -> None:
    config = write_config(
        discounts_yaml="""
customer_discount_bps:
  premium: 5000
quantity_discount_bps: []
max_discount_bps: 10000
""",
        products_yaml="""
- id: tiny
  name: Tiny
  unit_price_cents: 1
  currency: PLN
""",
    )

    result = PricingService(config=config).calculate_price("tiny", 1, "premium")

    assert result.discount_amount_cents == 1
    assert result.total_price_cents == 0


@pytest.mark.parametrize("quantity", [0, -1])
def test_non_positive_quantity_is_invalid(quantity: int) -> None:
    with pytest.raises(
        InvalidPricingRequestError,
        match="Invalid pricing request: quantity must be greater than zero",
    ) as exc:
        PricingService().calculate_price("mouse", quantity, "regular")

    assert exc.value.reason == "quantity must be greater than zero"
    assert isinstance(exc.value, PricingValidationError)


@pytest.mark.parametrize("quantity", ["1", True])
def test_non_integer_quantity_is_invalid(quantity: object) -> None:
    invalid_quantity = cast(int, quantity)

    with pytest.raises(
        InvalidPricingRequestError,
        match="Invalid pricing request: quantity must be an integer",
    ) as exc:
        PricingService().calculate_price("mouse", invalid_quantity, "regular")

    assert exc.value.reason == "quantity must be an integer"
    assert isinstance(exc.value, PricingValidationError)


def test_unsupported_customer_type_raises_domain_error() -> None:
    with pytest.raises(
        UnsupportedCustomerTypeError,
        match="Unsupported customer_type: wholesale",
    ) as exc:
        PricingService().calculate_price("mouse", 1, "wholesale")

    assert exc.value.customer_type == "wholesale"
    assert isinstance(exc.value, PricingValidationError)


def test_zero_priced_product_is_valid(write_config: Callable[..., Config]) -> None:
    config = write_config(
        products_yaml="""
- id: freebie
  name: Freebie
  unit_price_cents: 0
  currency: PLN
""",
    )

    result = PricingService(config=config).calculate_price("freebie", 3, "premium")

    assert result.unit_price_cents == 0
    assert result.subtotal_cents == 0
    assert result.discount_bps == 1000
    assert result.discount_amount_cents == 0
    assert result.total_price_cents == 0


def test_facade_returns_primitive_response_dto_for_success() -> None:
    response = PricingFacade().calculate_price("mouse", 1, "regular")

    non_primitive_fields = {
        field.name
        for field in fields(PricingResponse)
        if not isinstance(getattr(response, field.name), str | int)
    }

    assert isinstance(response, PricingResponse)
    assert response.status == "OK"
    assert response.error_code == ""
    assert response.error_message == ""
    assert response.unit_price == "150.00"
    assert response.total_price == "150.00"
    assert non_primitive_fields == set()


@pytest.mark.parametrize(
    ("product_id", "quantity", "customer_type", "error_code"),
    [
        ("desk", 1, "regular", "UNKNOWN_PRODUCT"),
        ("mouse", 0, "regular", "INVALID_REQUEST"),
        ("mouse", 1, "wholesale", "UNSUPPORTED_CUSTOMER_TYPE"),
    ],
)
def test_facade_returns_validation_error_response(
    product_id: str,
    quantity: int,
    customer_type: str,
    error_code: str,
) -> None:
    response = PricingFacade().calculate_price(product_id, quantity, customer_type)

    assert response.status == "VALIDATION_ERROR"
    assert response.error_code == error_code
    assert response.error_message
    assert response.product_id == ""
    assert response.quantity == 0
    assert response.total_price_cents == 0


def test_facade_maps_validation_errors_loaded_by_graft_runtime(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        facade_module,
        "_PricingService",
        lambda: _FakePricingService(
            _ReloadedPricingValidationError(
                "UNKNOWN_PRODUCT",
                "Unknown product_id: desk",
            )
        ),
    )

    response = PricingFacade().calculate_price("desk", 1, "regular")

    assert response.status == "VALIDATION_ERROR"
    assert response.error_code == "UNKNOWN_PRODUCT"
    assert response.error_message == "Unknown product_id: desk"


def test_facade_does_not_map_unexpected_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        facade_module,
        "_PricingService",
        lambda: _FakePricingService(RuntimeError("database unavailable")),
    )

    with pytest.raises(RuntimeError, match="database unavailable"):
        PricingFacade().calculate_price("mouse", 1, "regular")


def test_package_exports_only_graftcode_pricing_surface() -> None:
    assert pricing_service.__all__ == ["PricingFacade", "PricingResponse"]
    assert pricing_service.PricingFacade is PricingFacade
    assert pricing_service.PricingResponse is PricingResponse
    assert "PricingService" not in vars(facade_module)
    assert _public_facade_module_classes() == {"PricingFacade", "PricingResponse"}


def test_facade_public_surface_is_alpha_friendly() -> None:
    public_methods = {
        name
        for name, value in vars(PricingFacade).items()
        if not name.startswith("_") and callable(value)
    }
    public_instance_attributes = {
        name for name in vars(PricingFacade()) if not name.startswith("_")
    }

    calculate_price = signature(PricingFacade.calculate_price)
    parameters = calculate_price.parameters

    assert public_methods == {"calculate_price"}
    assert public_instance_attributes == set()
    assert not iscoroutinefunction(PricingFacade.calculate_price)
    assert parameters["product_id"].annotation is str
    assert parameters["quantity"].annotation is int
    assert parameters["customer_type"].annotation is str
    assert calculate_price.return_annotation is PricingResponse
    assert PricingResponse.__bases__ == (object,)
    assert not hasattr(PricingResponse, "__slots__")
    assert not any(
        type(getattr(PricingResponse, field.name, None)).__name__ == "member_descriptor"
        for field in fields(PricingResponse)
    )
    assert all(get_origin(field.type) is None for field in fields(PricingResponse))
    assert _pricing_response_field_types() == {
        "status": str,
        "error_code": str,
        "error_message": str,
        "product_id": str,
        "product_name": str,
        "customer_type": str,
        "quantity": int,
        "currency": str,
        "unit_price_cents": int,
        "unit_price": str,
        "subtotal_cents": int,
        "subtotal": str,
        "discount_bps": int,
        "discount_amount_cents": int,
        "discount_amount": str,
        "total_price_cents": int,
        "total_price": str,
    }


def test_pricing_gateway_exposes_result_dto() -> None:
    dockerfile = Path(__file__).parents[1] / "Dockerfile"

    assert (
        "--types pricing_service.facade.PricingFacade,"
        "pricing_service.models.PricingResponse"
    ) in dockerfile.read_text(encoding="utf-8")


def test_pricing_distribution_name_matches_python_namespace() -> None:
    pyproject = Path(__file__).parents[1] / "pyproject.toml"
    metadata = tomllib.loads(pyproject.read_text(encoding="utf-8"))

    assert metadata["project"]["name"] == "pricing_service"


def _pricing_response_field_types() -> dict[str, object]:
    return {field.name: field.type for field in fields(PricingResponse)}


class _ReloadedPricingValidationError(Exception):
    def __init__(self, error_code: str, message: str) -> None:
        self.error_code = error_code
        super().__init__(message)


class _FakePricingService:
    def __init__(self, error: Exception) -> None:
        self._error = error

    def calculate_price(
        self,
        product_id: str,
        quantity: int,
        customer_type: str,
    ) -> PriceQuote:
        raise self._error


def _public_facade_module_classes() -> set[str]:
    return {
        name
        for name, value in vars(facade_module).items()
        if not name.startswith("_") and isclass(value)
    }
