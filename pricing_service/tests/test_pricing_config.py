from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

from pricing_service.config import Config


def test_duplicate_product_ids_fail_fast(
    write_config_files: Callable[..., tuple[Path, Path]],
) -> None:
    discounts_path, products_path = write_config_files(
        discounts_yaml="""
customer_discount_bps:
  regular: 0
quantity_discount_bps: []
max_discount_bps: 2000
""",
        products_yaml="""
- id: mouse
  name: Mouse
  unit_price_cents: 15000
- id: MOUSE
  name: Duplicate Mouse
  unit_price_cents: 16000
""",
    )

    with pytest.raises(ValueError, match="duplicate ids"):
        Config(discounts_path=discounts_path, products_path=products_path)


def test_missing_config_file_fails_fast(
    write_config_files: Callable[..., tuple[Path, Path]],
) -> None:
    discounts_path, products_path = write_config_files()

    with pytest.raises(FileNotFoundError, match="Discounts config not found"):
        Config(
            discounts_path=discounts_path.with_name("missing.yaml"),
            products_path=products_path,
        )


def test_invalid_yaml_config_fails_fast(
    write_config_files: Callable[..., tuple[Path, Path]],
) -> None:
    discounts_path, products_path = write_config_files(
        discounts_yaml="customer_discount_bps: [\n",
    )

    with pytest.raises(ValueError, match="Invalid discounts config YAML"):
        Config(discounts_path=discounts_path, products_path=products_path)


def test_invalid_discount_basis_points_config_fails_fast(
    write_config_files: Callable[..., tuple[Path, Path]],
) -> None:
    discounts_path, products_path = write_config_files(
        discounts_yaml="""
customer_discount_bps:
  regular: 10001
quantity_discount_bps: []
max_discount_bps: 2000
""",
    )

    with pytest.raises(ValueError):
        Config(discounts_path=discounts_path, products_path=products_path)


def test_duplicate_customer_types_after_normalization_fail_fast(
    write_config_files: Callable[..., tuple[Path, Path]],
) -> None:
    discounts_path, products_path = write_config_files(
        discounts_yaml="""
customer_discount_bps:
  premium: 1000
  Premium: 1500
quantity_discount_bps: []
max_discount_bps: 2000
""",
    )

    with pytest.raises(ValueError, match="Duplicate customer type"):
        Config(discounts_path=discounts_path, products_path=products_path)


def test_duplicate_quantity_discount_thresholds_fail_fast(
    write_config_files: Callable[..., tuple[Path, Path]],
) -> None:
    discounts_path, products_path = write_config_files(
        discounts_yaml="""
customer_discount_bps:
  regular: 0
quantity_discount_bps:
  - min_quantity: 10
    discount_bps: 500
  - min_quantity: 10
    discount_bps: 750
max_discount_bps: 2000
""",
    )

    with pytest.raises(ValueError, match="duplicate thresholds"):
        Config(discounts_path=discounts_path, products_path=products_path)


def test_invalid_product_config_fails_fast(
    write_config_files: Callable[..., tuple[Path, Path]],
) -> None:
    discounts_path, products_path = write_config_files(
        products_yaml="""
- id: mouse
  name: ""
  unit_price_cents: 15000
""",
    )

    with pytest.raises(ValueError, match="Product name must be a non-empty string"):
        Config(discounts_path=discounts_path, products_path=products_path)
