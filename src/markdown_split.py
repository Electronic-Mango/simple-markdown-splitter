from functools import reduce
from re import  match

from mdformat import text

from chunk_parsers import *

CHUNK_PARSERS = [
    combine_chunks_to_match_max_length,
    split_too_long_code_block_chunks,
]

def split(contents: str, *, max_length: int, format: bool = True) -> list[str]:
    contents = contents if not format else text(contents, options={"number": True})
    chunks = safe_split_into_chunks(contents)
    chunks = reduce(lambda c, f: f(c, max_length=max_length), CHUNK_PARSERS, chunks)
    return chunks


def safe_split_into_chunks(contents: str) -> list[str]:
    chunks = [""]
    is_code_block = False
    for line in contents.splitlines():
        line = line.rstrip()
        if match(r"^\s+", line) or not line:
            # Part of a list, or an empty line.
            chunks[-1] += linesep + line
        elif line.startswith("```") and is_code_block:
            # End of a code block.
            chunks[-1] += linesep + line
            is_code_block = False
        elif line.startswith("```"):
            # Start of a code block.
            chunks.append(line)
            is_code_block = True
        elif is_code_block:
            # Part of a code block.
            chunks[-1] += linesep + line
        else:
            # Regular line.
            chunks.append(line)
    chunks = chunks if chunks[0] else chunks[1:]  # Remove leading empty chunk.
    return chunks
