# Graftcode Package Compatibility

This document records the final Graftcode package and DTO constraints used by
the Pricing and Order services.

## Package Metadata

Pricing package metadata matches the Python package namespace exposed through
the Gateway:

```toml
name = "pricing_service"
version = "0.2.0"
```

Order package metadata also matches the Python package namespace exposed through
the Gateway:

```toml
name = "order_service"
version = "0.1.2"
```

Both distribution names avoid hyphens.

## Gateway Exposure

Pricing Gateway exposes only the public facade and response DTO:

```bash
--modules ./pricing_service/src \
--types pricing_service.facade.PricingFacade,pricing_service.models.PricingResponse
```

Order Gateway exposes only the public facade and result DTO:

```bash
--modules ./order_service/src \
--types order_service.facade.OrderFacade,order_service.models.OrderResult
```

## Public DTO Shape

Public DTOs are intentionally Alpha-compatible:

- `PricingResponse` and `OrderResult` are non-slotted dataclasses.
- Public DTO fields are strings and integers only.
- Graft-exposed methods are synchronous and stateless.
- Public DTOs do not expose inheritance, collection fields, async wrapper return
  types, or stateful remote object references.

`PricingResponse` is the public Pricing DTO. Successful responses use
`status="OK"`. Caller-correctable validation failures use
`status="VALIDATION_ERROR"` with stable `error_code` and `error_message` fields.

`OrderResult` is the public Order DTO. Successful orders use
`status="CONFIRMED"` and include the pricing snapshot used to confirm the order.

## Generated Pricing Graft

The Order image installs the generated Pricing Graft package during Docker
build. The top-level Compose defaults are:

```env
GRAFTCODE_PRICING_INDEX_URL=https://grft.dev/simple/019e4f4d-35e9-79f9-a0b1-8a68a7ea9a56__graftcode
GRAFTCODE_PRICING_PACKAGE=graft-pypi-pricing_service_ebifbb==0.2.0
```

When the Pricing public Graftcode API changes, regenerate the Pricing Graft from
Pricing Vision, set the matching `GRAFTCODE_PRICING_INDEX_URL` and
`GRAFTCODE_PRICING_PACKAGE` values in `.env`, then rebuild the Order image.

## Order Remote Pricing

Order uses one internal pricing provider boundary:

- `LOCAL` mode imports `pricing_service.facade.PricingFacade` and calls Pricing
  in-process.
- `REMOTE` mode imports
  `graft_pypi_pricing_service.pricingfacade.PricingFacade`, configures the
  generated Graft host, and calls Pricing through Graftcode.

There is no hand-written REST, gRPC, or HTTP fallback between Order and Pricing.
