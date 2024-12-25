from os import linesep
from re import DOTALL, match

from mdformat import text


def split(contents: str, *, max_length: int, format: bool = True) -> list[str]:
    contents = contents if not format else text(contents, options={"number": True})
    chunks = safe_split_into_chunks(contents)
    chunks = combine_chunks_to_match_max_length(chunks, max_length)
    chunks = split_too_long_code_block_chunks(chunks, max_length)
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


def combine_chunks_to_match_max_length(chunks: list[str], max_length: int) -> list[str]:
    new_chunks = []
    for chunk in chunks:
        if new_chunks and (len(new_chunks[-1]) + len(chunk) + len(linesep)) <= max_length:
            new_chunks[-1] += linesep + chunk
        else:
            new_chunks.append(chunk)
    return new_chunks


def split_too_long_code_block_chunks(chunks: list[str], max_length: int) -> list[str]:
    if not any(len(chunk) > max_length for chunk in chunks):
        return chunks
    new_chunks = []
    for chunk in chunks:
        if len(chunk) <= max_length or not match(r"^```.+```$", chunk, flags=DOTALL):
            new_chunks.append(chunk)
        else:
            new_chunks.extend(split_code_chunk(chunk, max_length))
    return new_chunks


def split_code_chunk(chunk: str, max_length: int) -> list[str]:
    new_chunks = [""]
    syntax_str = chunk.splitlines()[0]
    for chunk in chunk.splitlines():
        if len(new_chunks[-1]) + len(chunk) + (len(linesep) * 4) + len("```") <= max_length:
            new_chunks[-1] += chunk + linesep
        else:
            new_chunks[-1] += "```" + linesep
            new_chunks.append(f"{syntax_str}{linesep}{chunk}{linesep}")
    return new_chunks
