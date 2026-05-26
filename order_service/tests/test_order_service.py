import tomllib
from dataclasses import fields, replace
from inspect import isclass, iscoroutinefunction, signature
from pathlib import Path
from types import SimpleNamespace
from typing import cast, get_origin

import pytest

import order_service
import order_service.facade as facade_module
import order_service.pricing as pricing_module
from order_service.exceptions import (
    OrderNotFoundError,
    OrderValidationError,
    PricingUnavailableError,
)
from order_service.facade import OrderFacade
from order_service.models import OrderResult
from order_service.pricing import (
    ORDER_PRICING_HOST_ENV,
    ORDER_PRICING_MODE_ENV,
    LocalPricingProvider,
    PricingSnapshot,
    RemotePricingProvider,
    build_pricing_provider_from_env,
    pricing_snapshot_from_response,
)
from order_service.service import OrderService
from order_service.store import InMemoryOrderStore


def test_place_order_confirms_and_stores_priced_order() -> None:
    order_store = InMemoryOrderStore()
    service = OrderService(
        pricing_provider=_FakePricingProvider(_pricing_snapshot()),
        order_store=order_store,
        order_id_factory=lambda: "order-1",
    )

    result = service.place_order("mouse", 10, "premium")

    assert result == OrderResult(
        order_id="order-1",
        product_id="mouse",
        product_name="Mouse",
        customer_type="premium",
        quantity=10,
        status="CONFIRMED",
        currency="PLN",
        unit_price_cents=15000,
        unit_price="150.00",
        subtotal_cents=150000,
        subtotal="1500.00",
        discount_bps=1000,
        discount_amount_cents=15000,
        discount_amount="150.00",
        total_price_cents=135000,
        total_price="1350.00",
    )
    assert service.get_order("order-1") == result


def test_order_result_rejects_display_amounts_that_do_not_match_cents() -> None:
    with pytest.raises(ValueError, match="total_price must match its cents value"):
        replace(_order_result(), total_price="999.99")


def test_get_unknown_order_raises_not_found() -> None:
    service = OrderService(
        pricing_provider=_FakePricingProvider(_pricing_snapshot()),
        order_store=InMemoryOrderStore(),
    )

    with pytest.raises(OrderNotFoundError, match="Order not found: missing"):
        service.get_order("missing")


@pytest.mark.parametrize("quantity", [0, -1, "1", True])
def test_invalid_quantity_does_not_call_pricing_or_save(quantity: object) -> None:
    pricing_provider = _FakePricingProvider(_pricing_snapshot())
    order_store = InMemoryOrderStore()
    service = OrderService(
        pricing_provider=pricing_provider,
        order_store=order_store,
        order_id_factory=lambda: "order-1",
    )
    invalid_quantity = cast(int, quantity)

    with pytest.raises(OrderValidationError):
        service.place_order("mouse", invalid_quantity, "regular")

    assert pricing_provider.calls == []
    assert order_store.get("order-1") is None


@pytest.mark.parametrize(
    ("error", "match"),
    [
        (OrderValidationError("Unknown product_id: desk"), "Unknown product_id"),
        (
            OrderValidationError("Unsupported customer_type: wholesale"),
            "Unsupported customer_type",
        ),
    ],
)
def test_pricing_validation_error_does_not_save_order(
    error: Exception,
    match: str,
) -> None:
    order_store = InMemoryOrderStore()
    service = OrderService(
        pricing_provider=_FakePricingProvider(error=error),
        order_store=order_store,
        order_id_factory=lambda: "order-1",
    )

    with pytest.raises(OrderValidationError, match=match):
        service.place_order("desk", 1, "regular")

    assert order_store.get("order-1") is None


def test_pricing_infrastructure_error_does_not_save_order() -> None:
    order_store = InMemoryOrderStore()
    service = OrderService(
        pricing_provider=_FakePricingProvider(error=RuntimeError("connection failed")),
        order_store=order_store,
        order_id_factory=lambda: "order-1",
    )

    with pytest.raises(PricingUnavailableError, match="Pricing service failed"):
        service.place_order("mouse", 1, "regular")

    assert order_store.get("order-1") is None


