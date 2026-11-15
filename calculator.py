"""Tiny calculator used to prove that the self-hosted runner works."""

from __future__ import annotations


def add(a: float, b: float) -> float:
    """Return the sum of ``a`` and ``b``."""
    return a + b


def subtract(a: float, b: float) -> float:
    """Return ``a`` minus ``b``."""
    return a - b


def multiply(a: float, b: float) -> float:
    """Return ``a`` multiplied by ``b``."""
    return a * b


def divide(a: float, b: float) -> float:
    """Return ``a`` divided by ``b``.

    Raises:
        ValueError: if ``b`` is zero.
    """
    if b == 0:
        raise ValueError("cannot divide by zero")
    return a / b
