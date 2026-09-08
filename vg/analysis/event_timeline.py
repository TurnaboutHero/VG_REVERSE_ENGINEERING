"""Stream lossless event rows with verified native labels from numbered VGR sections."""

import argparse
from collections.abc import Iterable, Iterator, Sequence
from contextlib import nullcontext
from dataclasses import dataclass
import json
import math
from pathlib import Path
import re
import struct
import sys
from typing import Final, Literal, TextIO, TypeGuard, TypedDict, assert_never

from vg.core.vgr_records import VGRRecord, VGRRecordError, iter_records


APPLE_DOUBLE_MAGIC: Final = b"\x00\x05\x16\x07"
NATIVE_EVIDENCE_SHA256: Final = "c23b2e9eb201f47694c7e71ab39d2c8c96850beb4ddf489745def23927fcd891"
NATIVE_EVIDENCE: Final = "gamekindred-c23b2e9e"
END_MATCH_EVIDENCE_SHA256: Final = "659f9eed557a426db57554d2a768efe34ba9fe02ba1085d77db64390b0d92642"
END_MATCH_EVIDENCE: Final = "windows-659f9eed"
ATTRIBUTE_STATS: Final[dict[int, str]] = {0x29: "kills", 0x2A: "deaths"}
type KnownOpcode = Literal[0x03F1, 0x041C, 0x041D, 0x042B, 0x0430, 0x0431]
DEFAULT_OPCODES: Final = frozenset({0x03F1, 0x041C, 0x041D, 0x042B, 0x0430, 0x0431})
EXPECTED_CONTENT_LENGTH: Final[dict[KnownOpcode, int]] = {
    0x03F1: 8,
    0x041C: 24,
    0x041D: 16,
    0x042B: 16,
    0x0430: 16,  # Two opcode bytes plus the observed 14-byte payload.
    0x0431: 8,
}
SECTION_NAME: Final = re.compile(r"^(?P<prefix>.+)\.(?P<frame>\d+)\.vgr$")


class DecodedFields(TypedDict, total=False):
    decoding_status: str
    expected_content_length: int
    ref0: int
    ref1: int
    value: float | None
    value_bits: int
    code: int
    remaining_hex: str
    uninterpreted_bytes: list[int]
    native_evidence: str
    native_evidence_sha256: str
    native_label: str
    native_victim_id: int
    native_source_raw: int
    native_source_is_sentinel: bool
    native_class: str
    native_winning_team_id: int
    native_winning_team_raw: int
    native_end_reason: int
    native_surrender: bool
    native_type: str
    native_index: int
    native_layer: int
    native_operation: str
    native_stat: str | None
    native_flags: list[int]
    native_state_bits: int
    native_mask_a: int
    native_mask_b: int
    native_state_from: int
    native_state_to: int
    native_conditional: bool


class TimelineRow(DecodedFields):
    frame_idx: int
    record_index: int
    record_offset: int
    timestamp: float
    content_length: int
    opcode: int
    payload_hex: str


@dataclass(frozen=True, slots=True)
class TimelineInputError(ValueError):
    path: Path
    reason: str

    def __str__(self) -> str:
        return f"{self.path}: {self.reason}"


def _is_known_opcode(opcode: int) -> TypeGuard[KnownOpcode]:
    return opcode in DEFAULT_OPCODES


def _is_apple_double(path: Path) -> bool:
    with path.open("rb") as stream:
        return stream.read(4) == APPLE_DOUBLE_MAGIC


def _float_fields(payload: memoryview, offset: int) -> tuple[float | None, int]:
    raw_bits = struct.unpack_from(">I", payload, offset)[0]
    value = struct.unpack_from(">f", payload, offset)[0]
    return (value if math.isfinite(value) else None, raw_bits)


