from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    field_validator,
    model_validator,
)

from .basis_points import BasisPoints
from .models import (
    Product,
    ProductCatalog,
    QuantityDiscountRule,
    normalize_identifier,
)
from .money import DEFAULT_CURRENCY

DISCOUNTS_CONFIG_PATH_ENV = "PRICING_DISCOUNTS_CONFIG_PATH"
PRODUCTS_CONFIG_PATH_ENV = "PRICING_PRODUCTS_CONFIG_PATH"
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DISCOUNTS_CONFIG_PATH = PROJECT_ROOT / "config" / "discounts" / "default.yaml"
DEFAULT_PRODUCTS_CONFIG_PATH = PROJECT_ROOT / "config" / "products" / "default.yaml"


class QuantityDiscountConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    min_quantity: int = Field(ge=1, strict=True)
    discount_bps: BasisPoints


class PricingConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    customer_discount_bps: dict[str, BasisPoints]
    quantity_discount_bps: list[QuantityDiscountConfig] = Field(default_factory=list)
    max_discount_bps: BasisPoints

    @field_validator("customer_discount_bps", mode="before")
    @classmethod
    def normalize_customer_discount_bps(cls, value: Any) -> dict[str, Any]:
        if not isinstance(value, dict) or not value:
            raise ValueError("customer_discount_bps must be a non-empty mapping")

        return _normalize_customer_discount_keys(value)

    @field_validator("quantity_discount_bps")
    @classmethod
    def sort_quantity_discount_bps(
        cls,
        value: list[QuantityDiscountConfig],
    ) -> list[QuantityDiscountConfig]:
        thresholds = [rule.min_quantity for rule in value]

        if len(thresholds) != len(set(thresholds)):
            raise ValueError(
                "quantity_discount_bps must not contain duplicate thresholds"
            )

        return sorted(value, key=lambda rule: rule.min_quantity)


class ProductConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    unit_price_cents: int = Field(ge=0, strict=True)
    currency: str = DEFAULT_CURRENCY

    @field_validator("id", mode="before")
    @classmethod
    def normalize_product_id(cls, value: Any) -> str:
        normalized = normalize_identifier(value)

        if not normalized:
            raise ValueError("Product id must be a non-empty string")

        return normalized

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, value: Any) -> str:
        normalized = value.strip() if isinstance(value, str) else ""

        if not normalized:
            raise ValueError("Product name must be a non-empty string")

        return normalized

    @field_validator("currency", mode="before")
    @classmethod
    def validate_currency(cls, value: Any) -> str:
        normalized = value.strip() if isinstance(value, str) else ""

        if not normalized:
            raise ValueError("Product currency must be a non-empty string")

        return normalized.upper()


class ProductsConfig(RootModel[list[ProductConfig]]):
    @property
    def products(self) -> list[ProductConfig]:
        return self.root

    @field_validator("root")
    @classmethod
    def validate_products(cls, value: list[ProductConfig]) -> list[ProductConfig]:
        if not value:
            raise ValueError("Products config must contain at least one product")

        return value

    @model_validator(mode="after")
    def reject_duplicate_product_ids(self) -> ProductsConfig:
        seen_product_ids: set[str] = set()

        for product in self.products:
            if product.id in seen_product_ids:
                raise ValueError(
                    "products must not contain duplicate ids after normalization: "
                    f"{product.id}"
                )

            seen_product_ids.add(product.id)

        return self


class Config:
    discounts_path: Path
    products_path: Path
    product_catalog: ProductCatalog
    customer_discount_bps: dict[str, int]
    quantity_discount_bps: tuple[QuantityDiscountRule, ...]
    max_discount_bps: int

    def __init__(
        self,
        discounts_path: str | os.PathLike[str] | None = None,
        products_path: str | os.PathLike[str] | None = None,
    ) -> None:
        self.discounts_path = _resolve_path(
            discounts_path,
            env_var=DISCOUNTS_CONFIG_PATH_ENV,
            default_path=DEFAULT_DISCOUNTS_CONFIG_PATH,
            config_name="Discounts",
        )

        self.products_path = _resolve_path(
            products_path,
            env_var=PRODUCTS_CONFIG_PATH_ENV,
            default_path=DEFAULT_PRODUCTS_CONFIG_PATH,
            config_name="Products",
        )

        config = PricingConfig.model_validate(
            _load_yaml(self.discounts_path, config_name="Discounts")
        )

        products_config = ProductsConfig.model_validate(
            _load_yaml(self.products_path, config_name="Products")
        )

        self.product_catalog = _build_product_catalog(products_config)

        self.customer_discount_bps = config.customer_discount_bps
        self.quantity_discount_bps = tuple(
            QuantityDiscountRule(
                min_quantity=rule.min_quantity,
                discount_bps=rule.discount_bps,
            )
            for rule in config.quantity_discount_bps
        )
        self.max_discount_bps = config.max_discount_bps


def _resolve_path(
    path: str | os.PathLike[str] | None,
    *,
    env_var: str,
    default_path: Path,
    config_name: str,
) -> Path:
    env_path = os.getenv(env_var)

    candidate = Path(path or env_path or default_path)

    resolved = candidate if candidate.is_absolute() else Path.cwd() / candidate

    if resolved.suffix.lower() not in {".yaml", ".yml"}:
        raise ValueError(f"{config_name} config must be a YAML file")

    if not resolved.exists():
        raise FileNotFoundError(f"{config_name} config not found: {resolved}")

    return resolved


def _load_yaml(path: Path, *, config_name: str) -> Any:
    try:
        with path.open("r", encoding="utf-8") as config_file:
            data = yaml.safe_load(config_file) or {}
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid {config_name.lower()} config YAML: {path}") from exc

    return data


def _normalize_customer_type(value: Any) -> str:
    normalized = value.strip() if isinstance(value, str) else ""

    if not normalized:
        raise ValueError("customer_discount_bps keys must be non-empty strings")

    return normalized.lower()


def _normalize_customer_discount_keys(discounts: dict[Any, Any]) -> dict[str, Any]:
    normalized_discounts: dict[str, Any] = {}

    for customer_type, discount_bps in discounts.items():
        normalized_customer_type = _normalize_customer_type(customer_type)

        if normalized_customer_type in normalized_discounts:
            raise ValueError(
                f"Duplicate customer type after normalization: {customer_type}"
            )

        normalized_discounts[normalized_customer_type] = discount_bps

    return normalized_discounts


def _build_product_catalog(config: ProductsConfig) -> ProductCatalog:
    products = (
        Product(
            id=product.id,
            name=product.name,
            unit_price_cents=product.unit_price_cents,
            currency=product.currency,
        )
        for product in config.products
    )

    return {product.id: product for product in products}
