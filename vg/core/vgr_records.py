from dataclasses import dataclass
import math
import struct
from typing import Iterator


class VGRRecordError(ValueError):
    def __init__(self, message: str, offset: int):
        self.offset = offset
        super().__init__(f"record at offset {offset}: {message}")


@dataclass(frozen=True)
class VGRRecord:
    offset: int
    timestamp: float
    content_length: int
    opcode: int
    payload: memoryview


def iter_records(data: bytes) -> Iterator[VGRRecord]:
    view = memoryview(data)
    offset = 0
    while offset < len(view):
        remaining = len(view) - offset
        if remaining < 8:
            raise VGRRecordError(
                f"truncated header: need 8 bytes, have {remaining}", offset
            )

        timestamp, content_length = struct.unpack_from(">fI", view, offset)
        if not math.isfinite(timestamp):
            raise VGRRecordError("non-finite timestamp", offset)
        if content_length < 2:
            raise VGRRecordError(
                f"content length {content_length} is smaller than opcode", offset
            )
        if content_length > remaining - 8:
            raise VGRRecordError(
                f"truncated body: declared {content_length} bytes, have {remaining - 8}",
                offset,
            )

        opcode = struct.unpack_from(">H", view, offset + 8)[0]
        end = offset + 8 + content_length
        yield VGRRecord(
            offset=offset,
            timestamp=timestamp,
            content_length=content_length,
            opcode=opcode,
            payload=view[offset + 10 : end],
        )
        offset = end
