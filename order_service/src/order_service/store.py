from __future__ import annotations

from threading import RLock

from .models import OrderResult


class InMemoryOrderStore:
    def __init__(self) -> None:
        self._orders: dict[str, OrderResult] = {}
        self._lock = RLock()

    def save(self, order: OrderResult) -> None:
        with self._lock:
            self._orders[order.order_id] = order

    def get(self, order_id: str) -> OrderResult | None:
        with self._lock:
            return self._orders.get(order_id)


DEFAULT_ORDER_STORE = InMemoryOrderStore()
