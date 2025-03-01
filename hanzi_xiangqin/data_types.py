from dataclasses import dataclass

from .config import get_config


@dataclass
class Hanzi:
    simplified: str
    traditional: str
    rank: int


def load_character_list() -> list[Hanzi]:
    config = get_config()

    with open(f"{config.data_dir}/hanzi.txt") as f:
        simplified_lines = f.readlines()

    with open(f"{config.data_dir}/hanzi_trad.txt") as f:
        traditional_lines = f.readlines()

    if len(simplified_lines) != len(traditional_lines):
        raise RuntimeError("Simplified and traditional character files have different lengths!")

    chars = []
    for i, (s_line, t_line) in enumerate(zip(simplified_lines, traditional_lines)):
        if i % 2 == 0:
            chars.append(Hanzi(s_line.strip(), t_line.strip(), i + 1))

    return chars
