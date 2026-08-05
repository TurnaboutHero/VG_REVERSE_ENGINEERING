#!/usr/bin/env python3
"""
Unified Replay Decoder - Single entry point for complete VGR replay analysis.

Combines all solved detection modules:
  - VGRParser: players, teams, heroes, game mode (100% accuracy)
  - KDADetector: kills 99.0%, deaths 98.0%, assists 98.0% (combined 98.3%)
  - Gold earned: 600 starting + action 0x06 (sell_flag!=0x01). ±5% 98.0%, ±10% 100%
  - WinLossDetector: crystal destruction detection (100% accuracy)
  - Item-Player Mapping: [10 04 3D] acquire events → per-player item builds
  - Crystal Death Detection: eid 2000-2005 death → game duration & winner
  - Objective Events: Kraken vs Gold Mine via player kill proximity (eid>60000)

Team label limitation:
  The team_byte at player block +0xD5 groups players correctly (100%),
  but the 1→left / 2→right mapping is non-deterministic (~50% of matches
  have swapped labels). No binary-level signal has been found to resolve
  this (exhaustive search: player block bytes, entity events, event headers,
  turret clustering, crystal entity IDs — all fail to discriminate left/right).
  The E.V.I.L. engine replay format does not appear to encode map position.
  Winner detection via kill count asymmetry is 100% accurate (the winning
  GROUP is always correctly identified), but its "left"/"right" label may
  not match the API convention. Use truth_comparison.py auto-swap correction
  when validating against API telemetry data.

Usage:
    from vg.core.unified_decoder import UnifiedDecoder

    decoder = UnifiedDecoder("/path/to/replay")
    match = decoder.decode()
    print(match.to_json())

CLI:
    python -m vg.core.unified_decoder /path/to/replay
"""

import bisect
import json
import math
import struct
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Local imports with fallback for both package and direct execution
try:
    from vg.core.vgr_parser import VGRParser
    from vg.core.kda_detector import KDADetector
    from vg.core.vgr_mapping import ITEM_ID_MAP, RECIPES
    from vg.analysis.win_loss_detector import WinLossDetector
except ImportError:
    try:
        from vgr_parser import VGRParser
        from kda_detector import KDADetector
        from vgr_mapping import ITEM_ID_MAP, RECIPES
        _root = Path(__file__).resolve().parent.parent
        sys.path.insert(0, str(_root.parent))
        from vg.analysis.win_loss_detector import WinLossDetector
    except ImportError as e:
        raise ImportError(f"Cannot import required modules: {e}")

# Event headers for item and objective detection
_ITEM_ACQUIRE_HEADER = bytes([0x10, 0x04, 0x3D])
_ITEM_EQUIP_HEADER = bytes([0x10, 0x04, 0x4B])
_CREDIT_HEADER = bytes([0x10, 0x04, 0x1D])
_DEATH_HEADER = bytes([0x08, 0x04, 0x31])
_KILL_HEADER = bytes([0x18, 0x04, 0x1C])
_PLAYER_EID_RANGE = set(range(1500, 1510))  # BE entity IDs for players

# ===== ITEM BUILD ESTIMATION =====
# Upgrade tree using BINARY REPLAY IDs (from ITEM_ID_MAP)
# component_id -> set of result_ids it could have been upgraded into
#
# Two ID ranges:
#   - 200-255: standard shop purchases (qty=1)
#   - 0-27: T3/special item completions (qty=2), identified via hero distribution
#
# Uses TRANSITIVE relationships (T1 → all reachable T3s) so a single pass can
# compare each component against every result it could have been consumed by,
# even when the intermediate step is itself gone from the final build.
# Verified against official VG recipes (item_price_verify.py OFFICIAL_RECIPES).
UPGRADE_TREE = {
    458: {461, 464, 479, 480, 482, 491, 505, 506, 507, 524},  # Weapon Blade
    459: {462, 465, 486, 492, 496, 509, 510, 511, 512, 522, 523},  # Crystal Bit
    460: {463, 466, 482, 484, 491, 507, 508, 509, 520},  # Swift Shooter
    461: {464, 480, 491, 524},  # Six Sins
    462: {465, 486, 492, 522, 523},  # Eclipse Prism
    463: {466, 482, 484, 507, 509, 520},  # Blazing Salvo
    467: {468, 484, 485, 487, 488, 497, 503, 504, 516, 518, 528, 531, 533, 534},  # Oakheart
    468: {484, 497, 531, 533, 534},  # Dragonheart
    469: {470, 471, 498, 525, 538},  # Light Armor
    470: {471, 498, 525},  # Coat of Plates
    472: {474, 476, 490, 511, 539},  # Energy Battery
    473: {475, 476, 492, 524, 531, 534},  # Hourglass
    474: {476, 490, 511, 539},  # Void Battery
    475: {476, 492, 516, 519, 524, 531, 534},  # Chronograph (-> Stormcrown 519)
    513: {519},  # Stormguard Banner -> Stormcrown 519
    477: {478, 489, 490, 497, 530},  # Sprint Boots
    478: {489, 490, 497, 530},  # Travel Boots
    485: {488, 503},  # Reflex Block
    499: {479, 500, 520},  # Book of Eulogies
    500: {479, 520},  # Barbed Needle
    501: {487, 502, 503, 525, 538, 539},  # Light Shield
    502: {487, 503, 525, 539},  # Kinetic Shield
    504: {487, 533},  # Lifespring
    505: {464, 479, 507, 524},  # Heavy Steel
    506: {480, 482},  # Piercing Spear
    508: {466, 491},  # Lucky Strike
    510: {496},  # Piercing Shard
    512: {465, 486, 496, 509, 511, 522, 523},  # Heavy Prism
    # Both scout items feed SuperScout 2000: of its 31 owners, 27 also bought a
    # ScoutPak and 29 a ScoutTuff, and in every one of those cases the component
    # came first. The 529 edge was missing, so a ScoutPak consumed by the
    # upgrade stayed a build candidate forever.
    528: {527},  # ScoutTuff -> SuperScout 2000
    529: {527},  # ScoutPak  -> SuperScout 2000
    # Journey Boots(489), Contraption(516) and Flare Gun(518) were identified
    # from purchase costs; their edges follow the same transitive convention.
    518: {516, 527, 528},  # Flare Gun -> Contraption / ScoutTuff -> SuperScout
    # (Stormguard Banner 513 -> Stormcrown edge dropped: Stormcrown is unmapped;
    #  composed 527 is SuperScout 2000, not Stormcrown.)
    517: {466, 491, 508},  # Minion's Foot
}

