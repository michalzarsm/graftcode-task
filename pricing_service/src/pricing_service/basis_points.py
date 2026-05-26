from __future__ import annotations

from typing import Annotated, Final

from pydantic import Field

MIN_BASIS_POINTS: Final = 0
MAX_BASIS_POINTS: Final = 10_000
BASIS_POINTS_DENOMINATOR: Final = MAX_BASIS_POINTS

BasisPoints = Annotated[
    int,
    Field(ge=MIN_BASIS_POINTS, le=MAX_BASIS_POINTS, strict=True),
]


def validate_basis_points(value: int) -> None:
    if type(value) is not int:
        raise TypeError("Basis points must be an integer")

    if value < MIN_BASIS_POINTS or value > MAX_BASIS_POINTS:
        raise ValueError(
            f"Basis points must be between {MIN_BASIS_POINTS} and {MAX_BASIS_POINTS}"
        )
