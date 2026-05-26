from __future__ import annotations

import importlib
import logging
import os
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Protocol, cast

from .exceptions import OrderValidationError, PricingUnavailableError

logger = logging.getLogger(__name__)

ORDER_PRICING_MODE_ENV = "ORDER_PRICING_MODE"
ORDER_PRICING_HOST_ENV = "ORDER_PRICING_HOST"
ORDER_PRICING_GRAFT_CONFIG_ENV = "ORDER_PRICING_GRAFT_CONFIG"
DEFAULT_ORDER_PRICING_MODE = "LOCAL"
DEFAULT_ORDER_PRICING_HOST = "ws://127.0.0.1:8080/ws"
PRICING_GRAFT_NAME = "graft.pypi.pricing_service"
PRICING_GRAFT_RUNTIME = "python"
PRICING_STATUS_OK = "OK"
PRICING_STATUS_VALIDATION_ERROR = "VALIDATION_ERROR"


@dataclass(frozen=True, slots=True)
class PricingSnapshot:
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


class PricingProvider(Protocol):
    def calculate_price(
        self,
        product_id: str,
        quantity: int,
        customer_type: str,
    ) -> PricingSnapshot: ...


class _PricingFacadeLike(Protocol):
    def calculate_price(
        self,
        product_id: str,
        quantity: int,
        customer_type: str,
    ) -> object: ...


class LocalPricingProvider:
    def __init__(self, facade: _PricingFacadeLike | None = None) -> None:
        self._facade = facade

    def calculate_price(
        self,
        product_id: str,
        quantity: int,
        customer_type: str,
    ) -> PricingSnapshot:
        try:
            facade = self._get_facade()

            response = facade.calculate_price(product_id, quantity, customer_type)

            return pricing_snapshot_from_response(response)
        except OrderValidationError:
            raise
        except Exception as exc:
            if _is_local_pricing_validation_error(exc):
                raise OrderValidationError(str(exc)) from exc

            logger.exception("Local pricing call failed")

            raise PricingUnavailableError("Pricing service failed") from exc

    def _get_facade(self) -> _PricingFacadeLike:
        if self._facade is None:
            facade_module = importlib.import_module("pricing_service.facade")

            self._facade = facade_module.PricingFacade()

        return self._facade


class RemotePricingProvider:
    def __init__(
        self,
        config: str,
        facade_factory: Callable[[str], _PricingFacadeLike] | None = None,
    ) -> None:
        self._config = config
        self._facade_factory = facade_factory or _default_remote_facade_factory
        self._facade: _PricingFacadeLike | None = None

    def calculate_price(
        self,
        product_id: str,
        quantity: int,
        customer_type: str,
    ) -> PricingSnapshot:
        try:
            facade = self._get_facade()

            response = facade.calculate_price(product_id, quantity, customer_type)

            return pricing_snapshot_from_response(response)
        except OrderValidationError:
            raise
        except Exception as exc:
            logger.exception("Remote pricing call failed")

            raise PricingUnavailableError("Pricing service is unavailable") from exc

    def _get_facade(self) -> _PricingFacadeLike:
        if self._facade is None:
            self._facade = self._facade_factory(self._config)

        return self._facade


def build_pricing_provider_from_env(
    env: Mapping[str, str] | None = None,
    *,
    remote_facade_factory: Callable[[str], _PricingFacadeLike] | None = None,
) -> PricingProvider:
    source = os.environ if env is None else env
    mode = (
        source.get(ORDER_PRICING_MODE_ENV, DEFAULT_ORDER_PRICING_MODE).strip().upper()
    )

    if mode == "LOCAL":
        return LocalPricingProvider()

    if mode == "REMOTE":
        return RemotePricingProvider(
            _build_remote_config(source),
            facade_factory=remote_facade_factory,
        )

    raise ValueError(f"{ORDER_PRICING_MODE_ENV} must be LOCAL or REMOTE, got {mode!r}")


