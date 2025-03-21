from functools import cache
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    data_dir: str = "data"
    test_inactivity_timeout: int = 60
    num_workers: int = 1
    dev: bool = False

    @field_validator("dev", mode="before")
    @classmethod
    def convert_empty_string(cls, raw: Any) -> bool:
        if raw == "":
            return False
        return raw


@cache
def get_config() -> Config:
    return Config()
