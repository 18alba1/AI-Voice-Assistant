import io
from typing import BinaryIO


def create_memory_file(content: bytes, filename: str) -> BinaryIO:
  memory_file = io.BytesIO(content)
  memory_file.name = filename
  return memory_file