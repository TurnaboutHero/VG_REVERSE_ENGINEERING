# Mismatch investigation evidence (2026-09-07)

These are the original tested research scripts and compact results, not a production decoder. Raw replays, truth JSON, images, APKs, engines, and large per-record exports are kept locally and are not included here. `reconciled.json` uses anonymous actor references, not player names. `archive-hashes.json` retains every compared member hash with its frame number; private source paths are omitted.

## Reproduce with the original local fixtures

Run from the repository root in the existing Python environment. `vg/output/tournament_truth.json` must point to the original local replay files. The source export scripts intentionally preserve their tested output location. Create it first:

```sh
mkdir -p .superpowers/sdd/2026-09-07-mismatch
PYTHONPATH=. python vg/docs/evidence/2026-09-07-mismatch/probe.py
PYTHONPATH=. python vg/docs/evidence/2026-09-07-mismatch/clock_probe.py
```

Copy `reconcile.py` and `verify_reconciliation.py` to that output directory alongside the exported `probe.json` and `clocks.json`. Then run there:

```sh
python reconcile.py probe.json clocks.json --output reconciled.json
python verify_reconciliation.py
```

Expected: 294 KDA values and 78 resource14/CS comparisons match in the ten coherent fixtures; M9's 36 comparisons are not scorable. M6 mismatch counts are 11 (raw), 4 (initial state only), 7 (clock only), and 0 (both). The existing 107-player matching denominator is preserved, not silently expanded to 110. M5 and M6 are in-game capture-time comparisons, not final results. No overall 100% claim.

`archive_compare.py` runs from the repository root and prints the source ZIP comparison JSON. `source_integrity.py` runs from the root after exporting and verifies the input-file hashes. Those outputs include local paths and should remain ignored.

The scripts require the exact observed snapshot sizes and ADD/layer profiles; unsupported inputs fail assertions instead of being guessed. Clock interpolation is estimated from per-frame anchors. Its game-state assignment is statically traced; the clock-rendering code is not. Resource14 storage is traced, but the CS display label is only compared empirically here.

## Evidence identity

`verification.json` binds the tested scripts and private exported inputs to SHA-256. `review.md` records the original evidence review. `source-integrity.json` shows that all 1,322 source replay files remained unchanged. These SHA-bound source results predate the branch's history alignment and remain identifiable by file content.

`native-proof.md` and adjacent disassembly files trace snapshot application in the Android engine identified in [the APK comparison](../../OFFICIAL_APK_COMPARISON_2026-09-07.md). Engine SHA-256: `cd1b8831f82c469274613fc30f1f1f6e78c788102cdad7db5db2c04b96580a47`. Function role labels are analysis names for stripped code. The extra four bytes in 750-byte snapshots are not interpreted.
