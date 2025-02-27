import functools

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    data_dir: str = "data"


@functools.cache
def get_config() -> Config:
    return Config()
