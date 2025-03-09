from typing import Iterator

from ..db import Channel


def channel() -> Iterator[Channel]:
    yield Channel()