def pricing_snapshot_from_response(response: object) -> PricingSnapshot:
    status = _read_string_field(response, "status")

    if status == PRICING_STATUS_VALIDATION_ERROR:
        error_code = _read_string_field(response, "error_code")
        error_message = _read_string_field(response, "error_message")

        if not error_code.strip():
            raise TypeError("Pricing validation response must include error_code")

        if not error_message.strip():
            raise TypeError("Pricing validation response must include error_message")

        raise OrderValidationError(f"{error_code}: {error_message}")

    if status != PRICING_STATUS_OK:
        raise TypeError(f"Unknown pricing response status: {status}")

    error_code = _read_string_field(response, "error_code")
    error_message = _read_string_field(response, "error_message")

    if error_code or error_message:
        raise TypeError("Successful pricing response must not include errors")

    return PricingSnapshot(
        product_id=_read_string_field(response, "product_id"),
        product_name=_read_string_field(response, "product_name"),
        customer_type=_read_string_field(response, "customer_type"),
        quantity=_read_int_field(response, "quantity"),
        currency=_read_string_field(response, "currency"),
        unit_price_cents=_read_int_field(response, "unit_price_cents"),
        unit_price=_read_string_field(response, "unit_price"),
        subtotal_cents=_read_int_field(response, "subtotal_cents"),
        subtotal=_read_string_field(response, "subtotal"),
        discount_bps=_read_int_field(response, "discount_bps"),
        discount_amount_cents=_read_int_field(response, "discount_amount_cents"),
        discount_amount=_read_string_field(response, "discount_amount"),
        total_price_cents=_read_int_field(response, "total_price_cents"),
        total_price=_read_string_field(response, "total_price"),
    )


def _build_remote_config(source: Mapping[str, str]) -> str:
    explicit_config = source.get(ORDER_PRICING_GRAFT_CONFIG_ENV)

    if explicit_config is not None and explicit_config.strip():
        return explicit_config.strip()

    host = source.get(ORDER_PRICING_HOST_ENV, DEFAULT_ORDER_PRICING_HOST).strip()

    if not host:
        host = DEFAULT_ORDER_PRICING_HOST

    return f"name={PRICING_GRAFT_NAME};runtime={PRICING_GRAFT_RUNTIME};host={host}"


def _default_remote_facade_factory(config: str) -> _PricingFacadeLike:
    _configure_generated_pricing_graft(_host_from_graft_config(config))

    facade_module = importlib.import_module("graft_pypi_pricing_service.pricingfacade")

    return cast(_PricingFacadeLike, facade_module.PricingFacade())


def _configure_generated_pricing_graft(host: str) -> None:
    seen_configs: list[object] = []

    for module_name in (
        "graft_pypi_pricing_service",
        "graft_pypi_pricing_service.graft.pypi.pricing_service",
    ):
        try:
            config_module = importlib.import_module(module_name)
        except ImportError:
            if module_name == "graft_pypi_pricing_service":
                continue
            raise

        graft_config = getattr(config_module, "GraftConfig", None)

        if graft_config is None or any(
            graft_config is seen_config for seen_config in seen_configs
        ):
            continue

        setattr(graft_config, "host", host)

        seen_configs.append(graft_config)

    if not seen_configs:
        raise ImportError("Generated Pricing Graft package does not expose GraftConfig")


def _host_from_graft_config(config: str) -> str:
    for part in config.split(";"):
        key, separator, value = part.partition("=")

        if separator and key.strip() == "host" and value.strip():
            return value.strip()

    return DEFAULT_ORDER_PRICING_HOST


def _read_string_field(result: object, field_name: str) -> str:
    value = _read_result_field(result, field_name)

    if not isinstance(value, str):
        raise TypeError(f"Pricing response field {field_name!r} must be a string")

    return value


def _read_int_field(result: object, field_name: str) -> int:
    value = _read_result_field(result, field_name)

    if type(value) is not int:
        raise TypeError(f"Pricing response field {field_name!r} must be an integer")

    return value


def _read_result_field(result: object, field_name: str) -> object:
    if hasattr(result, field_name):
        return getattr(result, field_name)

    instance = getattr(result, "instance", None)

    if instance is None or not hasattr(instance, "get_instance_field"):
        raise TypeError(f"Pricing response has no field {field_name!r}")

    return instance.get_instance_field(field_name).execute().get_value()


def _is_local_pricing_validation_error(exc: Exception) -> bool:
    try:
        exceptions_module = importlib.import_module("pricing_service.exceptions")
    except ImportError:
        return False

    return isinstance(exc, exceptions_module.PricingValidationError)
