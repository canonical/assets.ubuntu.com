# syntax=docker/dockerfile:experimental

FROM ubuntu:noble AS base-dependencies
ENV LANG C.UTF-8
WORKDIR /srv
ADD . .

# Install python and import python dependencies
RUN apt-get update && apt-get install --no-install-recommends --yes \
    python3-venv python3-dev python3-pip python3-setuptools python3-wheel python3-lib2to3 \
    python3-pkg-resources ca-certificates libsodium-dev \
    # Wand dependencies
    libmagic1 libmagickwand-dev \
    # Pillow dependencies
    libtiff5-dev libjpeg8-dev libopenjp2-7-dev zlib1g-dev \
    libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python3-tk \
    libharfbuzz-dev libfribidi-dev libxcb1-dev \
    # SH dependencies
    libjpeg-progs optipng\
    # psycopg2 dependencies
    libpq-dev

# Build stage: Install python dependencies
# ===
FROM base-dependencies AS python-dependencies
RUN --mount=type=cache,target=/root/.cache/pip python3 -m venv .venv \
    && . .venv/bin/activate \
    && .venv/bin/pip install -r requirements.txt

# Build stage: Install yarn dependencies
# ===
FROM node:20 AS yarn-dependencies
WORKDIR /srv
ADD . .
RUN --mount=type=cache,target=/usr/local/share/.cache/yarn yarn install

# Build stage: Run "yarn run build-css"
# ===
FROM yarn-dependencies AS build
RUN yarn build

# Build stage: Build the production image
# ===
FROM python-dependencies AS production

# Set up environment
WORKDIR /srv

# Import code, build assets and mirror list
RUN rm -rf package.json yarn.lock requirements.txt
COPY --from=build /srv/static/css static/css
COPY --from=build /srv/static/js/dist static/js/dist

# Set revision ID
ARG BUILD_ID
ENV TALISKER_REVISION_ID "${BUILD_ID}"

# Setup commands to run server
ENTRYPOINT ["./entrypoint"]
CMD ["0.0.0.0:80"]
