# syntax=docker/dockerfile:1

# ---- build stage: compile the challenge binary ----
FROM debian:bookworm AS build
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libc6-dev make \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /src
COPY src/ ./
RUN make

# ---- runtime stage: socat + the binary ----
FROM debian:bookworm-slim
RUN apt-get update \
    && apt-get install -y --no-install-recommends socat \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 pwn

WORKDIR /pwn
COPY --from=build /src/vuln /pwn/vuln
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod 0755 /entrypoint.sh /pwn/vuln && chown -R root:root /pwn

USER pwn
EXPOSE 9999
ENTRYPOINT ["/entrypoint.sh"]
