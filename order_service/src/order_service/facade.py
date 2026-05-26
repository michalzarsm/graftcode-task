from .models import OrderResult
from .service import OrderService as _OrderService


class OrderFacade:
    def __init__(self) -> None:
        self._order_service = _OrderService()

    def place_order(
        self,
        product_id: str,
        quantity: int,
        customer_type: str,
    ) -> OrderResult:
        return self._order_service.place_order(
            product_id=product_id,
            quantity=quantity,
            customer_type=customer_type,
        )

    def get_order(self, order_id: str) -> OrderResult:
        return self._order_service.get_order(order_id)
