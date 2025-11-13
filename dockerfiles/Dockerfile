FROM --platform=amd64 python:3.10-slim AS source

RUN apt-get update && apt-get install -y \
    curl \
    qt6-base-dev \
    wget

ENV QT_QPA_PLATFORM=offscreen

COPY . /src
WORKDIR /src

RUN curl -fsSL https://pixi.sh/install.sh | sh
ENV PATH="/root/.pixi/bin:${PATH}"
RUN pixi install
SHELL [ "pixi", "run" ]
ENTRYPOINT [ "pixi", "run" ]

RUN chmod og+rwX -R /src

FROM --platform=amd64 python:3.10-slim AS package

RUN apt update && apt install -y curl

COPY . /src
WORKDIR /src

RUN curl -fsSL https://pixi.sh/install.sh | sh
ENV PATH="/root/.pixi/bin:${PATH}"
RUN pixi install -e production
SHELL [ "pixi", "run" ]
ENTRYPOINT [ "pixi", "run" ]

RUN chmod og+rwX -R /src
