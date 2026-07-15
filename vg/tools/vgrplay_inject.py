"""Inject a source replay into the live temp replay slot using vgrplay."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


DEFAULT_VGRPLAY = (
    r"D:\Desktop\My Folder\Game\VG\vg replay\vaingloryreplay-master\windows_amd64\vgrplay.exe"
)


def _replay_name_from_vgr(path: Path) -> Optional[str]:
    if path.suffix != ".vgr":
        return None
    stem = path.stem
    name, dot, frame = stem.rpartition(".")
    if not dot or not frame.isdigit():
        return None
    return name


def _frame_index(path: Path) -> Optional[int]:
    if path.suffix != ".vgr":
        return None
    frame = path.stem.rsplit(".", 1)[-1]
    return int(frame) if frame.isdigit() else None


def _group_replay_frames(directory: Path) -> Dict[str, Dict[int, Path]]:
    groups: Dict[str, Dict[int, Path]] = {}
    for path in directory.glob("*.vgr"):
        name = _replay_name_from_vgr(path)
        frame = _frame_index(path)
        if name is None or frame is None:
            continue
        groups.setdefault(name, {})[frame] = path
    return groups


def _frame_summary(frames: Dict[int, Path]) -> Dict[str, object]:
    if not frames:
        return {
            "frame_count": 0,
            "min_frame": None,
            "max_frame": None,
            "frame0_path": None,
            "frame0_mtime": None,
            "latest_file": None,
            "latest_mtime": None,
        }
    latest = max(frames.values(), key=lambda item: item.stat().st_mtime)
    frame0 = frames.get(0)
    return {
        "frame_count": len(frames),
        "min_frame": min(frames),
        "max_frame": max(frames),
        "frame0_path": str(frame0.resolve()) if frame0 else None,
        "frame0_mtime": frame0.stat().st_mtime if frame0 else None,
        "latest_file": str(latest.resolve()),
        "latest_mtime": latest.stat().st_mtime,
    }


def find_live_temp_replay(temp_dir: str, replay_name: Optional[str] = None) -> Dict[str, object]:
    """Find the active replay group using vgrplay's frame-0 mtime rule."""
    temp_path = Path(temp_dir)
    groups = _group_replay_frames(temp_path)
    if not groups:
        raise FileNotFoundError(f"No .vgr files found under temp dir: {temp_dir}")
    if replay_name is not None:
        if replay_name not in groups:
            raise FileNotFoundError(f"No .vgr files found for replay_name={replay_name} under {temp_dir}")
        oname = replay_name
        selected_by = "explicit_replay_name"
    else:
        frame0_groups = {
            name: frames for name, frames in groups.items()
            if 0 in frames
        }
        if not frame0_groups:
            raise FileNotFoundError(f"No replay group with frame 0 found under temp dir: {temp_dir}")
        oname = max(
            frame0_groups,
            key=lambda name: frame0_groups[name][0].stat().st_mtime,
        )
        selected_by = "latest_frame0_mtime"
    selected = _frame_summary(groups[oname])
    return {
        **selected,
        "oname": oname,
        "selected_by": selected_by,
        "candidate_count": len(groups),
    }


