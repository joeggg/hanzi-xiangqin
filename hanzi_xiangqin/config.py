import functools
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    data_dir: str = "data"
    result_cache_ttl: int = 600
    test_timeout: int = 3600
    answer_timeout: int = 60
    num_workers: int = 1
    dev: bool = False

    @field_validator("dev", mode="before")
    @classmethod
    def convert_empty_string(cls, raw: Any) -> bool:
        if raw == "":
            return False
        return raw


@functools.cache
def get_config() -> Config:
    return Config()