# One .vgr section covers this much game time. Measured externally across 14
# matches spanning 716-2939s (9.94-10.00 s/section), so section count times this
# gives how long the recording ran - a length the event stream cannot fake.
SECONDS_PER_SECTION = 10

# Below this, the event stream stops well before the recording does, which means
# the tail of the match was never captured. Separates 10 complete tournament
# matches (0.97-1.00) from the one known truncated recording (0.56); the gap
# either side of it is empty, so the exact cut point is not tuned.
COMPLETENESS_THRESHOLD = 0.90

# Consumables leave no event when they are used, so a Flare or an infusion
# bought early is almost certainly gone by the end while the purchase log still
# shows it. Keep one only if it was bought in the last stretch of the player's
# purchases. Dropping them outright scores higher on F1 (93.4% precision against
# 91.7%) but costs a real item, so the conservative cut is the one used.
CONSUMABLE_KEEP_FRACTION = 0.90

# Granted at match start, never bought, so never part of a final build.
# Consumables that ARE bought (infusions, flares) stay eligible and are held
# back by the slot ranking instead.
STARTER_IDS = {
    457,  # Healing Flask   (1,201) - auto-granted at match start
    526,  # Scout Camera    (2,14)  - auto-granted at match start
}
# Both are handed to every player rather than bought: each appears for 456/502
# players, and per match either everyone has it (51 matches) or nobody does
# (5 matches whose start frames are missing) - never a partial split, which is
# what a purchased item produces.


def _le_to_be(eid_le: int) -> int:
    """Convert uint16 Little Endian entity ID to Big Endian."""
    return struct.unpack('>H', struct.pack('<H', eid_le))[0]


# An acquire and the cost it was charged for sit within a few hundred bytes of
# each other. 400 pairs 10479 of the corpus's purchases without ever reaching
# past a neighbouring purchase.
_COST_WINDOW = 400
# Refunds land on whole gold, so anything looser than a rounding slack would
# start matching items the player did not sell.
_SALE_TOLERANCE = 1.0
# Every price in the game is a multiple of 25, so half of one lands on 12.5 at
# worst; 93.6% of the corpus's refunds are a clean multiple of 25. The rest are
# accounting drift wearing a refund's clothes (see _detect_wallet), and this is
# what keeps most of it out.
_REFUND_STEP = 25
# Drift accumulates report after report, so a player it has caught looks like a
# serial seller. Real sellers are not: two is above every case that survived
# manual reading, and the cap is what stops a drifting player from being
# stripped down to their starter items.
_MAX_SALES_PER_PLAYER = 2


def _is_refund(amount: float) -> bool:
    """Whether a purse increase is shaped like half of an item's price."""
    return abs(amount - round(amount / _REFUND_STEP) * _REFUND_STEP) <= _SALE_TOLERANCE


def _pair_costs(
    acquires: List[Tuple[int, int]],
    costs: List[Tuple[int, float]],
) -> Dict[int, float]:
    """
    Match each acquire with the purchase cost logged beside it.

    The cost is what the player actually handed over, which is the full price
    only when they held none of the components - buying a result you already
    have parts for is charged the difference. That is what makes the amount
    usable for identifying an item, and for pricing what a sale gave back.

    Args:
        acquires: [(byte_offset, item_id)]
        costs: [(byte_offset, amount)] sorted by offset, amounts positive

    Returns:
        {acquire_offset: amount} for acquires with a cost nearby
    """
    positions = [pos for pos, _ in costs]
    paid: Dict[int, float] = {}
    for offset, _ in acquires:
        j = bisect.bisect_left(positions, offset)
        best: Optional[Tuple[int, float]] = None
        for k in (j - 1, j):
            if 0 <= k < len(costs) and abs(costs[k][0] - offset) <= _COST_WINDOW:
                if best is None or abs(costs[k][0] - offset) < abs(best[0] - offset):
                    best = costs[k]
        if best is not None:
            paid[offset] = best[1]
    return paid