def decode_fields(record: VGRRecord) -> DecodedFields:
    """Decode only structurally confirmed fields for an exact known layout.

    ActorDie preserves the raw death source, not a credited killer. Only the
    observed 14-byte payload is decoded; its final six bytes remain opaque.
    An end-match action records a queued request, not completed-match proof.
    Reasons 5/6/7 enter validation-error paths and 8 is a no-op in this build.
    native_surrender is only the consumer's reason == 2 boolean; team IDs have
    no screen-side mapping here. Timestamp always belongs to the outer record.
    """
    if not _is_known_opcode(record.opcode):
        return {"decoding_status": "unknown_opcode"}

    expected_length = EXPECTED_CONTENT_LENGTH[record.opcode]
    if record.content_length != expected_length:
        return {
            "decoding_status": "unexpected_content_length",
            "expected_content_length": expected_length,
        }

    payload = record.payload
    match record.opcode:
        case 0x03F1:
            winning_team_raw = struct.unpack_from(">I", payload, 0)[0]
            return {
                "decoding_status": "decoded",
                "native_type": "end_match_action",
                "native_class": "Nuo::Kindred::ActionEndMatch",
                "native_winning_team_raw": winning_team_raw,
                "native_winning_team_id": winning_team_raw & 0xFF,
                "native_end_reason": payload[4],
                "native_surrender": payload[4] == 2,
                "remaining_hex": payload[5:].hex(),
                "native_evidence": END_MATCH_EVIDENCE,
                "native_evidence_sha256": END_MATCH_EVIDENCE_SHA256,
            }
        case 0x041C:
            value, raw_bits = _float_fields(payload, 8)
            return {
                "decoding_status": "decoded",
                "ref0": struct.unpack_from(">I", payload, 0)[0],
                "ref1": struct.unpack_from(">I", payload, 4)[0],
                "value": value,
                "value_bits": raw_bits,
                "code": payload[12],
                "remaining_hex": payload[13:].hex(),
                "native_evidence": NATIVE_EVIDENCE, "native_type": "attribute_update",
                "native_index": payload[12], "native_layer": payload[13],
                "native_operation": "set" if payload[14] != 0 else "add",
                "native_stat": ATTRIBUTE_STATS.get(payload[12]),
            }
        case 0x041D:
            value, raw_bits = _float_fields(payload, 4)
            return {
                "decoding_status": "decoded",
                "ref0": struct.unpack_from(">I", payload, 0)[0],
                "value": value,
                "value_bits": raw_bits,
                "code": payload[8],
                "remaining_hex": payload[9:].hex(),
                "native_evidence": NATIVE_EVIDENCE, "native_type": "resource_update",
                "native_index": payload[8], "native_operation": "set" if payload[9] != 0 else "add",
                "native_flags": [payload[10], payload[11]],
                "native_stat": "assists" if payload[8] == 0x0B else None,
            }
        case 0x042B:
            return {
                "decoding_status": "decoded",
                "ref0": struct.unpack_from(">I", payload, 0)[0],
                "uninterpreted_bytes": list(payload[4:]),
                "native_evidence": NATIVE_EVIDENCE, "native_type": "indexed_state_bits",
                "native_index": payload[4], "native_state_bits": payload[5],
                "native_mask_a": payload[6], "native_mask_b": payload[7],
            }
        case 0x0430:
            victim, source = struct.unpack_from(">II", payload, 0)
            return {
                "decoding_status": "decoded",
                "ref0": victim,
                "ref1": source,
                "native_label": "ActionActorDie",
                "native_class": "Nuo::Kindred::ActionActorDie",
                "native_type": "actor_die_action",
                "native_victim_id": victim,
                "native_source_raw": source,
                "native_source_is_sentinel": source == 0xFFFFFFFF,
                "remaining_hex": payload[8:].hex(),
                "native_evidence": END_MATCH_EVIDENCE,
                "native_evidence_sha256": END_MATCH_EVIDENCE_SHA256,
            }
        case 0x0431:
            return {
                "decoding_status": "decoded",
                "ref0": struct.unpack_from(">I", payload, 0)[0],
                "remaining_hex": payload[4:].hex(),
                "native_evidence": NATIVE_EVIDENCE, "native_type": "actor_state_transition",
                "native_state_from": 3, "native_state_to": 4,
                "native_conditional": True,
                "native_stat": None,
            }
        case unreachable:
            assert_never(unreachable)


