FROM python:3.13.2-alpine

RUN adduser -S api
WORKDIR /app

RUN apk add --no-cache curl
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="$PATH:/root/.local/bin"

COPY pyproject.toml uv.lock README.md ./
RUN uv sync --no-install-project --frozen --no-dev --group=api 

COPY hanzi_xiangqin ./hanzi_xiangqin

USER api

CMD [ ".venv/bin/python", "-m", "hanzi_xiangqin", "api" ]
