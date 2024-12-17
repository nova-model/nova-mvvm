FROM --platform=amd64 regproxy.ornl.gov/hub_proxy/python:3.10-slim AS source

RUN apt-get update && apt-get install -y qt6-base-dev

ENV QT_QPA_PLATFORM=offscreen

ENV POETRY_CACHE_DIR=/poetry/.cache
ENV POETRY_CONFIG_DIR=/poetry/.config
ENV POETRY_HOME=/poetry

RUN pip install poetry
COPY . /src
WORKDIR /src

RUN poetry install -E pyqt5 -E pyqt6 -E panel
RUN poetry build --format=wheel

RUN chmod og+rwX -R /poetry
RUN chmod og+rwX -R /src