def test_local_pricing_provider_maps_pricing_validation_to_order_validation() -> None:
    from pricing_service.exceptions import UnknownProductError

    class _Facade:
        def calculate_price(
            self,
            product_id: str,
            quantity: int,
            customer_type: str,
        ) -> object:
            raise UnknownProductError("desk")

    provider = LocalPricingProvider(facade=_Facade())

    with pytest.raises(OrderValidationError, match="Unknown product_id: desk"):
        provider.calculate_price("desk", 1, "regular")


def test_remote_provider_uses_config_and_reads_generated_response_shape() -> None:
    seen_configs: list[str] = []

    def _facade_factory(config: str) -> _RemoteFacade:
        seen_configs.append(config)
        return _RemoteFacade(_FakeRemotePricingResponse.ok(_pricing_snapshot()))

    provider = RemotePricingProvider(
        "name=graft.pypi.pricing_service;runtime=python;host=ws://pricing:80/ws",
        facade_factory=_facade_factory,
    )

    result = provider.calculate_price("mouse", 10, "premium")

    assert seen_configs == [
        "name=graft.pypi.pricing_service;runtime=python;host=ws://pricing:80/ws"
    ]
    assert result == _pricing_snapshot()


def test_remote_provider_maps_validation_responses() -> None:
    provider = RemotePricingProvider(
        "name=graft.pypi.pricing_service;runtime=python;host=ws://pricing:80/ws",
        facade_factory=lambda _config: _RemoteFacade(
            result=_FakeRemotePricingResponse.validation_error(
                "UNKNOWN_PRODUCT",
                "Unknown product_id: desk",
            )
        ),
    )

    with pytest.raises(
        OrderValidationError,
        match="UNKNOWN_PRODUCT: Unknown product_id: desk",
    ):
        provider.calculate_price("desk", 1, "regular")


def test_remote_provider_does_not_classify_errors_by_message() -> None:
    provider = RemotePricingProvider(
        "name=graft.pypi.pricing_service;runtime=python;host=ws://pricing:80/ws",
        facade_factory=lambda _config: _RemoteFacade(
            error=RuntimeError("Unknown product_id: desk")
        ),
    )

    with pytest.raises(PricingUnavailableError, match="Pricing service is unavailable"):
        provider.calculate_price("desk", 1, "regular")


def test_remote_provider_maps_other_errors_to_infrastructure_errors() -> None:
    provider = RemotePricingProvider(
        "name=graft.pypi.pricing_service;runtime=python;host=ws://pricing:80/ws",
        facade_factory=lambda _config: _RemoteFacade(
            error=RuntimeError("connection refused")
        ),
    )

    with pytest.raises(PricingUnavailableError, match="Pricing service is unavailable"):
        provider.calculate_price("mouse", 1, "regular")


def test_remote_provider_config_can_be_built_from_env() -> None:
    seen_configs: list[str] = []

    def _facade_factory(config: str) -> _RemoteFacade:
        seen_configs.append(config)
        return _RemoteFacade(_FakeRemotePricingResponse.ok(_pricing_snapshot()))

    provider = build_pricing_provider_from_env(
        {
            ORDER_PRICING_MODE_ENV: "REMOTE",
            ORDER_PRICING_HOST_ENV: "ws://pricing-gateway:80/ws",
        },
        remote_facade_factory=_facade_factory,
    )

    assert isinstance(provider, RemotePricingProvider)
    assert provider.calculate_price("mouse", 1, "regular") == _pricing_snapshot()
    assert seen_configs == [
        "name=graft.pypi.pricing_service;runtime=python;host=ws://pricing-gateway:80/ws"
    ]


