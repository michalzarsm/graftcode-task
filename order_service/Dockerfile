FROM python:3.13-bookworm

ARG GRAFTCODE_GATEWAY_VERSION=v1.2.7
ARG GRAFTCODE_PRICING_INDEX_URL=https://grft.dev/simple/019e4f4d-35e9-79f9-a0b1-8a68a7ea9a56__graftcode
ARG GRAFTCODE_PRICING_PACKAGE=graft-pypi-pricing_service_ebifbb==0.2.0

WORKDIR /usr/app

RUN apt-get update \
 && apt-get install -y --no-install-recommends wget \
 && wget -O /usr/app/gg.deb https://github.com/grft-dev/graftcode-gateway/releases/download/${GRAFTCODE_GATEWAY_VERSION}/gg_linux_amd64.deb \
 && dpkg -i /usr/app/gg.deb \
 && rm /usr/app/gg.deb \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

COPY ./pricing_service /usr/app/pricing_service
COPY ./order_service /usr/app/order_service
COPY ./config /usr/app/config

ENV PRICING_DISCOUNTS_CONFIG_PATH=/usr/app/config/discounts/default.yaml \
    PRICING_PRODUCTS_CONFIG_PATH=/usr/app/config/products/default.yaml

RUN pip install --no-cache-dir --extra-index-url ${GRAFTCODE_PRICING_INDEX_URL} ${GRAFTCODE_PRICING_PACKAGE} \
 && pip install --no-cache-dir ./pricing_service \
 && pip install --no-cache-dir ./order_service

EXPOSE 80
EXPOSE 81

CMD if [ -n "$GRAFTCODE_PROJECT_KEY" ]; then \
      gg --runtime python --modules ./order_service/src --types order_service.facade.OrderFacade,order_service.models.OrderResult --projectKey "$GRAFTCODE_PROJECT_KEY"; \
    else \
      gg --runtime python --modules ./order_service/src --types order_service.facade.OrderFacade,order_service.models.OrderResult; \
    fi
