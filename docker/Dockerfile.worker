FROM python:3.13.2-alpine

RUN adduser -S worker
WORKDIR /app

RUN apk add --no-cache curl
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="$PATH:/root/.local/bin"

COPY pyproject.toml uv.lock README.md ./
RUN uv sync --no-install-project --frozen --no-dev --group=worker 

COPY data data
COPY hanzi_xiangqin ./hanzi_xiangqin

USER worker

CMD [ ".venv/bin/python", "-m", "hanzi_xiangqin", "worker" ]
