import argparse
from collections import Counter
import json
from pathlib import Path
import sys

from vg.core.vgr_records import VGRRecordError, iter_records


APPLE_DOUBLE_MAGIC = b"\x00\x05\x16\x07"


def _candidate_files(path: Path) -> tuple[list[Path], Path]:
    if not path.exists():
        raise ValueError(f"input path does not exist: {path}")
    if path.is_file():
        if path.suffix.lower() != ".vgr":
            raise ValueError(f"input file is not a .vgr file: {path}")
        return [path], path.parent
    files = sorted(candidate for candidate in path.rglob("*.vgr") if candidate.is_file())
    if not files:
        raise ValueError(f"no .vgr files found under: {path}")
    return files, path


def audit_path(path: Path) -> dict:
    path = Path(path)
    files, relative_root = _candidate_files(path)
    opcode_counts: Counter[str] = Counter()
    length_counts: Counter[str] = Counter()
    summary = {
        "schema_version": 1,
        "files_seen": len(files),
        "replay_files": 0,
        "replay_starts": 0,
        "apple_double_files": 0,
        "files_fully_consumed": 0,
        "records": 0,
        "bytes": 0,
        "consumed_bytes": 0,
        "opcode_counts": {},
        "content_lengths": {},
        "errors": [],
    }

    for file_path in files:
        data = file_path.read_bytes()
        if data[:4] == APPLE_DOUBLE_MAGIC:
            summary["apple_double_files"] += 1
            continue

        summary["replay_files"] += 1
        summary["bytes"] += len(data)
        if file_path.name.endswith(".0.vgr"):
            summary["replay_starts"] += 1

        consumed = 0
        try:
            for record in iter_records(data):
                summary["records"] += 1
                consumed = record.offset + 8 + record.content_length
                opcode_counts[f"0x{record.opcode:04x}"] += 1
                length_counts[str(record.content_length)] += 1
        except VGRRecordError as error:
            try:
                display_path = file_path.relative_to(relative_root).as_posix()
            except ValueError:
                display_path = file_path.name
            summary["errors"].append(
                {"path": display_path, "offset": error.offset, "reason": str(error)}
            )
        else:
            summary["files_fully_consumed"] += 1
        summary["consumed_bytes"] += consumed

    summary["opcode_counts"] = dict(sorted(opcode_counts.items()))
    summary["content_lengths"] = dict(
        sorted(length_counts.items(), key=lambda item: int(item[0]))
    )
    return summary


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit raw VGR record framing without assigning gameplay semantics."
    )
    parser.add_argument("path", type=Path, help=".vgr file or directory to audit")
    parser.add_argument("-o", "--output", type=Path, help="write JSON to this path")
    return parser


def main(argv=None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.output is not None:
            files, _ = _candidate_files(args.path)
            output_path = args.output.resolve()
            for input_path in files:
                if output_path == input_path.resolve() or (
                    args.output.exists() and args.output.samefile(input_path)
                ):
                    raise ValueError("output path aliases an input replay")
        summary = audit_path(args.path)
        rendered = json.dumps(summary, indent=2, sort_keys=True) + "\n"
        if args.output:
            args.output.write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    if summary["replay_files"] == 0:
        print("error: audit contains no real replay files", file=sys.stderr)
        return 1
    if summary["errors"]:
        print("error: malformed replay framing detected", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
