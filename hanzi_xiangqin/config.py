import functools

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    data_dir: str = "data"
    result_cache_ttl: int = 300


@functools.cache
def get_config() -> Config:
    return Config()
