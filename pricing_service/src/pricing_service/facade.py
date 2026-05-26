from .exceptions import PricingValidationError as _PricingValidationError
from .models import PricingResponse
from .service import PricingService as _PricingService


class PricingFacade:
    def __init__(self) -> None:
        self._pricing_service = _PricingService()

    def calculate_price(
        self,
        product_id: str,
        quantity: int,
        customer_type: str,
    ) -> PricingResponse:
        try:
            quote = self._pricing_service.calculate_price(
                product_id=product_id,
                quantity=quantity,
                customer_type=customer_type,
            )
        except _PricingValidationError as exc:
            return PricingResponse.validation_error(exc.error_code, str(exc))
        except Exception as exc:
            # Graft's Python runtime can load service classes separately from the
            # facade module, so isinstance checks can miss validation exceptions.
            error_code = _pricing_validation_error_code(exc)

            if error_code is None:
                raise

            return PricingResponse.validation_error(error_code, str(exc))

        return PricingResponse.from_quote(quote)


def _pricing_validation_error_code(exc: Exception) -> str | None:
    error_code = getattr(exc, "error_code", None)

    if isinstance(error_code, str) and error_code.strip():
        return error_code

    return None