def _estimate_final_build(
    acquires: List[Tuple[int, int]],
    costs: List[Tuple[int, float]] = (),
    sales: List[Tuple[int, float]] = (),
) -> List[str]:
    """
    Replay the purchases and return up to 6 items (final build).

    Two passes, because each catches what the other cannot:

    1. Inventory replay against RECIPES. Buying a result consumes one of each
       component, so a component bought three times and upgraded twice still
       leaves one. Counting is what makes that expressible - the older
       set-of-purchased-ids could only say "bought at some point".
    2. Order-aware strip against UPGRADE_TREE. A component bought after the
       result it feeds was never eaten by it, and pass 1 misses that because it
       consumes at the moment of the upgrade. UPGRADE_TREE is transitive, so one
       sweep compares each component against every result it could have fed.

    Pass 2 drops a component outright rather than decrementing it, so it can
    discard copies pass 1 says are still held - buy three Weapon Blades, upgrade
    one, and none survive. Decrementing instead is the coherent reading and was
    measured: it scores 97.5%/90.0% against 98.0%/90.9%, because holding spare
    copies of a component is rarer than the log's repeat purchases suggest.
    The weaker-looking rule wins on the data, so it is the one that ships.

    A sale leaves no event of its own, so pass 1 is also told what each held
    copy cost: a refund is half of that, which is enough to say which item went
    back to the shop. See _detect_wallet for where the refunds come from.

    Args:
        acquires: [(byte_offset, item_id)] in purchase order
        costs: [(byte_offset, amount)] purchase costs, sorted, positive
        sales: [(byte_offset, refund)] refunds inferred from wallet reports

    Returns:
        List of item names in final 6-slot build, sorted by tier desc
    """
    # Pass 1: replay purchases, consuming components as results are bought.
    # `spent_on` shadows the counts with what each held copy is worth, so a
    # refund can be traced back to the copy it came from. None means the price
    # was not readable and that copy can never answer for a sale.
    inventory: Dict[int, int] = defaultdict(int)
    spent_on: Dict[int, List[Optional[float]]] = defaultdict(list)
    paid = _pair_costs(acquires, costs) if sales else {}
    for offset, iid in sorted(acquires):
        recovered, priced = 0.0, offset in paid
        for comp_id in RECIPES.get(iid, ()):
            if inventory[comp_id] > 0:
                inventory[comp_id] -= 1
                consumed = spent_on[comp_id].pop() if spent_on[comp_id] else None
                if consumed is None:
                    priced = False
                else:
                    recovered += consumed
        inventory[iid] += 1
        spent_on[iid].append(paid[offset] + recovered if priced else None)

    # Sales. The refund is half of everything the player put into the item,
    # components included, so double it and look for the copy that cost that
    # much. Drop it only when exactly one copy answers: an ambiguous refund
    # would otherwise cost a real item, and keeping a sold one is the cheaper
    # mistake.
    for _, refund in sales:
        target = 2 * refund
        matched = [
            (iid, slot)
            for iid, stack in spent_on.items()
            for slot, amount in enumerate(stack)
            if amount is not None and abs(amount - target) <= _SALE_TOLERANCE
        ]
        if len(matched) == 1:
            iid, slot = matched[0]
            spent_on[iid].pop(slot)
            inventory[iid] -= 1

    # Last purchase of each item, used both to strip and to rank.
    seq: Dict[int, int] = {}
    for offset, iid in acquires:
        if offset > seq.get(iid, -1):
            seq[iid] = offset

    remaining = {iid for iid, n in inventory.items() if n > 0} - STARTER_IDS

    # Pass 2: drop components whose result was bought at or after them.
    for comp_id in list(remaining):
        results = UPGRADE_TREE.get(comp_id, set()) & remaining
        if results and any(seq.get(r, 0) >= seq.get(comp_id, 0) for r in results):
            remaining.discard(comp_id)

    # Convert to named items, dropping consumables bought early enough that the
    # player has almost certainly spent them since.
    last_offset = max((offset for offset, _ in acquires), default=0)
    consumable_cutoff = last_offset * CONSUMABLE_KEEP_FRACTION
    items = []
    for iid in remaining:
        info = ITEM_ID_MAP.get(iid)
        ts = seq.get(iid, 0)
        if info:
            tier = info.get('tier', 0)
            if tier < 1 and ts < consumable_cutoff:
                continue
            items.append((tier, ts, info['name'], iid))
        else:
            items.append((-1, ts, f"Unknown_{iid}", iid))

    # Rank for the 6-slot inventory limit:
    #   1) completed T3 items - held for the rest of the match, so an early
    #      purchase must not be pushed out by components bought later
    #   2) T1/T2 items, most recent first - unconsumed components a player is
    #      still carrying are the ones they bought last
    #   3) consumables (T0: infusions, traps) only fill leftover slots
    # Ranking tier ahead of recency across ALL tiers instead loses the low-tier
    # components players genuinely end the match holding.
    def _slot_rank(entry):
        tier, acquired = entry[0], entry[1]
        bucket = 0 if tier >= 3 else (1 if tier >= 1 else 2)
        return (bucket, -acquired)

    selected = sorted(items, key=_slot_rank)[:6]

    selected.sort(key=lambda x: (-x[0], -x[1]))
    return [name for _, _, name, _ in selected]


