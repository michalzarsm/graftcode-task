# Graftcode Pricing and Order Task

## Overview

The Pricing Service is implemented and covered by local tests. It exposes a
small Graftcode-facing facade plus the `PricingResponse` DTO, loads product and
discount rules from YAML configuration, validates caller input, and uses integer
cents for money values.

The Order Service exposes `OrderFacade.place_order(...)` and
`OrderFacade.get_order(...)` through Graftcode Vision. It supports both local
in-process pricing and remote pricing through the generated Pricing Graft
package. The top-level Docker Compose setup runs Order in remote mode by
default, so the order flow calls Pricing through Graftcode rather than through a
hand-written REST/gRPC client. See [docs/CONSTRAINTS.md](docs/CONSTRAINTS.md) for the
Graftcode package compatibility constraints.

## Prerequisites

- Python 3.13
- `uv`
- Docker with the Docker Compose plugin
- Network access during Docker builds, because the Dockerfiles download the
  Graftcode Gateway package and the generated Pricing Graft package

## Environment

The Compose files read `.env`. Create it in the repository root:

```env
GRAFTCODE_PROJECT_KEY=your-project-key
PRICING_GATEWAY_PORT=8080
PRICING_VISION_PORT=8081
ORDER_GATEWAY_PORT=8090
ORDER_VISION_PORT=8091

# Order pricing mode. Top-level Docker Compose defaults these to REMOTE and
# ws://pricing-gateway:80/ws when they are not set.
# ORDER_PRICING_MODE=LOCAL
# ORDER_PRICING_HOST=ws://pricing-gateway:80/ws
# ORDER_PRICING_GRAFT_CONFIG=name=graft.pypi.pricing_service;runtime=python;host=ws://pricing-gateway:80/ws

# Generated Pricing Graft package used by the Order image build.
# Set these after regenerating the Pricing Graft from Pricing Vision.
# GRAFTCODE_PRICING_INDEX_URL=https://grft.dev/simple/<project-id>__graftcode
# GRAFTCODE_PRICING_PACKAGE=<generated-pricing-graft-package>

# Optional pricing config overrides
# PRICING_PRODUCTS_CONFIG_PATH=config/products/default.yaml
# PRICING_DISCOUNTS_CONFIG_PATH=config/discounts/default.yaml
```

`GRAFTCODE_PROJECT_KEY` comes from the Graftcode portal project. The services
can start without it, but project registration and Vision integration should use
the real key.

`PRICING_PRODUCTS_CONFIG_PATH` and `PRICING_DISCOUNTS_CONFIG_PATH` are optional.
When they are not set, the Pricing Service uses the default YAML files under
`config/products` and `config/discounts`.

`ORDER_PRICING_MODE` can be `LOCAL` or `REMOTE`. `LOCAL` calls the Pricing
facade in-process. `REMOTE` calls the generated Pricing Graft package. If
`ORDER_PRICING_GRAFT_CONFIG` is set, the Order Service reads its `host=...`
entry and applies it to the generated Graft with `GraftConfig.host`. Otherwise
the Order Service builds the host setting from `ORDER_PRICING_HOST`.

## Run Gateway Containers With Docker Compose

The Compose setup can start both Gateway containers. Pricing exposes
`PricingFacade.calculate_price(...)`, and Order exposes
`OrderFacade.place_order(...)` plus `OrderFacade.get_order(...)`.

Build both images:

```bash
docker compose build
```

The Order image installs the generated Pricing Graft package during the build,
and Compose passes the package settings from `.env` into the Docker build. The
defaults expect the package name/version generated for this repository after the
updated Pricing service is registered:

```text
GRAFTCODE_PRICING_INDEX_URL=https://grft.dev/simple/019e4f4d-35e9-79f9-a0b1-8a68a7ea9a56__graftcode
GRAFTCODE_PRICING_PACKAGE=graft-pypi-pricing_service_ebifbb==0.2.0
```

If you regenerate the Pricing Graft in your own Graftcode project, set the
matching values in `.env` and then run the normal root Compose commands:

```env
GRAFTCODE_PRICING_INDEX_URL=https://grft.dev/simple/<project-id>__graftcode
GRAFTCODE_PRICING_PACKAGE=<generated-pricing-graft-package>
```

Compose cannot create that generated package during `docker compose build`.
First-time setup after a Pricing public API change is a two-step process:
start/register Pricing, copy the new package command from Pricing Vision into
`.env`, then build Order.

Start both Graftcode Gateway containers. In this mode the Order Service uses
the generated Pricing Graft against `ws://pricing-gateway:80/ws`:

```bash
docker compose up -d
```

Build and start in one command:

```bash
docker compose up -d --build
```

Check container status:

```bash
docker compose ps
```

Check Graftcode Vision endpoints:

```bash
curl -f http://127.0.0.1:8081/GV
curl -f http://127.0.0.1:8091/GV
```

Open Vision in a browser:

- Pricing Service: `http://127.0.0.1:8081/GV`
- Order Service: `http://127.0.0.1:8091/GV`

In Order Service Vision, create an `OrderFacade` and call:

```text
place_order("mouse", 10, "premium")
get_order("<order_id returned by place_order>")
```

Stop and remove the containers:

```bash
docker compose down
```

## Run One Service With Docker Compose

