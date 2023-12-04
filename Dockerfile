ARG APP_USER=ph8
ARG APP_UID=1001
ARG APP_ROOT=/app
ARG APP_PORT=8118


###
# Stage: poetry base
###

FROM pfeiffermax/python-poetry:1.7.0-poetry1.6.1-python3.11.6-slim-bookworm AS base-stage

ARG APP_USER
ARG APP_UID
ARG APP_ROOT

ENV PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONPATH=$APP_ROOT \
  POETRY_VIRTUALENVS_IN_PROJECT=true \
  POETRY_CACHE_DIR="${APP_ROOT}/.cache" \
  VIRTUAL_ENVIRONMENT_PATH="${APP_ROOT}/.venv"

ENV PATH="$VIRTUAL_ENVIRONMENT_PATH/bin:$PATH"

RUN groupadd -g ${APP_UID} ${APP_USER} && \
  useradd -r -u ${APP_UID} -g ${APP_USER} ${APP_USER}

WORKDIR ${APP_ROOT}

RUN chown ${APP_USER}:${APP_USER} ${APP_ROOT}
RUN mkdir ${POETRY_CACHE_DIR} && chown ${APP_USER}:${APP_USER} ${POETRY_CACHE_DIR}


###
# Stage: build deps
###

FROM base-stage AS build-deps
COPY ./poetry.lock ./pyproject.toml ./
RUN --mount=type=cache,target=${POETRY_CACHE_DIR} \
  poetry install --no-interaction --no-root --without dev


###
# Stage: production
###

FROM base-stage AS production

LABEL org.opencontainers.image.source = "https://github.com/thezanke/ph8.py"

ARG APP_USER
ARG APP_PORT

RUN apt-get -yqq update && \
  apt-get -yqq install wget gnupg2 unzip entr && \
  wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
  sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' && \
  apt-get -yqq update && apt-get install -y google-chrome-stable

RUN wget -O /tmp/chromedriver.zip https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/119.0.6045.105/linux64/chromedriver-linux64.zip && \
  unzip /tmp/chromedriver.zip chromedriver-linux64/chromedriver -d /usr/local/bin/

ENV SELENIUM_CACHE_DIR=/home/${APP_USER}/.cache/selenium
RUN mkdir -p ${SELENIUM_CACHE_DIR} && chown ${APP_USER}:${APP_USER} ${SELENIUM_CACHE_DIR}

ENV DISPLAY=:99

COPY --chown=${APP_USER}:${APP_USER} --from=build-deps ${PYTHONPATH}/.venv ${PYTHONPATH}/.venv
COPY --chown=${APP_USER}:${APP_USER} ph8 ${PYTHONPATH}/ph8

USER ${APP_UID}
EXPOSE ${APP_PORT}

CMD ["python", "-m", "ph8.main"]
