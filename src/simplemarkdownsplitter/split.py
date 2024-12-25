"""Main module for splitting Markdown content into smaller chunks."""

from os import linesep
from re import DOTALL, match


def split(contents: str, max_length: int, force: bool = False) -> list[str]:
    """
    Splits the given Markdown content into smaller chunks based on the specified maximum length.
    Chunks can be:
      - list entries - every paragraph in a list entry will be the same chunk
      - code blocks
      - paragraphs split with single newline characters

    By default list entries are not split if they are exceeding the ``max_length`` argument.
    Code blocks are split by lines, however by default too long lines aren't split.
    You can force splitting by setting the ``force`` argument to ``True``, however this can break
    Markdown formatting, as the chunks are simply truncated.
 
    Args:
        contents (str): The markdown content to be split.
        max_length (int): The maximum length of each chunk.
        force (bool, optional): If ``True``, forces the splitting of chunks that exceed the maximum
                                length. Can break formatting between chunks. Defaults to ``False``.

    Returns:
        list[str]: A list of markdown content chunks, each with a length up to ``max_length``.
                   If force is set to ``False`` (or default), chunks might be longer, if there's
                   no natural way of breaking them up.
    """
    chunks = split_into_chunks(contents)
    chunks = combine_chunks_to_match_max_length(chunks, max_length)
    chunks = split_too_long_code_block_chunks(chunks, max_length)
    chunks = force_split_too_long_chunks(chunks, max_length) if force else chunks
    return chunks


def split_into_chunks(contents: str) -> list[str]:
    """
    Split Markdown content into chunks, e.g.:
      - list entries
      - code blocks
      - paragraphs split with single newline characters
    
    Args:
        contents (str): The markdown content to be split.
    
    Returns:
        list[str]: A list of markdown content chunks.
    """
    chunks = [""]
    is_code_block = False
    for line in contents.splitlines():
        line = line.rstrip()
        if line.startswith("```"):
            is_code_block = not is_code_block
            if is_code_block:
                # End of a code block.
                chunks[-1] += linesep + line
            else:
                # Start of a code block.
                chunks.append(line)
        elif match(r"^\s+", line) or is_code_block or not line:
            # Part of a list, an empty line, or a code block.
            chunks[-1] += linesep + line
        else:
            # Regular line.
            chunks.append(line)
    return chunks if chunks[0] else chunks[1:]  # Remove leading empty chunk.


def combine_chunks_to_match_max_length(chunks: list[str], max_length: int) -> list[str]:
    """
    Combine multiple chunks into one, if their combined length fits in the specified maximum length.
    Chunks already bigger than the maximum length are not modified.

    Args:
        chunks (list[str]): A list of markdown content chunks.
        max_length (int): The maximum length of each chunk.
    
    Returns:
        list[str]: A list of combined markdown content chunks, if possible.
    """
    new_chunks = []
    for chunk in chunks:
        if new_chunks and (len(new_chunks[-1]) + len(chunk) + len(linesep)) <= max_length:
            new_chunks[-1] += linesep + chunk
        else:
            new_chunks.append(chunk)
    return new_chunks


def split_too_long_code_block_chunks(chunks: list[str], max_length: int) -> list[str]:
    """
    Split code block chunks that exceed the maximum length into smaller chunks.
    Code blocks are identified by triple backticks at the start and end of the block.
    Code syntax should be preserved.
    Too long code blocks are split by lines. It's possible, that chunks are still to long,
    if a single line is longer than the maximum length.

    If no chunks exceed the maximum length, the original list is returned.

    Args:
        chunks (list[str]): A list of markdown content chunks.
        max_length (int): The maximum length of each chunk.
    
    Returns:
        list[str]: A list of markdown content chunks, with shortened code blocks.
    """
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
    """
    Split single code block chunk into smaller chunks, if it exceeds the maximum length.
    Code blocks are identified by triple backticks at the start and end of the block.
    Code syntax should be preserved.
    Too long code blocks are split by lines. It's possible, that chunks are still to long,
    if a single line is longer than the maximum length.

    Args:
        chunks (list[str]): A markdown code block to split.
        max_length (int): The maximum length of each chunk.
    
    Returns:
        list[str]: A list of shortened code block chunks.
    """
    new_chunks = [""]
    chunk_lines = chunk.splitlines()
    syntax_str = chunk_lines[0]
    for line in chunk_lines:
        if len(new_chunks[-1]) + len(line) + (len(linesep) * 2) + len("```") <= max_length:
            new_chunks[-1] += line + linesep
        else:
            new_chunks[-1] += "```" + linesep
            new_chunks.append(f"{syntax_str}{linesep}{line}{linesep}")
    return new_chunks


def force_split_too_long_chunks(chunks: list[str], max_length: int) -> list[str]:
    """
    Force split too long chunks into smaller chunks, if they exceed the maximum length.
    Too long chunks are simply truncated to max length, with '...' at the end,
    so markdown formatting might be broken.

    Args:
        chunks (list[str]): A list of markdown content chunks.
        max_length (int): The maximum length of each chunk.
    
    Returns:
        list[str]: A list of markdown content chunks, with forced truncated chunks.
    """
    return (
        [c if len(c) <= max_length else c[: max_length - 3] + "..." for c in chunks]
        if any(len(chunk) > max_length for chunk in chunks)
        else chunks
    )
