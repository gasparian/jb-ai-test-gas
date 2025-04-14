FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    curl \
    wget \
    git \
    sudo \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libxml2-dev \
    libxmlsec1-dev \
    libffi-dev \
    liblzma-dev \
    && rm -rf /var/lib/apt/lists/*

ENV PYENV_ROOT=/root/.pyenv
ENV PATH=$PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH
RUN curl https://pyenv.run | bash

RUN pyenv install 3.12 && pyenv global 3.12

ENV PATH=/root/.local/bin:$PATH

WORKDIR /app

# Ensure /app is fully writable
RUN mkdir -p /app && chown -R root:root /app && chmod -R 777 /app
# Configure sudo to not require a password
RUN echo "root ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

COPY env-setuper env-setuper
RUN pip install env-setuper/dist/env_setuper-0.1.0-py3-none-any.whl

# Copy test applications code
COPY python-mnist python-mnist
COPY rust_web_service rust_web_service
COPY rust_web_service_f rust_web_service_f


ENTRYPOINT ["/bin/bash"]