def _build_frame_inventory(directory: Path, replay_name: str) -> Dict[int, Path]:
    return _group_replay_frames(directory).get(replay_name, {})


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_injected_frames(
    source_dir: str,
    source_name: str,
    target_dir: str,
    target_name: str,
) -> Dict[str, object]:
    source = _build_frame_inventory(Path(source_dir), source_name)
    target = _build_frame_inventory(Path(target_dir), target_name)
    source_indexes = set(source)
    target_indexes = set(target)
    common_indexes = sorted(source_indexes & target_indexes)
    size_mismatches = []
    hash_mismatches = []
    for frame in common_indexes:
        source_size = source[frame].stat().st_size
        target_size = target[frame].stat().st_size
        if source_size != target_size:
            size_mismatches.append(
                {
                    "frame": frame,
                    "source_size": source_size,
                    "target_size": target_size,
                }
            )
            continue
        source_hash = _sha256(source[frame])
        target_hash = _sha256(target[frame])
        if source_hash != target_hash:
            hash_mismatches.append(
                {
                    "frame": frame,
                    "source_sha256": source_hash,
                    "target_sha256": target_hash,
                }
            )
    missing_target = sorted(source_indexes - target_indexes)
    extra_target = sorted(target_indexes - source_indexes)
    return {
        "source_frame_count": len(source),
        "target_frame_count": len(target),
        "source_min_frame": min(source_indexes) if source_indexes else None,
        "source_max_frame": max(source_indexes) if source_indexes else None,
        "target_min_frame": min(target_indexes) if target_indexes else None,
        "target_max_frame": max(target_indexes) if target_indexes else None,
        "missing_target_frames": missing_target,
        "extra_target_frames": extra_target,
        "size_mismatch_count": len(size_mismatches),
        "size_mismatches": size_mismatches[:20],
        "hash_mismatch_count": len(hash_mismatches),
        "hash_mismatches": hash_mismatches[:20],
        "verified_frame_count": len(common_indexes) - len(size_mismatches) - len(hash_mismatches),
        "ok": (
            bool(source)
            and len(source) == len(target)
            and not missing_target
            and not extra_target
            and not size_mismatches
            and not hash_mismatches
        ),
    }


def inject_replay_with_vgrplay(
    source_dir: str,
    replay_name: str,
    temp_dir: str,
    vgrplay_path: str = DEFAULT_VGRPLAY,
    live_replay_name: Optional[str] = None,
) -> Dict[str, object]:
    live = find_live_temp_replay(temp_dir, replay_name=live_replay_name)
    before_files = {
        path.name: path.stat().st_mtime
        for path in Path(temp_dir).glob(f"{live['oname']}.*.vgr")
    }

    cmd = [
        vgrplay_path,
        "-source",
        source_dir,
        "-sname",
        replay_name,
        "-overwrite",
        temp_dir,
        "-oname",
        str(live["oname"]),
    ]
    completed = subprocess.run(cmd, capture_output=True, text=True)

    after_files = {
        path.name: path.stat().st_mtime
        for path in Path(temp_dir).glob(f"{live['oname']}.*.vgr")
    }
    changed = sorted(
        name for name, mtime in after_files.items()
        if name not in before_files or before_files[name] != mtime
    )
    verification = verify_injected_frames(
        source_dir=source_dir,
        source_name=replay_name,
        target_dir=temp_dir,
        target_name=str(live["oname"]),
    )

    return {
        "captured_at": datetime.now().isoformat(),
        "command": cmd,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "source_dir": str(Path(source_dir).resolve()),
        "replay_name": replay_name,
        "temp_dir": str(Path(temp_dir).resolve()),
        "live_replay": live,
        "target_after": _frame_summary(_build_frame_inventory(Path(temp_dir), str(live["oname"]))),
        "changed_files": changed,
        "changed_count": len(changed),
        "verification": verification,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Inject a replay into the current temp replay slot via vgrplay.")
    parser.add_argument("--source-dir", required=True, help="Replay source directory")
    parser.add_argument("--replay-name", required=True, help="Replay name used by vgrplay -sname")
    parser.add_argument("--temp-dir", default=str(Path.home() / "AppData" / "Local" / "Temp"), help="Temp replay directory")
    parser.add_argument("--vgrplay", default=DEFAULT_VGRPLAY, help="Path to vgrplay.exe")
    parser.add_argument("--live-replay-name", help="Explicit temp replay group name to overwrite")
    parser.add_argument("-o", "--output", help="Optional output JSON path")
    args = parser.parse_args()

    report = inject_replay_with_vgrplay(
        source_dir=args.source_dir,
        replay_name=args.replay_name,
        temp_dir=args.temp_dir,
        vgrplay_path=args.vgrplay,
        live_replay_name=args.live_replay_name,
    )
    payload = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(payload, encoding="utf-8")
        print(f"vgrplay injection report saved to {args.output}")
    else:
        print(payload)
    return 0 if report["returncode"] == 0 else report["returncode"]


if __name__ == "__main__":
    raise SystemExit(main())
