from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

from pricing_service.config import (
    DISCOUNTS_CONFIG_PATH_ENV,
    PRODUCTS_CONFIG_PATH_ENV,
    Config,
)

DEFAULT_DISCOUNTS_YAML = """
customer_discount_bps:
  regular: 0
  premium: 1000
quantity_discount_bps:
  - min_quantity: 10
    discount_bps: 500
max_discount_bps: 2000
"""

DEFAULT_PRODUCTS_YAML = """
- id: mouse
  name: Mouse
  unit_price_cents: 15000
  currency: PLN
"""


@pytest.fixture(autouse=True)
def clear_pricing_config_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(DISCOUNTS_CONFIG_PATH_ENV, raising=False)
    monkeypatch.delenv(PRODUCTS_CONFIG_PATH_ENV, raising=False)


@pytest.fixture
def write_config_files(tmp_path: Path) -> Callable[..., tuple[Path, Path]]:
    def _write_config_files(
        *,
        discounts_yaml: str = DEFAULT_DISCOUNTS_YAML,
        products_yaml: str = DEFAULT_PRODUCTS_YAML,
    ) -> tuple[Path, Path]:
        discounts_path = tmp_path / "discounts.yaml"
        products_path = tmp_path / "products.yaml"

        discounts_path.write_text(discounts_yaml, encoding="utf-8")
        products_path.write_text(products_yaml, encoding="utf-8")

        return discounts_path, products_path

    return _write_config_files


@pytest.fixture
def write_config(
    write_config_files: Callable[..., tuple[Path, Path]],
) -> Callable[..., Config]:
    def _write_config(
        *,
        discounts_yaml: str = DEFAULT_DISCOUNTS_YAML,
        products_yaml: str = DEFAULT_PRODUCTS_YAML,
    ) -> Config:
        discounts_path, products_path = write_config_files(
            discounts_yaml=discounts_yaml,
            products_yaml=products_yaml,
        )

        return Config(discounts_path=discounts_path, products_path=products_path)

    return _write_config