@dataclass
class ObjectiveEvent:
    """Detected objective event (Gold Mine/Ghostwing capture or Kraken/Blackclaw death)."""
    timestamp: float
    event_type: str  # 3v3: GOLD_MINE_CAPTURE, KRAKEN_DEATH/WAVE. 5v5: GHOSTWING_CAPTURE, BLACKCLAW_DEATH/WAVE
    entity_count: int
    entity_ids: List[int] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class DecodedPlayer:
    """Player data from unified decoding."""
    name: str
    team: str                          # "left" / "right"
    hero_name: str
    hero_id: Optional[int]
    entity_id: int                     # Little Endian (original)
    # When the match's DecodedMatch.data_complete is False these are lower
    # bounds: the recording stops mid-match so later events were never written.
    # Checked against truth on the one known truncated match - all 9 players
    # came in at or under the real figures, none over.
    kills: int = 0
    deaths: int = 0
    assists: Optional[int] = None
    minion_kills: int = 0
    jungle_kills: int = 0  # action 0x0D credit count
    gold_spent: int = 0
    gold_earned: int = 0  # 600 starting + 0x06 income (sell_flag!=0x01). ±5% 98.0%, ±10% 100%
    items: List[str] = field(default_factory=list)  # Final build (after upgrade tree filtering)
    # Raw acquire log, kept unfiltered. Includes the STARTER_IDS items every
    # player is handed at match start, so subtract those before reading it as
    # purchase frequency.
    items_all_purchased: List[str] = field(default_factory=list)
    # Comparison fields (populated when truth is available)
    truth_kills: Optional[int] = None
    truth_deaths: Optional[int] = None

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class DecodedMatch:
    """Complete decoded match data."""
    replay_name: str
    replay_path: str
    game_mode: str
    map_name: str
    team_size: int
    duration_seconds: Optional[int] = None
    winner: Optional[str] = None
    left_team: List[DecodedPlayer] = field(default_factory=list)
    right_team: List[DecodedPlayer] = field(default_factory=list)
    total_frames: int = 0
    crystal_death_ts: Optional[float] = None
    crystal_death_eid: Optional[int] = None
    objective_events: List[ObjectiveEvent] = field(default_factory=list)
    # How much game time the .vgr sections cover, from the section count.
    recorded_seconds: Optional[int] = None
    # duration_seconds / recorded_seconds. Near 1.0 when the event stream runs
    # to the end of the recording; well below when the recording outlasts it.
    completeness_ratio: Optional[float] = None
    # True/False once both durations are known, None while undecidable.
    # False means kills/deaths/assists are LOWER BOUNDS, not wrong values.
    data_complete: Optional[bool] = None
    # Detection flags
    kda_detection_used: bool = False
    win_detection_used: bool = False
    item_detection_used: bool = False
    team_labels_reliable: bool = False  # left/right labels may not match API convention

    @property
    def all_players(self) -> List[DecodedPlayer]:
        return self.left_team + self.right_team

    def to_dict(self) -> Dict:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


