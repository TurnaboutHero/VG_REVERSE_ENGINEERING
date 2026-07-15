"""Build result-screen KDA corrections from screenshot OCR row links."""

from __future__ import annotations

import argparse
import difflib
import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple


KDA_RE = re.compile(r"^\d{1,2}/\d{1,2}/\d{1,2}$")
OCRRow = Tuple[Sequence[Sequence[float]], str, float]
OCRReader = Callable[[str], Iterable[OCRRow]]


def _box_center(box: Sequence[Sequence[float]]) -> Tuple[float, float]:
    xs = [float(point[0]) for point in box]
    ys = [float(point[1]) for point in box]
    return sum(xs) / len(xs), sum(ys) / len(ys)


def _normalize_label(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def _clean_ocr_text(value: str) -> str:
    return re.sub(r"\s+", "", value.strip())


def _match_expected_name(text: str, expected_names: Sequence[str]) -> Optional[str]:
    normalized_text = _normalize_label(text)
    if not normalized_text:
        return None

    normalized_names = {_normalize_label(name): name for name in expected_names}
    if normalized_text in normalized_names:
        return normalized_names[normalized_text]

    matches = difflib.get_close_matches(normalized_text, list(normalized_names), n=1, cutoff=0.86)
    return normalized_names[matches[0]] if matches else None


@lru_cache(maxsize=1)
def _load_easyocr_reader():
    try:
        import easyocr  # type: ignore
    except Exception as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("easyocr is not available for screenshot KDA fallback") from exc

    return easyocr.Reader(["en"], gpu=False, verbose=False)


def _default_easyocr_reader(image_path: str) -> Iterable[OCRRow]:
    return _load_easyocr_reader().readtext(image_path, detail=1, paragraph=False)


def link_kda_rows_from_ocr_tokens(
    tokens: Iterable[OCRRow],
    expected_players: List[Dict[str, object]],
    *,
    row_y_tolerance: int = 72,
) -> Dict[str, object]:
    """Link OCR KDA tokens to expected players using same-row left-side labels."""
    expected_names = [str(player["name"]) for player in expected_players]
    name_tokens: List[Dict[str, object]] = []
    kda_tokens: List[Dict[str, object]] = []
    raw_tokens = []

    for box, text, confidence in tokens:
        cleaned = _clean_ocr_text(str(text))
        center_x, center_y = _box_center(box)
        raw_tokens.append(
            {
                "text": cleaned,
                "confidence": float(confidence),
                "center_x": round(center_x, 2),
                "center_y": round(center_y, 2),
            }
        )
        if KDA_RE.match(cleaned):
            kda_tokens.append(
                {
                    "kda": cleaned,
                    "confidence": float(confidence),
                    "center_x": center_x,
                    "center_y": center_y,
                }
            )
            continue

        matched_name = _match_expected_name(cleaned, expected_names)
        if matched_name:
            name_tokens.append(
                {
                    "name": matched_name,
                    "ocr_text": cleaned,
                    "confidence": float(confidence),
                    "center_x": center_x,
                    "center_y": center_y,
                }
            )

    assignments: Dict[str, Dict[str, object]] = {}
    for kda_token in kda_tokens:
        candidates = [
            name_token
            for name_token in name_tokens
            if float(name_token["center_x"]) < float(kda_token["center_x"])
            and abs(float(name_token["center_y"]) - float(kda_token["center_y"])) <= row_y_tolerance
        ]
        if not candidates:
            continue
        candidates.sort(
            key=lambda name_token: (
                abs(float(name_token["center_y"]) - float(kda_token["center_y"])),
                float(kda_token["center_x"]) - float(name_token["center_x"]),
                -float(name_token["confidence"]),
            )
        )
        name_token = candidates[0]
        name = str(name_token["name"])
        candidate = {
            "name": name,
            "corrected_kda": kda_token["kda"],
            "name_ocr_text": name_token["ocr_text"],
            "name_confidence": name_token["confidence"],
            "kda_confidence": kda_token["confidence"],
            "row_y_delta": round(abs(float(name_token["center_y"]) - float(kda_token["center_y"])), 2),
        }
        existing = assignments.get(name)
        if existing is None or (
            float(candidate["row_y_delta"]),
            -float(candidate["kda_confidence"]),
        ) < (
            float(existing["row_y_delta"]),
            -float(existing["kda_confidence"]),
        ):
            assignments[name] = candidate

    player_rows = []
    for player in expected_players:
        name = str(player["name"])
        assignment = assignments.get(name)
        parser_kda = f"{player['kills']}/{player['deaths']}/{player['assists']}"
        if assignment:
            corrected_kda = str(assignment["corrected_kda"])
            status = "image_ocr_row_linked"
        else:
            corrected_kda = None
            status = "unresolved"
        player_rows.append(
            {
                "name": name,
                "team": player["team"],
                "hero_name": player.get("hero_name"),
                "parser_kda": parser_kda,
                "corrected_kda": corrected_kda,
                "correction_status": status,
                "ocr_row_link": assignment,
            }
        )

    applicable_rows = sum(int(row["corrected_kda"] is not None) for row in player_rows)
    return {
        "applicable_rows": applicable_rows,
        "total_rows": len(expected_players),
        "recognized_name_tokens": len(name_tokens),
        "recognized_kda_tokens": len(kda_tokens),
        "raw_tokens": raw_tokens[:200],
        "player_rows": player_rows,
    }


def build_result_screen_image_kda_correction_apply(
    image_path: str,
    expected_players: List[Dict[str, object]],
    *,
    ocr_reader: Optional[OCRReader] = None,
) -> Dict[str, object]:
    reader = ocr_reader or _default_easyocr_reader
    report = link_kda_rows_from_ocr_tokens(reader(image_path), expected_players)
    return {
        "image_path": str(Path(image_path).resolve()),
        **report,
    }


def main() -> int:
    from .result_screen_kda_correction_report import _load_expected_players

    parser = argparse.ArgumentParser(description="Apply screenshot OCR KDA corrections to player rows.")
    parser.add_argument("--image", required=True, help="Result-screen screenshot path")
    parser.add_argument("--expected", required=True, help="Player rows JSON or decoder debug JSON")
    parser.add_argument("-o", "--output", help="Optional output JSON path")
    args = parser.parse_args()

    expected_players = _load_expected_players(args.expected)
    report = build_result_screen_image_kda_correction_apply(args.image, expected_players)
    payload = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(payload, encoding="utf-8")
        print(f"Result-screen image KDA correction apply report saved to {args.output}")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
