import io
from typing import BinaryIO


def create_memory_file(content: bytes, filename: str) -> BinaryIO:
  """Create memory file by giving file content and file name.

    Args:
      content: the content in the file.
      filename: the string of the filename.
    Returns:
      BinaryIO of a memory file.
  """
  memory_file = io.BytesIO(content)
  memory_file.name = filename
  return memory_file