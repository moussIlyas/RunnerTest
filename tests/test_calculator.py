"""Unit tests for :mod:`calculator`."""

from __future__ import annotations

import pytest

from calculator import add, divide, multiply, subtract


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (2, 3, 5),
        (-1, 1, 0),
        (0, 0, 0),
        (1.5, 2.25, 3.75),
    ],
)
def test_add(a: float, b: float, expected: float) -> None:
    assert add(a, b) == pytest.approx(expected)


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (10, 4, 6),
        (-5, -5, 0),
        (0, 7, -7),
        (2.5, 0.5, 2.0),
    ],
)
def test_subtract(a: float, b: float, expected: float) -> None:
    assert subtract(a, b) == pytest.approx(expected)


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (3, 4, 12),
        (-2, 5, -10),
        (0, 99, 0),
        (0.5, 8, 4),
    ],
)
def test_multiply(a: float, b: float, expected: float) -> None:
    assert multiply(a, b) == pytest.approx(expected)


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (10, 4, 2.5),
        (-9, 3, -3.0),
        (1, 3, 1 / 3),
        (0, 5, 0.0),
    ],
)
def test_divide(a: float, b: float, expected: float) -> None:
    assert divide(a, b) == pytest.approx(expected)


def test_divide_by_zero_raises() -> None:
    with pytest.raises(ValueError, match="cannot divide by zero"):
        divide(1, 0)
