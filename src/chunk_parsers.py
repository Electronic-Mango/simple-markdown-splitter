from os import linesep
from re import DOTALL, match

from common import CHUNKS_SEPARATOR


def combine_multiparagraph_chunks(chunks: list[str], **_) -> list[str]:
    new_chunks = []
    for chunk in chunks:
        if match(r"^\s+", chunk) and new_chunks:
            new_chunks[-1] += CHUNKS_SEPARATOR + chunk
        else:
            new_chunks.append(chunk)
    return new_chunks


def combine_code_blocks(chunks: list[str], **_) -> list[str]:
    new_chunks = []
    is_code_block = False
    for chunk in chunks:
        if ("```" not in chunk and not is_code_block) or match(r"^```.+```$", chunk, flags=DOTALL):
            new_chunks.append(chunk)
        elif chunk.startswith("```") and not is_code_block:
            is_code_block = True
            new_chunks.append(chunk)
        else:
            is_code_block = not chunk.endswith("```")
            new_chunks[-1] += CHUNKS_SEPARATOR + chunk
    return new_chunks


def combine_chunks_to_match_max_length(chunks: list[str], *, max_length: int, **_) -> list[str]:
    new_chunks = []
    for chunk in chunks:
        if new_chunks and (len(new_chunks[-1]) + len(chunk) + len(CHUNKS_SEPARATOR)) <= max_length:
            new_chunks[-1] += CHUNKS_SEPARATOR + chunk
        else:
            new_chunks.append(chunk)
    return new_chunks


def split_too_long_code_block_chunks(chunks: list[str], *, max_length: int, **_) -> list[str]:
    new_chunks = []
    for chunk in chunks:
        if len(chunk) <= max_length or not match(r"^```.+```$", chunk, flags=DOTALL):
            new_chunks.append(chunk)
        else:
            new_chunks.extend(_split_code_chunk(chunk, max_length))
    return new_chunks


def _split_code_chunk(chunk: str, max_length: int) -> list[str]:
    code_block_chunks = []
    code_block_syntax = chunk.splitlines()[0]
    for code_block_chunk in chunk.splitlines():
        if not code_block_chunks:
            code_block_chunks.append(code_block_chunk)
        elif (
            len(code_block_chunks[-1])
            + len(code_block_chunk)
            + len(CHUNKS_SEPARATOR)
            + len(linesep)
            + len("```")
        ) <= max_length:
            code_block_chunks[-1] += linesep + code_block_chunk
        else:
            code_block_chunks[-1] += linesep + "```"
            code_block_chunks.append(f"{code_block_syntax}{linesep}{code_block_chunk.lstrip()}")
    return code_block_chunks