def test_default_remote_facade_factory_sets_generated_graft_host(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _RootGraftConfig:
        host = "inmemory"

    class _NestedGraftConfig:
        host = "inmemory"

    class _GeneratedPricingFacade:
        def calculate_price(
            self,
            product_id: str,
            quantity: int,
            customer_type: str,
        ) -> object:
            raise NotImplementedError

    modules = {
        "graft_pypi_pricing_service": SimpleNamespace(GraftConfig=_RootGraftConfig),
        "graft_pypi_pricing_service.graft.pypi.pricing_service": SimpleNamespace(
            GraftConfig=_NestedGraftConfig
        ),
        "graft_pypi_pricing_service.pricingfacade": SimpleNamespace(
            PricingFacade=_GeneratedPricingFacade
        ),
    }

    def _import_module(module_name: str) -> object:
        return modules[module_name]

    monkeypatch.setattr(pricing_module.importlib, "import_module", _import_module)

    facade = pricing_module._default_remote_facade_factory(
        "name=graft.pypi.pricing_service;runtime=python;host=ws://pricing-gateway:80/ws"
    )

    assert type(facade) is _GeneratedPricingFacade
    assert _RootGraftConfig.host == "ws://pricing-gateway:80/ws"
    assert _NestedGraftConfig.host == "ws://pricing-gateway:80/ws"


def test_generated_pricing_response_adapter_requires_primitive_fields() -> None:
    result = pricing_snapshot_from_response(
        _FakeRemotePricingResponse.ok(_pricing_snapshot())
    )

    assert result == _pricing_snapshot()


def test_generated_pricing_response_adapter_rejects_missing_error_code() -> None:
    with pytest.raises(TypeError, match="must include error_code"):
        pricing_snapshot_from_response(
            _FakeRemotePricingResponse.validation_error(
                "",
                "Unknown product_id: desk",
            )
        )


def test_facade_returns_order_result_for_local_mode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ORDER_PRICING_MODE", "LOCAL")

    result = OrderFacade().place_order("mouse", 1, "regular")

    assert isinstance(result, OrderResult)
    assert result.status == "CONFIRMED"
    assert result.total_price == "150.00"


def test_order_package_exports_only_graftcode_order_surface() -> None:
    assert order_service.__all__ == ["OrderFacade", "OrderResult"]
    assert order_service.OrderFacade is OrderFacade
    assert order_service.OrderResult is OrderResult
    assert _public_facade_module_classes() == {"OrderFacade", "OrderResult"}


def test_order_facade_public_surface_is_alpha_friendly() -> None:
    public_methods = {
        name
        for name, value in vars(OrderFacade).items()
        if not name.startswith("_") and callable(value)
    }
    public_instance_attributes = {
        name for name in vars(OrderFacade()) if not name.startswith("_")
    }

    place_order = signature(OrderFacade.place_order)
    get_order = signature(OrderFacade.get_order)

    assert public_methods == {"place_order", "get_order"}
    assert public_instance_attributes == set()
    assert not iscoroutinefunction(OrderFacade.place_order)
    assert not iscoroutinefunction(OrderFacade.get_order)
    assert place_order.parameters["product_id"].annotation is str
    assert place_order.parameters["quantity"].annotation is int
    assert place_order.parameters["customer_type"].annotation is str
    assert place_order.return_annotation is OrderResult
    assert get_order.parameters["order_id"].annotation is str
    assert get_order.return_annotation is OrderResult
    assert OrderResult.__bases__ == (object,)
    assert not hasattr(OrderResult, "__slots__")
    assert not any(
        type(getattr(OrderResult, field.name, None)).__name__ == "member_descriptor"
        for field in fields(OrderResult)
    )
    assert all(get_origin(field.type) is None for field in fields(OrderResult))
    assert _order_result_field_types() == {
        "order_id": str,
        "product_id": str,
        "product_name": str,
        "customer_type": str,
        "quantity": int,
        "status": str,
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


def test_order_gateway_exposes_result_dto() -> None:
    dockerfile = Path(__file__).parents[1] / "Dockerfile"

    assert (
        "--types order_service.facade.OrderFacade,order_service.models.OrderResult"
    ) in dockerfile.read_text(encoding="utf-8")


def test_order_distribution_name_matches_python_namespace() -> None:
    pyproject = Path(__file__).parents[1] / "pyproject.toml"
    metadata = tomllib.loads(pyproject.read_text(encoding="utf-8"))

    assert metadata["project"]["name"] == "order_service"


class _FakePricingProvider:
    def __init__(
        self,
        result: PricingSnapshot | None = None,
        error: Exception | None = None,
    ) -> None:
        self._result = result
        self._error = error
        self.calls: list[tuple[str, int, str]] = []

    def calculate_price(
        self,
        product_id: str,
        quantity: int,
        customer_type: str,
    ) -> PricingSnapshot:
        self.calls.append((product_id, quantity, customer_type))

        if self._error is not None:
            raise self._error

        if self._result is None:
            raise RuntimeError("missing test result")

        return self._result


class _RemoteFacade:
    def __init__(
        self,
        result: object | None = None,
        error: Exception | None = None,
    ) -> None:
        self._result = result
        self._error = error

    def calculate_price(
        self,
        product_id: str,
        quantity: int,
        customer_type: str,
    ) -> object:
        if self._error is not None:
            raise self._error

        return self._result


class _FakeRemotePricingResponse:
    def __init__(self, values: dict[str, object]) -> None:
        self._values = values

    @classmethod
    def ok(cls, snapshot: PricingSnapshot) -> "_FakeRemotePricingResponse":
        values: dict[str, object] = {
            "status": "OK",
            "error_code": "",
            "error_message": "",
        }
        values.update(
            {
                field.name: getattr(snapshot, field.name)
                for field in fields(PricingSnapshot)
            }
        )
        return cls(values)

    @classmethod
    def validation_error(
        cls,
        error_code: str,
        error_message: str,
    ) -> "_FakeRemotePricingResponse":
        return cls(
            {
                "status": "VALIDATION_ERROR",
                "error_code": error_code,
                "error_message": error_message,
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
        )

    @property
    def instance(self) -> "_FakeRemoteInstance":
        return _FakeRemoteInstance(self._values)


class _FakeRemoteInstance:
    def __init__(self, values: dict[str, object]) -> None:
        self._values = values

    def get_instance_field(self, field_name: str) -> "_FakeRemoteValue":
        return _FakeRemoteValue(self._values[field_name])


class _FakeRemoteValue:
    def __init__(self, value: object) -> None:
        self._value = value

    def execute(self) -> "_FakeRemoteValue":
        return self

    def get_value(self) -> object:
        return self._value


def _pricing_snapshot() -> PricingSnapshot:
    return PricingSnapshot(
        product_id="mouse",
        product_name="Mouse",
        customer_type="premium",
        quantity=10,
        currency="PLN",
        unit_price_cents=15000,
        unit_price="150.00",
        subtotal_cents=150000,
        subtotal="1500.00",
        discount_bps=1000,
        discount_amount_cents=15000,
        discount_amount="150.00",
        total_price_cents=135000,
        total_price="1350.00",
    )


def _order_result() -> OrderResult:
    return OrderResult(
        order_id="order-1",
        product_id="mouse",
        product_name="Mouse",
        customer_type="premium",
        quantity=10,
        status="CONFIRMED",
        currency="PLN",
        unit_price_cents=15000,
        unit_price="150.00",
        subtotal_cents=150000,
        subtotal="1500.00",
        discount_bps=1000,
        discount_amount_cents=15000,
        discount_amount="150.00",
        total_price_cents=135000,
        total_price="1350.00",
    )


def _order_result_field_types() -> dict[str, object]:
    return {field.name: field.type for field in fields(OrderResult)}


def _public_facade_module_classes() -> set[str]:
    return {
        name
        for name, value in vars(facade_module).items()
        if not name.startswith("_") and isclass(value)
    }
