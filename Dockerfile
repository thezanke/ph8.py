FROM python:3.11 as base

ENV PYHTONFAULTHANDER=1 \
  PYTHONHASHSEED=random \
  PYTHONUNBUFFERED=1

WORKDIR /app

FROM base as builder

ENV PIP_DEFAULT_TIMEOUT=100 \
  PIP_DISABLE_PIP_VERSION_CHECK=1 \
  PIP_NO_CACHE_DIR=1 \
  POETRY_VERSION=1.6.1

RUN pip install "poetry==$POETRY_VERSION"
RUN python -m venv /venv

COPY pyproject.toml poetry.lock README.md ./
COPY src ./src
RUN poetry config virtualenvs.in-project true && \
    poetry install --only=main --no-root && \
    poetry build

FROM base as final 

COPY --from=builder /app/.venv ./.venv
COPY --from=builder /app/dist .
COPY --from=builder /app/src ./src
COPY docker-entrypoint.sh .

RUN ./.venv/bin/pip install *.whl
CMD ["./docker-entrypoint.sh"]
