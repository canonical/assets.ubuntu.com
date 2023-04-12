FROM ubuntu:focal AS base-dependencies
ENV PATH="/root/.local/bin:${PATH}"
ENV DEBIAN_FRONTEND noninteractive
ENV LANG C.UTF-8
ENV C_INCLUDE_PATH=/usr/include
# Install python and import python dependencies
RUN apt-get update && apt-get install --no-install-recommends --yes \
    python3-dev python3-pip python3-setuptools python3-wheel python3-lib2to3 \
    python3-pkg-resources ca-certificates libsodium-dev \
    # Wand dependencies
    libmagic1 libmagickwand-dev \
    # Pillow dependencies
    libtiff5-dev libjpeg8-dev libopenjp2-7-dev zlib1g-dev \
    libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python3-tk \
    libharfbuzz-dev libfribidi-dev libxcb1-dev \
    # psycopg2 dependencies
    libpq-dev

# Build stage: Install python dependencies
# ===
FROM base-dependencies AS python-dependencies
ADD requirements.txt /tmp/requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip pip3 install --user --requirement /tmp/requirements.txt

# Build stage: Install yarn dependencies
# ===
FROM node:18 AS yarn-dependencies
WORKDIR /srv
ADD package.json .
RUN --mount=type=cache,target=/usr/local/share/.cache/yarn yarn install

# Build stage: Run "yarn run build-css"
# ===
FROM yarn-dependencies AS build-css
ADD static/sass static/sass
RUN yarn run build-css

# Build the production image
# ===
FROM base-dependencies
COPY --from=python-dependencies /root/.local/lib/python3.8/site-packages /root/.local/lib/python3.8/site-packages
COPY --from=python-dependencies /root/.local/bin /root/.local/bin

# Set up environment
WORKDIR /srv

# Import code, build assets and mirror list
ADD . .
RUN rm -rf package.json yarn.lock requirements.txt
COPY --from=build-css /srv/static/css static/css

# Set revision ID
ARG BUILD_ID
ENV TALISKER_REVISION_ID "${BUILD_ID}"

# Setup commands to run server
ENTRYPOINT ["./entrypoint"]
CMD ["0.0.0.0:80"]