Pricing Service only:

```bash
docker compose -f pricing_service/compose.yml up -d --build
docker compose -f pricing_service/compose.yml down
```

Order Service only, using the mode configured in `.env` or the code default
`LOCAL`:

```bash
docker compose -f order_service/compose.yml up -d --build
docker compose -f order_service/compose.yml down
```

## Build And Run Images Directly

Build images without Compose:

```bash
docker build -f pricing_service/Dockerfile -t pricing-service-py:test .
docker build -f order_service/Dockerfile -t order-service-py:test .
```

Run Pricing Service directly:

```bash
docker run --rm --env-file .env -p 8080:80 -p 8081:81 pricing-service-py:test
```

Run Order Service directly:

```bash
docker run --rm --env-file .env -p 8090:80 -p 8091:81 order-service-py:test
```

## Local Development Checks

Install/sync workspace dependencies:

```bash
uv sync --all-packages --group dev
```

Run tests:

```bash
uv run pytest
```

Run linting:

```bash
uv run ruff check .
```

Run type checks:

```bash
uv run ty check
```

Run the full local verification set:

```bash
uv run pytest
uv run ruff check .
uv run ty check
```

## Pricing Decisions

The Pricing Service uses integer cents as the source of truth for money values.
Human-readable amount strings are derived from cents in the quote fields.

Discounts do not stack. The service evaluates all applicable discounts and
applies only the highest one. If two discounts have the same value, customer
discounts win over quantity discounts; between quantity discounts, the highest
matching quantity threshold wins.

Discount amounts are rounded to the nearest cent with half-up rounding. The
configured `max_discount_bps` is applied as a cap to the selected discount.

Invalid caller input is rejected with explicit errors:

- quantity `0` or negative quantity is invalid,
- unknown product IDs are invalid,
- unsupported customer types are invalid.

Product and discount rule configuration fails fast at startup if it is missing,
malformed, duplicated, or otherwise invalid. Zero-priced products are valid;
their totals remain zero and discounts have no monetary effect.

Internally, successful pricing calculations are represented as a success-only
`PriceQuote`. The Graftcode-facing facade returns a flat `PricingResponse`
instead: successful responses use `status="OK"`, while caller-correctable
validation failures use `status="VALIDATION_ERROR"` and stable `error_code`
values such as `INVALID_REQUEST`, `UNKNOWN_PRODUCT`, and
`UNSUPPORTED_CUSTOMER_TYPE`.

## Order Service Decisions

The Order Service keeps its business flow behind a small public
`OrderFacade`. `place_order(...)` validates caller input, asks Pricing for a
price, creates an in-memory order only after pricing succeeds, and returns an
`OrderResult` DTO with string and integer fields only. `get_order(...)` returns
confirmed in-memory orders by ID.
`OrderResult` also validates that human-readable amount strings match their
corresponding integer cent fields.

Successful orders use status `CONFIRMED`. The generated `order_id` is a UUID4
hex string. No database is used.

Order failures are raised as readable exceptions:

- invalid quantity, missing IDs and structured Pricing validation responses are
  `OrderValidationError`,
- generated Graft import/config/call failures are `PricingUnavailableError`,
- missing stored orders are `OrderNotFoundError`.

No invalid or unpriced order is persisted.

## Graftcode Boundary Decisions

The Pricing Service exposes `PricingFacade.calculate_price(...)` as the public
Graftcode-facing boundary. The facade is intentionally small, stateless and
business-oriented, while the pricing rules, config loading and validation remain
behind that boundary.

The Order Service consumes Pricing through one internal pricing provider
boundary. `LOCAL` mode calls `PricingFacade.calculate_price(...)` directly
in-process. `REMOTE` mode imports
`graft_pypi_pricing_service.pricingfacade.PricingFacade`, configures
`graft.pypi.pricing_service`, and calls Pricing through the generated Graft. A
hand-written REST, gRPC or HTTP client fallback is intentionally not included,
because that would bypass the main Graftcode requirement of the task.

The public Pricing DTO uses simple fields only: strings and integers. Discount
code labels are intentionally omitted from the public response while validating
the current Graftcode Alpha package generator behavior around collection types.
`PricingResponse` is deliberately not slotted because the Python analyzer exposes
slotted dataclass fields as descriptor objects instead of a simple DTO shape.
The Pricing package distribution name also matches the Python package namespace
(`pricing_service`) so generated Graft imports for same-package DTO return types
resolve inside the generated wheel. This keeps the exposed surface compatible
with the Alpha constraints around complex objects, collection annotations,
inheritance, async wrapper return types and stateful remote object references.
The Order package distribution name remains aligned with the Python import
namespace exposed through the Gateway: `order_service`.

Order reads `PricingResponse.status` and `PricingResponse.error_code` to
distinguish validation failures from infrastructure failures in `REMOTE` mode.
It does not classify generated Graft exceptions by matching exception message
text.

## Versioning And Compatibility

Public Graftcode methods should be treated like library APIs. Compatible changes
can be additive, for example adding optional result fields while keeping the
existing method signature stable.

Breaking changes, such as renaming `calculate_price`, changing argument types or
changing the meaning of returned fields, should be introduced through a new
facade or method version, for example `PricingFacadeV2`, while keeping the
existing facade available for consumers during migration.
