
from os import linesep
from re import DOTALL, sub

from common import CHUNKS_SEPARATOR


def force_code_blocks_into_new_chunks(contents: str, **_) -> str:
    return sub("```", f"{CHUNKS_SEPARATOR}```", contents)


def rstrip_each_line(contents: str, **_) -> str:
    return linesep.join(line.rstrip() for line in contents.splitlines())


def truncate_line_separators(contents: str, **_) -> str:
    return sub(f"{CHUNKS_SEPARATOR}+", CHUNKS_SEPARATOR, contents).strip()


def strip_code_blocks(contents: str, **_) -> str:
    return sub(fr"(```.*?){CHUNKS_SEPARATOR}```", fr"\g<1>{linesep}```", contents, flags=DOTALL)
