# ----------------------------
#  builder
# ----------------------------
FROM python:3.12.8-slim AS builder

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=0

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml /app

RUN uv lock && uv sync --frozen --no-dev
# ----------------------------
#  runtime
# ----------------------------
FROM python:3.12.8-slim

ENV PORT 8080
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE $PORT
VOLUME /app/resource
VOLUME /app/log
VOLUME /app/vector
VOLUME /app/storage

WORKDIR /app

COPY . /app
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder --chown=app:app /app/.venv /app/.venv

CMD uv run python /app/main.py