# syntax=docker/dockerfile:1

FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Evita .pyc e garante logs sem buffer
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# 1) Copia apenas os arquivos de dependências primeiro (cache de build)
COPY pyproject.toml uv.lock ./

# 2) Instala as dependências (sem instalar o projeto ainda, sem dev deps)
RUN uv sync --frozen --no-install-project --no-dev

# 3) Copia o restante do código-fonte
COPY . .

# 4) Instala o próprio projeto (se necessário) e finaliza o sync
RUN uv sync --frozen --no-dev

# Porta padrão da aplicação (pode ser sobrescrita via env PORTA)
ENV PORTA=5001
EXPOSE 5001

# Garante que o venv gerenciado pelo uv seja usado
ENV PATH="/app/.venv/bin:$PATH"

CMD ["uv", "run", "python", "controllers/main.py"]