FROM python:3.14-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates openssh-client procps sudo \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -s /bin/bash vscode \
    && echo 'vscode ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/vscode
USER vscode
