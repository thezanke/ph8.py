ARG APP_USER=ph8
ARG APP_ROOT=/home/${APP_USER}
ARG APP_PORT=8118

###
# Stage: poetry base
###
FROM pfeiffermax/python-poetry:1.7.0-poetry1.6.1-python3.11.6-slim-bookworm AS base-stage

ARG APP_USER
ARG APP_ROOT

ENV PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONPATH=$APP_ROOT \
  POETRY_VIRTUALENVS_IN_PROJECT=true \
  POETRY_CACHE_DIR="${APP_ROOT}/.cache" \
  VIRTUAL_ENVIRONMENT_PATH="${APP_ROOT}/.venv"

ENV PATH="$VIRTUAL_ENVIRONMENT_PATH/bin:$PATH"

RUN groupadd -g 1001 ${APP_USER} && \
  useradd -r -u 1001 -g ${APP_USER} ${APP_USER}

WORKDIR ${PYTHONPATH}

RUN chown ${APP_USER}:${APP_USER} ${PYTHONPATH}
RUN mkdir ${POETRY_CACHE_DIR} && chown ${APP_USER}:${APP_USER} ${POETRY_CACHE_DIR}

###
# Stage: build deps
###
FROM base-stage AS build-deps
COPY ./poetry.lock ./pyproject.toml ./
RUN poetry install --no-interaction --without dev

###
# Stage: production
###
FROM base-stage AS production

ARG APP_USER
ARG APP_ROOT
ARG APP_PORT

COPY --chown=${APP_USER}:${APP_USER} --from=build-deps ${APP_ROOT}/.venv ${APP_ROOT}/.venv
COPY --chown=${APP_USER}:${APP_USER} ph8 ${APP_ROOT}/ph8

USER 1001

EXPOSE ${APP_PORT}

CMD ["python", "-m", "ph8.main"]