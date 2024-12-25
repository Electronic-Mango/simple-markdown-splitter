from os import linesep
from re import DOTALL, match


def combine_chunks_to_match_max_length(chunks: list[str], *, max_length: int, **_) -> list[str]:
    new_chunks = []
    for chunk in chunks:
        if new_chunks and (len(new_chunks[-1]) + len(chunk) + len(linesep)) <= max_length:
            new_chunks[-1] += linesep + chunk
        else:
            new_chunks.append(chunk)
    return new_chunks


def split_too_long_code_block_chunks(chunks: list[str], *, max_length: int, **_) -> list[str]:
    if not any(len(chunk) > max_length for chunk in chunks):
        return chunks
    new_chunks = []
    for chunk in chunks:
        if len(chunk) <= max_length or not match(r"^```.+```$", chunk, flags=DOTALL):
            new_chunks.append(chunk)
        else:
            new_chunks.extend(_split_code_chunk(chunk, max_length))
    return new_chunks


def _split_code_chunk(chunk: str, max_length: int) -> list[str]:
    new_chunks = [""]
    syntax_str = chunk.splitlines()[0]
    for chunk in chunk.splitlines():
        if len(new_chunks[-1]) + len(chunk) + (len(linesep) * 4) + len("```") <= max_length:
            new_chunks[-1] += chunk + linesep
        else:
            new_chunks[-1] += "```" + linesep
            new_chunks.append(f"{syntax_str}{linesep}{chunk}{linesep}")
    return new_chunks
