set -e

docker compose -f tests/docker-compose.yml up -d
uv run coverage run --source hanzi_xiangqin -m pytest tests/ -svv
uv run coverage report -m
docker compose -f tests/docker-compose.yml down