class UnifiedDecoder:
    """
    Single entry point for complete VGR replay analysis.

    Orchestrates VGRParser, KDADetector, WinLossDetector, and ItemExtractor
    to produce a fully decoded match result.
    """

    def __init__(self, replay_path: str):
        """
        Args:
            replay_path: Path to .0.vgr file or replay cache folder.
        """
        self.replay_path = Path(replay_path)

    def decode(self, detect_items: bool = False) -> DecodedMatch:
        """
        Run full decoding pipeline.

        Args:
            detect_items: If True, also run ItemExtractor (partial accuracy).

        Returns:
            DecodedMatch with all detected fields populated.
        """
        # --- Step 1: Basic parsing (frame 0) ---
        parser = VGRParser(
            str(self.replay_path),
            detect_heroes=False,
            auto_truth=False,
        )
        parsed = parser.parse()

        match_info = parsed.get("match_info", {})
        replay_name = parsed.get("replay_name", "")
        replay_file = parsed.get("replay_file", str(self.replay_path))

        # Resolve frame directory
        replay_file_path = Path(replay_file)
        frame_dir = replay_file_path.parent
        frame_name = replay_file_path.stem.rsplit('.', 1)[0]

        # Build player list from parsed teams
        left_parsed = parsed.get("teams", {}).get("left", [])
        right_parsed = parsed.get("teams", {}).get("right", [])

        left_team = [self._make_player(p) for p in left_parsed]
        right_team = [self._make_player(p) for p in right_parsed]
        all_players = left_team + right_team

        # --- Step 2: Load all frames ---
        frames = self._load_frames(frame_dir, frame_name)
        # Section count describes the loaded bytes, so derive it from `frames`
        # rather than re-globbing: unreadable or filtered sections must not
        # inflate the recording length we compare the event stream against.
        recorded_seconds = (
            (max(idx for idx, _ in frames) + 1) * SECONDS_PER_SECTION if frames else None
        )

        # --- Step 3: KDA Scanning (event collection only, no filtering yet) ---
        kda_used = False
        duration_est = None
        kda_detector = None
        eid_map_be_kda = {}  # BE -> player
        team_map_kda = {}    # BE -> team name
        if frames and all_players:
            kda_detector, eid_map_be_kda, team_map_kda, duration_est = \
                self._scan_kda_events(frames, all_players)
            kda_used = kda_detector is not None

        # --- Step 4: Win/Loss Detection ---
        # Strategy: WinLossDetector for crystal destruction detection,
        # then KDA-based team mapping to determine which side won.
        # WinLossDetector's left/right label is unreliable due to
        # entity ID mapping issues, so we cross-check with kill totals.
        win_used = False
        winner = None
        crystal_detected = False
        try:
            import io
            detector = WinLossDetector(str(self.replay_path))
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            try:
                outcome = detector.detect_winner()
            finally:
                sys.stdout = old_stdout
            if outcome:
                crystal_detected = True
                win_used = True
        except Exception:
            pass

        # --- Step 5: Per-player Item Detection via [10 04 3D] ---
        item_used = False
        all_data = b"".join(data for _, data in frames) if frames else b""
        if all_data and all_players:
            eid_map_be = {}
            for player in all_players:
                if player.entity_id:
                    eid_be = _le_to_be(player.entity_id)
                    eid_map_be[eid_be] = player
            if eid_map_be:
                self._detect_items_per_player(all_data, eid_map_be)
                self._detect_gold_per_player(frames, eid_map_be)
                item_used = True

        # --- Step 6: Crystal Death Detection ---
        crystal_ts = None
        crystal_eid = None
        if all_data:
            crystal_ts, crystal_eid = self._detect_crystal_death(
                all_data, duration_est
            )

        # --- Step 7: Duration estimation ---
        # Crystal death is preferred but eid 2000-2005 can be turrets.
        # If crystal is much earlier than max player death, it's a FP.
        duration = None
        if crystal_ts is not None and duration_est is not None:
            if crystal_ts >= duration_est - 30:
                # Crystal death is at or after last player death → valid
                duration = int(crystal_ts)
            else:
                # Crystal death is much earlier → false positive turret
                duration = int(duration_est)
        elif crystal_ts is not None:
            duration = int(crystal_ts)
        elif duration_est is not None:
            duration = int(duration_est)

        # --- Step 7a: Completeness ---
        # The event stream ending long before the recording does means the tail
        # of the match was never captured, so every per-player count is short.
        # Both durations must be known to decide; otherwise stay undecided
        # rather than calling a replay with no deaths at all "truncated".
        completeness = None
        data_complete = None
        if duration and recorded_seconds:
            completeness = duration / recorded_seconds
            data_complete = completeness >= COMPLETENESS_THRESHOLD

        # --- Step 7b: Apply KDA filter with computed duration ---
        # Now that we have proper game duration (from crystal death),
        # filter kills/deaths/assists with post-game ceremony removal.
        if kda_detector and eid_map_be_kda:
            results = kda_detector.get_results(
                game_duration=duration, team_map=team_map_kda,
            )
            for eid_be, kda in results.items():
                player = eid_map_be_kda.get(eid_be)
                if player:
                    player.kills = kda.kills
                    player.deaths = kda.deaths
                    player.assists = kda.assists
                    player.minion_kills = kda.minion_kills

        # KDA-based winner: team with more kills wins (consistent
        # with VGRParser's team label convention).
        if kda_used:
            left_kills = sum(p.kills for p in left_team)
            right_kills = sum(p.kills for p in right_team)
            if left_kills > right_kills:
                winner = "left"
            elif right_kills > left_kills:
                winner = "right"
            # Tie: use WinLossDetector's label as fallback
            elif crystal_detected and outcome:
                winner = outcome.winner

        # --- Step 8: Objective event detection ---
        # 3v3: Kraken / Gold Mine.  5v5: Blackclaw / Ghostwing
        game_mode = match_info.get("mode", "")
        is_5v5 = "5v5" in game_mode
        objective_events = []
        if all_data:
            objective_events = self._detect_objective_events(
                all_data, is_5v5=is_5v5,
            )

        # --- Step 9: Assemble result ---
        return DecodedMatch(
            replay_name=replay_name,
            replay_path=str(replay_file),
            game_mode=match_info.get("mode", "Unknown"),
            map_name=match_info.get("map_name", "Unknown"),
            team_size=match_info.get("team_size", 3),
            duration_seconds=duration,
            winner=winner,
            left_team=left_team,
            right_team=right_team,
            total_frames=match_info.get("total_frames", 0),
            crystal_death_ts=crystal_ts,
            crystal_death_eid=crystal_eid,
            recorded_seconds=recorded_seconds,
            completeness_ratio=round(completeness, 3) if completeness else None,
            data_complete=data_complete,
            objective_events=objective_events,
            kda_detection_used=kda_used,
            win_detection_used=win_used,
            item_detection_used=item_used,
        )

    def decode_with_truth(self, truth_path: str) -> DecodedMatch:
        """
        Decode and attach truth data for comparison.

        Args:
            truth_path: Path to tournament_truth.json.

        Returns:
            DecodedMatch with truth_kills/truth_deaths populated.
        """
        match = self.decode()
        truth = self._load_truth(truth_path, match.replay_name)
        if not truth:
            return match

        # Apply truth duration/winner
        truth_info = truth.get("match_info", {})
        if truth_info.get("duration_seconds") is not None:
            match.duration_seconds = truth_info["duration_seconds"]
        if truth_info.get("winner"):
            # Keep detected winner, truth is for comparison

            pass

        # Apply truth K/D per player
        truth_players = truth.get("players", {})
        for player in match.all_players:
            tp = truth_players.get(player.name, {})
            if tp:
                player.truth_kills = tp.get("kills")
                player.truth_deaths = tp.get("deaths")

        # Note: KDA is NOT re-run with truth duration. The decoder's own
        # duration estimate (from crystal death / max death timestamp)
        # provides better post-game filtering.

        return match

    def _make_player(self, p: Dict) -> DecodedPlayer:
        """Convert parser player dict to DecodedPlayer."""
        return DecodedPlayer(
            name=p.get("name", "Unknown"),
            team=p.get("team", "unknown"),
            hero_name=p.get("hero_name", "Unknown"),
            hero_id=p.get("hero_id"),
            entity_id=p.get("entity_id", 0),
        )

    def _load_frames(self, frame_dir: Path, replay_name: str) -> List[tuple]:
        """Load all frame files as (frame_idx, data) tuples."""
        frame_files = list(frame_dir.glob(f"{replay_name}.*.vgr"))
        if not frame_files:
            return []

        def _idx(p: Path) -> int:
            try:
                return int(p.stem.split('.')[-1])
            except ValueError:
                return 0

        frame_files.sort(key=_idx)
        return [(_idx(f), f.read_bytes()) for f in frame_files]

    def _scan_kda_events(
        self,
        frames: List[tuple],
        all_players: List[DecodedPlayer],
    ) -> tuple:
        """
        Scan all frames for KDA events (no filtering applied yet).

        Returns:
            (detector, eid_map, team_map, duration_estimate)
            detector is None if no valid entity IDs found.
        """
        # Build BE entity ID set and LE→BE mapping
        eid_map = {}  # BE -> player
        valid_eids = set()
        team_map = {}  # BE -> team name
        for player in all_players:
            if player.entity_id:
                eid_be = _le_to_be(player.entity_id)
                eid_map[eid_be] = player
                valid_eids.add(eid_be)
                team_map[eid_be] = player.team

        if not valid_eids:
            return None, {}, {}, None

        detector = KDADetector(valid_eids)
        for frame_idx, data in frames:
            detector.process_frame(frame_idx, data)

        # Estimate duration from max death timestamp
        duration_est = None
        if detector.death_events:
            duration_est = max(d.timestamp for d in detector.death_events)

        return detector, eid_map, team_map, duration_est

    def _detect_wallet(
        self,
        all_data: bytes,
        valid_eids: Set[int],
    ) -> Tuple[Dict[int, List[Tuple[int, float]]], Dict[int, List[Tuple[int, float]]]]:
        """
        Read purchase costs, and infer sales from the wallet reports.

        A credit event carrying sell_flag=0x01 is not a delta at all: it states
        what the player is holding. Subtract the running (earned - spent) and
        what is left is starting gold plus every refund so far, which is why
        these values were right to keep out of income - counting them would
        have double-counted the whole purse.

        The residual is flat across a match - 750 in 37 of the 47 matches that
        report a purse - so the match minimum is the starting gold and any rise
        above it is a sale. 93.6% of those rises are a multiple of 25 and the
        common ones (150, 550, 700, 850, 1250) are half of a real item price,
        which is what makes them readable as refunds at all.

        Sales before the first report or after the last one are invisible, and
        two sales between one report and the next arrive added together. Both
        show up as a refund matching no single item, which is dropped.

        The residual also absorbs every error in the income accounting, and
        there is one: balances still run negative for some players, so gold is
        being earned somewhere this decoder does not see. That missing income
        creeps into the residual and reads as a run of sales, which is what
        _REFUND_STEP and _MAX_SALES_PER_PLAYER exist to blunt. Left unguarded
        it stripped three players of three or four tier-3 items each. None of
        this is measurable on the tuning set - matches 1 to 4 report almost no
        purse at all - so the guards answer to manual reading, not to a score.

        Args:
            all_data: concatenated replay bytes
            valid_eids: entity IDs of the players

        Returns:
            ({eid: [(offset, cost)]}, {eid: [(offset, refund)]}), both sorted
        """
        costs: Dict[int, List[Tuple[int, float]]] = defaultdict(list)
        purse: Dict[int, List[Tuple[int, float]]] = defaultdict(list)
        earned: Dict[int, float] = defaultdict(float)
        spent: Dict[int, float] = defaultdict(float)

        pos = 0
        while True:
            pos = all_data.find(_CREDIT_HEADER, pos)
            if pos == -1:
                break
            if pos + 13 > len(all_data) or all_data[pos + 3:pos + 5] != b'\x00\x00':
                pos += 1
                continue
            eid = struct.unpack_from(">H", all_data, pos + 5)[0]
            if eid not in valid_eids or all_data[pos + 11] != 0x06:
                pos += 3
                continue
            value = struct.unpack_from(">f", all_data, pos + 7)[0]
            if math.isnan(value) or math.isinf(value):
                pos += 3
                continue
            if value < 0:
                spent[eid] += -value
                costs[eid].append((pos, -value))
            elif all_data[pos + 12] == 0x01:
                purse[eid].append((pos, value - (earned[eid] - spent[eid])))
            else:
                earned[eid] += value
            pos += 3

        sales: Dict[int, List[Tuple[int, float]]] = defaultdict(list)
        residuals = [r for reports in purse.values() for _, r in reports]
        if residuals:
            starting_gold = min(residuals)
            for eid, reports in purse.items():
                previous = 0.0
                for offset, residual in reports:
                    refunded = residual - starting_gold
                    step = refunded - previous
                    previous = refunded
                    if step > _SALE_TOLERANCE and _is_refund(step):
                        sales[eid].append((offset, step))
                del sales[eid][_MAX_SALES_PER_PLAYER:]
        return costs, sales

    def _detect_items_per_player(
        self,
        all_data: bytes,
        eid_map: Dict[int, 'DecodedPlayer'],
    ) -> None:
        """
        Scan [10 04 3D] item acquire events and [10 04 1D] action=0x06
        purchase costs. Assigns per-player items (final build after upgrade tree)
        and gold_spent.

        Item acquire: [10 04 3D][00 00][eid BE][00 00][qty][item_id LE][00 00][counter BE][ts f32 BE]
        Purchase cost: [10 04 1D][00 00][eid BE][cost f32 BE (negative)][06]
        """
        valid_eids = set(eid_map.keys())
        costs, sales = self._detect_wallet(all_data, valid_eids)

        # --- Scan item acquire events ---
        player_items: Dict[int, Set[int]] = defaultdict(set)  # eid -> set of item_ids
        # Ordered acquisitions, keyed by byte offset. Sections are concatenated
        # in play order, so offset is a total order over purchases and unlike the
        # float timestamp it is never missing or out of range.
        player_acquires: Dict[int, List[Tuple[int, int]]] = defaultdict(list)
        pos = 0
        while True:
            pos = all_data.find(_ITEM_ACQUIRE_HEADER, pos)
            if pos == -1:
                break
            if pos + 20 > len(all_data):
                pos += 1
                continue
            if all_data[pos + 3:pos + 5] != b'\x00\x00':
                pos += 1
                continue

            eid = struct.unpack_from(">H", all_data, pos + 5)[0]
            if eid not in valid_eids:
                pos += 1
                continue

            # qty=1 + IDs 200-255 = standard item purchase
            # qty=2 + IDs 0-27 = T3/special item completion (NOT ability upgrades)
            #   Per-player analysis: only 2-5 qty=2 events (too few for abilities)
            #   Hero distribution matches item buyers perfectly
            # ID 14 is universal (system event, not an item) - filtered below
            qty = all_data[pos + 9]
            if qty not in (1, 2):
                pos += 3
                continue

            # 16-bit BIG-ENDIAN id: high=qty(+9), low=id(+10).
            # item_id = qty*256 + low  (qty=1 -> 457-511, qty=2 -> 512-539).
            # Confirmed vs real bytes + VGNA ground truth. Old code read a
            # uint16 LE at +10 and masked to low byte, discarding the high
            # byte and collapsing 457-539 onto 0-255 (the misID bug).
            item_id = qty * 256 + all_data[pos + 10]
            item_info = ITEM_ID_MAP.get(item_id)
            if item_info:
                player_items[eid].add(item_id)
                player_acquires[eid].append((pos, item_id))

            pos += 3

        # Apply upgrade tree filtering to get final builds
        for eid, item_ids in player_items.items():
            player = eid_map.get(eid)
            if player:
                # Store all purchased items (raw)
                all_purchased = []
                for iid in sorted(item_ids):
                    info = ITEM_ID_MAP.get(iid)
                    if info:
                        all_purchased.append(info['name'])
                player.items_all_purchased = all_purchased

                # Replay the purchases to get the final build (max 6 slots)
                player.items = _estimate_final_build(
                    player_acquires.get(eid, []),
                    costs.get(eid, []),
                    sales.get(eid, []),
                )

        # Gold detection moved to _detect_gold_per_player (frame-by-frame dedup)

    def _detect_gold_per_player(
        self,
        frames: List[tuple],
        eid_map: Dict[int, 'DecodedPlayer'],
    ) -> None:
        """
        Detect gold earned/spent via [10 04 1D] action=0x06.
        Frames are independent (not cumulative), so sum across all frames.

        Sell-back filtering: the byte at offset +12 (right after action byte)
        distinguishes income (0x00) from item sell-back refunds (0x01).
        Excluding 0x01 records eliminates sell-back gold overcounting.

        Args:
            frames: List of (frame_idx, data) tuples, sorted by frame index.
            eid_map: {BE entity ID: DecodedPlayer} mapping.
        """
        valid_eids = set(eid_map.keys())
        gold_spent: Dict[int, float] = defaultdict(float)
        gold_earned: Dict[int, float] = defaultdict(float)
        jungle_kills: Dict[int, int] = defaultdict(int)

        for frame_idx, data in frames:
            pos = 0
            while True:
                pos = data.find(_CREDIT_HEADER, pos)
                if pos == -1:
                    break
                if pos + 13 > len(data):
                    pos += 1
                    continue
                if data[pos + 3:pos + 5] != b'\x00\x00':
                    pos += 1
                    continue

                eid = struct.unpack_from(">H", data, pos + 5)[0]
                if eid not in valid_eids:
                    pos += 3
                    continue

                value = struct.unpack_from(">f", data, pos + 7)[0]
                action = data[pos + 11]
                sell_flag = data[pos + 12]

                if not math.isnan(value) and not math.isinf(value):
                    if action == 0x06:
                        if value < 0:
                            gold_spent[eid] += abs(value)
                        elif value > 0 and sell_flag != 0x01:
                            gold_earned[eid] += value
                    elif action == 0x0D:
                        jungle_kills[eid] += 1

                pos += 3

        for eid in valid_eids:
            player = eid_map.get(eid)
            if player:
                if eid in gold_spent:
                    player.gold_spent = round(gold_spent[eid])
                player.gold_earned = 600 + round(gold_earned.get(eid, 0))
                if eid in jungle_kills:
                    player.jungle_kills = jungle_kills[eid]

    def _detect_objective_events(
        self,
        all_data: bytes,
        eid_threshold: int = 60000,
        cluster_window: float = 5.0,
        is_5v5: bool = False,
    ) -> List[ObjectiveEvent]:
        """
        Detect objective events (Gold Mine captures and Kraken deaths).

        Classification rule for single-entity deaths (n=1, eid > 60000):
          - Player kill [18 04 1C] within ±500B → KRAKEN_DEATH
          - No player kill nearby → GOLD_MINE_CAPTURE
        Multi-entity clusters (n>1) are KRAKEN_WAVE or MINION_WAVE.
        """
        # Collect all objective deaths
        deaths = []
        pos = 0
        while True:
            idx = all_data.find(_DEATH_HEADER, pos)
            if idx == -1:
                break
            pos = idx + 1
            if idx + 13 > len(all_data):
                continue
            if (all_data[idx + 3:idx + 5] != b'\x00\x00' or
                    all_data[idx + 7:idx + 9] != b'\x00\x00'):
                continue
            eid = struct.unpack_from(">H", all_data, idx + 5)[0]
            ts = struct.unpack_from(">f", all_data, idx + 9)[0]
            if eid > eid_threshold and 0 < ts < 5000:
                deaths.append((ts, eid, idx))

        if not deaths:
            return []

        deaths.sort(key=lambda x: x[0])

        # Cluster by time window
        clusters: List[List[tuple]] = []
        cur: List[tuple] = []
        for d in deaths:
            if not cur or d[0] - cur[-1][0] <= cluster_window:
                cur.append(d)
            else:
                clusters.append(cur)
                cur = [d]
        if cur:
            clusters.append(cur)

        # Classify each cluster
        events = []
        for cluster in clusters:
            ts = cluster[0][0]
            eids = [d[1] for d in cluster]
            offsets = [d[2] for d in cluster]
            n = len(cluster)

            player_kill = self._has_player_kill_nearby(all_data, offsets)

            if n == 1 and not player_kill:
                event_type = "GHOSTWING_CAPTURE" if is_5v5 else "GOLD_MINE_CAPTURE"
            elif n == 1 and player_kill:
                event_type = "BLACKCLAW_DEATH" if is_5v5 else "KRAKEN_DEATH"
            elif n > 1 and player_kill:
                event_type = "BLACKCLAW_WAVE" if is_5v5 else "KRAKEN_WAVE"
            else:
                event_type = "MINION_WAVE"

            events.append(ObjectiveEvent(
                timestamp=round(ts, 2),
                event_type=event_type,
                entity_count=n,
                entity_ids=eids,
            ))

        return events

    @staticmethod
    def _has_player_kill_nearby(
        data: bytes, offsets: List[int], window: int = 500
    ) -> bool:
        """Check if any player kill [18 04 1C] exists within window bytes."""
        for off in offsets:
            s = max(0, off - window)
            e = min(len(data), off + window)
            region = data[s:e]
            pk = 0
            while True:
                kidx = region.find(_KILL_HEADER, pk)
                if kidx == -1:
                    break
                pk = kidx + 1
                if kidx + 7 > len(region):
                    continue
                killer = struct.unpack_from(">H", region, kidx + 5)[0]
                if killer in _PLAYER_EID_RANGE:
                    return True
        return False

    def _detect_crystal_death(
        self,
        all_data: bytes,
        duration_est: Optional[float],
    ) -> Tuple[Optional[float], Optional[int]]:
        """
        Detect Vain Crystal destruction via death header for eid 2000-2005.
        The crystal death timestamp closely matches game duration.

        Returns:
            (crystal_death_ts, crystal_death_eid) or (None, None).
        """
        crystal_deaths = []
        pos = 0
        while True:
            pos = all_data.find(_DEATH_HEADER, pos)
            if pos == -1:
                break
            if pos + 13 > len(all_data):
                pos += 1
                continue
            if (all_data[pos + 3:pos + 5] != b'\x00\x00' or
                    all_data[pos + 7:pos + 9] != b'\x00\x00'):
                pos += 1
                continue

            eid = struct.unpack_from(">H", all_data, pos + 5)[0]
            ts = struct.unpack_from(">f", all_data, pos + 9)[0]

            if 2000 <= eid <= 2005 and 60 < ts < 2400:
                crystal_deaths.append((ts, eid))

            pos += 1

        if not crystal_deaths:
            return None, None

        # The crystal death is the one with the latest timestamp
        # (closest to game end). Filter: must be within ±60s of
        # duration estimate if available.
        crystal_deaths.sort(key=lambda x: x[0], reverse=True)

        if duration_est is not None:
            for ts, eid in crystal_deaths:
                if abs(ts - duration_est) < 60:
                    return ts, eid

        # No duration estimate: return latest crystal death
        return crystal_deaths[0]

    def _load_truth(self, truth_path: str, replay_name: str) -> Optional[Dict]:
        """Load truth data for a specific replay."""
        try:
            with open(truth_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for m in data.get("matches", []):
                if m.get("replay_name") == replay_name:
                    return m
            return None
        except (FileNotFoundError, json.JSONDecodeError):
            return None


def main():
    import argparse

    arg_parser = argparse.ArgumentParser(
        description='Unified VGR Replay Decoder - decode all match data from replay files'
    )
    arg_parser.add_argument(
        'path',
        help='Path to replay folder or .0.vgr file'
    )
    arg_parser.add_argument(
        '--truth',
        help='Path to tournament_truth.json for comparison'
    )
    arg_parser.add_argument(
        '--items',
        action='store_true',
        help='(Legacy flag, items are now always detected per-player)'
    )
    arg_parser.add_argument(
        '-o', '--output',
        help='Output JSON file path (default: stdout)'
    )

    args = arg_parser.parse_args()

    decoder = UnifiedDecoder(args.path)
    if args.truth:
        match = decoder.decode_with_truth(args.truth)
    else:
        match = decoder.decode(detect_items=args.items)

    output = match.to_json()

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Result saved to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == '__main__':
    main()
