# https://github.com/max-pfeiffer/python-poetry/blob/main/build/Dockerfile

FROM pfeiffermax/python-poetry:1.7.0-poetry1.6.1-python3.11.6-slim-bookworm AS base


###
# Stage: build dependencies
###
FROM base AS build-deps
COPY ./poetry.lock ./pyproject.toml ./
RUN poetry install --no-interaction --no-root --without dev

###
# Stage: production
###
FROM base AS production
COPY --chown=${APP_USER}:${APP_USER} /ph8 ./ph8
CMD [ "python", "--version" ]