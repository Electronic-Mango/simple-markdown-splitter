from functools import reduce

from chunk_parsers import *
from common import CHUNKS_SEPARATOR
from initial_parsers import *

INITIAL_PARSERS = [
    force_code_blocks_into_new_chunks,
    rstrip_each_line,
    truncate_line_separators,
    strip_code_blocks,
]

CHUNK_PARSERS = [
    combine_multiparagraph_chunks,
    combine_code_blocks,
    combine_chunks_to_match_max_length,
    split_too_long_code_block_chunks,
]


def main() -> None:
    max_length = 700
    markdown = read_file()
    chunks = split(markdown, max_length=max_length)
    print(CHUNKS_SEPARATOR.join(chunks))
    print([len(chunk) for chunk in chunks])
    print()


def read_file() -> str:
    with open("markdown_example.md", "r") as file:
        return file.read()


def split(contents: str, *, max_length: int) -> list[str]:
    kwargs = {"max_length": max_length}
    contents = reduce(lambda text, func: func(text, **kwargs), INITIAL_PARSERS, contents)
    chunks = contents.split(CHUNKS_SEPARATOR)
    chunks = reduce(lambda chunk, func: func(chunk, **kwargs), CHUNK_PARSERS, chunks)
    return chunks


if __name__ == "__main__":
    main()
