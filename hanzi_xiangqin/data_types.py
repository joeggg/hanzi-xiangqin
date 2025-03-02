import re
from collections import defaultdict
from dataclasses import dataclass

from .config import get_config


@dataclass
class Definition:
    pinyin: str
    text: str


@dataclass
class Hanzi:
    simplified: str
    traditional: str
    rank: int
    definitions: list[Definition]


def load_dictionary() -> dict[str, list[Definition]]:
    dictionary = defaultdict(list)
    config = get_config()
    pattern = re.compile(r"^(.) . \[(.*)\] (.*)$")
    with open(f"{config.data_dir}/cedict_ts.u8") as f:
        for line in f:
            if not (match := pattern.match(line)):
                continue

            simplified, pinyin, definition = match.groups()
            dictionary[simplified].append(Definition(pinyin, definition[1:-1]))
    return dictionary


def load_character_list() -> list[Hanzi]:
    config = get_config()
    dictionary = load_dictionary()

    with open(f"{config.data_dir}/hanzi.txt") as f:
        simplified_lines = f.readlines()

    with open(f"{config.data_dir}/hanzi_trad.txt") as f:
        traditional_lines = f.readlines()

    if len(simplified_lines) != len(traditional_lines):
        raise RuntimeError("Simplified and traditional character files have different lengths!")

    chars = []
    for i, (s_line, t_line) in enumerate(zip(simplified_lines, traditional_lines)):
        if i % 2 == 0:
            simplified = s_line.strip()
            traditional = t_line.strip()

            chars.append(
                Hanzi(
                    simplified,
                    traditional,
                    i + 1,
                    dictionary.get(simplified, dictionary.get(traditional, [])),
                )
            )

    return chars