def _discover_sections(replay_file: Path) -> list[tuple[int, Path]]:
    path = Path(replay_file)
    if not path.exists():
        raise TimelineInputError(path=path, reason="input path does not exist")
    if not path.is_file():
        raise TimelineInputError(path=path, reason="input path is not a file")

    match = SECTION_NAME.fullmatch(path.name)
    if match is None:
        raise TimelineInputError(
            path=path,
            reason="input must be a numbered .vgr section such as replay.0.vgr",
        )
    if _is_apple_double(path):
        raise TimelineInputError(path=path, reason="input is AppleDouble metadata")

    prefix = match.group("prefix")
    sections: list[tuple[int, Path]] = []
    for candidate in path.parent.iterdir():
        candidate_match = SECTION_NAME.fullmatch(candidate.name)
        if (
            not candidate.is_file()
            or candidate_match is None
            or candidate_match.group("prefix") != prefix
        ):
            continue
        if _is_apple_double(candidate):
            continue
        sections.append((int(candidate_match.group("frame")), candidate))

    sections.sort(key=lambda section: (section[0], section[1].name))
    return sections


def iter_timeline(
    replay_file: str | Path,
    opcodes: Iterable[int] | None = None,
    entity_ids: Iterable[int] | None = None,
) -> Iterator[TimelineRow]:
    """Yield selected records in numeric frame and original record order."""
    selected_opcodes = DEFAULT_OPCODES if opcodes is None else frozenset(opcodes)
    selected_entities = None if entity_ids is None else frozenset(entity_ids)

    for frame_idx, frame_path in _discover_sections(Path(replay_file)):
        data = frame_path.read_bytes()
        for record_index, record in enumerate(iter_records(data)):
            if record.opcode not in selected_opcodes:
                continue
            fields = decode_fields(record)
            if selected_entities is not None and (
                fields.get("ref0") not in selected_entities
                and fields.get("ref1") not in selected_entities
            ):
                continue
            row: TimelineRow = {
                "frame_idx": frame_idx,
                "record_index": record_index,
                "record_offset": record.offset,
                "timestamp": record.timestamp,
                "content_length": record.content_length,
                "opcode": record.opcode,
                "payload_hex": record.payload.hex(),
                **fields,
            }
            yield row


def _integer(value: str) -> int:
    try:
        return int(value, 0)
    except ValueError as error:
        raise argparse.ArgumentTypeError(f"invalid integer: {value}") from error


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Stream verified native VGR event structures as lossless JSONL.")
    parser.add_argument("path", type=Path, help="numbered .vgr replay section")
    parser.add_argument("-o", "--output", type=Path, help="write JSONL to this path")
    parser.add_argument("--opcode", action="append", type=_integer, help="opcode integer; repeat to select more (default includes 0x0430 ActionActorDie)")
    parser.add_argument("--entity", action="append", type=_integer, help="ref0/ref1 integer, including ActorDie victim/raw source; repeat to select more")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        sections = _discover_sections(args.path)
        if args.output is not None:
            output_path = args.output.resolve()
            output_match = SECTION_NAME.fullmatch(args.output.name)
            target_match = SECTION_NAME.fullmatch(output_path.name)
            input_prefix = args.path.name.rsplit(".", 2)[0]
            if (
                (output_match is not None
                 and output_match.group("prefix") == input_prefix
                 and args.output.parent.resolve() == args.path.parent.resolve())
                or (target_match is not None
                    and target_match.group("prefix") == input_prefix
                    and output_path.parent == args.path.parent.resolve())
            ):
                raise TimelineInputError(
                    path=args.output,
                    reason="output names a sibling input .vgr section",
                )
            output_exists = args.output.exists()
            if any(
                output_path == section_path.resolve()
                or (output_exists and args.output.samefile(section_path))
                for _, section_path in sections
            ):
                raise TimelineInputError(
                    path=args.output,
                    reason="output path is an input .vgr section",
                )

        output_context = (args.output.open("w", encoding="utf-8", newline="\n")
                          if args.output is not None else nullcontext(sys.stdout))
        with output_context as stream:
            rows = iter_timeline(args.path, opcodes=args.opcode, entity_ids=args.entity)
            _write_jsonl(rows, stream)
    except (OSError, TimelineInputError, VGRRecordError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 0


def _write_jsonl(rows: Iterable[TimelineRow], stream: TextIO) -> None:
    for row in rows:
        stream.write(json.dumps(row, allow_nan=False, sort_keys=True) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
