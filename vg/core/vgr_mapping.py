#!/usr/bin/env python3
"""
VGR Mapping - Hero and Item ID Mapping for Vainglory
Maps internal game IDs to human-readable names.

Note: IDs are based on game version 4.13 and may vary in different versions.
These mappings are derived from game data analysis and community resources.
"""

import json
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict

# Asset-based Hero ID Mapping (extracted from game files)
# These IDs are used in /Characters/HeroXXX/ paths in game assets
ASSET_HERO_ID_MAP: Dict[str, str] = {
    "009": "SAW", "010": "Ringo", "011": "Taka", "012": "Krul",
    "013": "Skaarf", "014": "Celeste", "015": "Vox", "016": "Catherine",
    "017": "Ardan", "019": "Glaive", "020": "Joule", "021": "Koshka",
    "023": "Petal", "024": "Adagio", "025": "Rona", "027": "Fortress",
    "028": "Reim", "029": "Phinn", "030": "Blackfeather", "031": "Skye",
    "036": "Kestrel", "037": "Alpha", "038": "Lance", "039": "Ozo",
    "040": "Lyra", "041": "Samuel", "042": "Baron", "044": "Gwen",
    "045": "Flicker", "046": "Idris", "047": "Grumpjaw", "048": "Baptiste",
    "054": "Grace", "055": "Reza", "058": "Churnwalker", "059": "Lorelai",
    "060": "Tony", "061": "Varya", "062": "Malene", "063": "Kensei",
    "064": "Kinetic", "065": "San Feng", "066": "Silvernail", "067": "Yates",
    "068": "Inara", "069": "Magnus", "070": "Caine", "071": "Leo",
    "022": "Warhawk", # Likely candidate
    "032": "Anka",    # Confirmed active ID with high event count
    "056": "Miho",    # Likely candidate
    "072": "Amael",   # Confirmed from replay analysis
    "075": "Ishtar",  # Likely candidate
    "082": "Karas",   # Likely candidate
    "103": "Shin",    # Likely candidate (Latest hero)
    # Still missing: Ylva, Viola (One is likely 056 or 022?)
}

# Binary Hero ID Mapping (uint16 LE at player block offset +0x0A9)
# Discovered via cross-correlation analysis of 107 player blocks
# across 11 tournament replays with 100% consistency, 0 collisions.
# Structure: player_block_marker(DA 03 EE) + name + ... + entity_id(0xA5) + 00 00 + hero_id(0xA9)
BINARY_HERO_ID_MAP: Dict[int, str] = {
    # === Confirmed (100% - validated across 107 tournament players) ===
    0x0101: "Ardan",
    0x0301: "Fortress",
    0x0501: "Baron",
    0x0901: "Skye",
    0x0A01: "Reim",
    0x0B01: "Kestrel",
    0x0D01: "Lyra",
    0x1101: "Idris",
    0x1201: "Ozo",
    0x1401: "Samuel",
    0x1701: "Phinn",
    0x1801: "Blackfeather",
    0x1901: "Malene",
    0x1D01: "Celeste",
    0x8B01: "Gwen",
    0x8C01: "Grumpjaw",
    0x8D01: "Tony",
    0x8F01: "Baptiste",
    0x9103: "Leo",
    0x9301: "Reza",
    0x9303: "Caine",
    0x9403: "Warhawk",
    0x9601: "Grace",
    0x9901: "Lorelai",
    0x9A03: "Ishtar",
    0x9C01: "Kensei",
    0xA201: "Magnus",
    0xA401: "Kinetic",
    0xB001: "Silvernail",
    0xB401: "Ylva",
    0xB701: "Yates",
    0xB801: "Inara",
    0xBE01: "San Feng",
    0xF200: "Catherine",
    0xF300: "Ringo",
    0xFD00: "Joule",
    0xFF00: "Skaarf",
    # === Inferred (avg ~80% confidence - release chronology + ID pattern) ===
    # 0x00 suffix: original heroes
    0xF400: "Glaive",       # 85% - sequential in 0xFx00 range
    0xF500: "Koshka",       # 85% - sequential after F4
    0xF600: "Petal",        # 80% - sequential after F5
    0xF900: "Krul",         # 80% - original warrior
    0xFA00: "Adagio",       # 85% - sequential position
    0xFE00: "SAW",          # 90% - just before Skaarf(FF)
    # 0x01 suffix: season 1-3 heroes
    0x0001: "Taka",         # 90% - first assassin, early release
    0x0201: "Vox",          # 85% - sequential, high usage(10)
    0x0401: "Rona",         # 80% - season 1 warrior
    0x0C01: "Flicker",      # 75% - season 2 support
    0x1301: "Lance",        # 85% - season 2 captain, high usage(20)
    0x8901: "Alpha",        # 80% - season 2 warrior
    0x9801: "Churnwalker",  # 75% - between Grace(96) and Lorelai(99)
    0x9D01: "Varya",        # 70% - season 3 mage
    0xAD01: "Miho",         # 65% - between Kinetic(A4) and Silvernail(B0)
    # 0x03 suffix: season 4+ heroes
    0x9703: "Viola",        # 75% - between Warhawk(94) and Ishtar(9A)
    0x9C03: "Anka",         # 80% - season 4 assassin
    0x9D03: "Amael",        # CONFIRMED via replay screenshot (21.11.04 match, support build)
    0x9E03: "Shin",         # 70% - latest captain
    0x9F03: "Karas",        # SWAPPED with Amael - Karas is CP ranged dealer
}

# Reverse lookup: hero name -> binary ID
BINARY_HERO_NAME_TO_ID: Dict[str, int] = {
    name: bid for bid, name in BINARY_HERO_ID_MAP.items()
    if not name.startswith("unknown_")
}

# Binary Hero ID offset from player block marker (DA 03 EE)
HERO_ID_OFFSET = 0x0A9

# Hero name normalization for OCR typos
HERO_NAME_NORMALIZE: Dict[str, str] = {
    "mallene": "Malene",
    "ishutar": "Ishtar",
    # Add more typos as discovered
}

def normalize_hero_name(name: str) -> str:
    """Normalize hero name to handle OCR typos."""
    if not name:
        return name
    return HERO_NAME_NORMALIZE.get(name.lower(), name)

# Asset Hero ID map with integer keys for byte pattern matching
def _build_asset_hero_id_int_map() -> Dict[int, str]:
    """Convert ASSET_HERO_ID_MAP string keys to integers."""
    result = {}
    for key, name in ASSET_HERO_ID_MAP.items():
        try:
            # "009" -> 9, "010" -> 10
            int_key = int(key)
            result[int_key] = name
        except ValueError:
            continue
    return result

ASSET_HERO_ID_INT_MAP: Dict[int, str] = _build_asset_hero_id_int_map()

# Asset-based Item Name Mapping (extracted from game files)
ASSET_ITEM_NAMES = [
    "AC", "AMR", "CapPlate", "Crisis_Crystal_Con", "Crisis_Weapon_Con",
    "Crucible", "EMP", "Echo", "Flare_Proj_A", "Flare_Proj_E", "Flare_Ring_A",
    "Fountain", "Frostburn", "GraveLash", "HealingFlask", "IronGuard",
    "Protector", "ReflexBlock", "ScoutTrap", "Shell", "Shiv", "Slumbering_Husk",
    "StormGuard", "UC", "WarTreads", "WindRider"
]

# Hero ID Mapping
# Based on internal game order and community research
HERO_ID_MAP: Dict[int, Dict] = {
    # Original Heroes (Season 1)
    1: {"name": "Adagio", "name_ko": "아다지오", "role": "Captain"},
    2: {"name": "Catherine", "name_ko": "캐서린", "role": "Captain"},
    3: {"name": "Glaive", "name_ko": "글레이브", "role": "Warrior"},
    4: {"name": "Koshka", "name_ko": "코쉬카", "role": "Assassin"},
    5: {"name": "Krul", "name_ko": "크럴", "role": "Warrior"},
    6: {"name": "Petal", "name_ko": "페탈", "role": "Mage"},
    7: {"name": "Ringo", "name_ko": "링고", "role": "Sniper"},
    8: {"name": "SAW", "name_ko": "쏘우", "role": "Sniper"},
    9: {"name": "Skaarf", "name_ko": "스카프", "role": "Mage"},
    10: {"name": "Taka", "name_ko": "타카", "role": "Assassin"},
    
    # Season 1 Additions
    11: {"name": "Joule", "name_ko": "쥴", "role": "Warrior"},
    12: {"name": "Ardan", "name_ko": "아단", "role": "Captain"},
    13: {"name": "Celeste", "name_ko": "셀레스트", "role": "Mage"},
    14: {"name": "Vox", "name_ko": "복스", "role": "Sniper"},
    15: {"name": "Rona", "name_ko": "로나", "role": "Warrior"},
    16: {"name": "Fortress", "name_ko": "포트리스", "role": "Captain"},
    17: {"name": "Reim", "name_ko": "라임", "role": "Mage"},
    
    # Season 2 Heroes
    18: {"name": "Phinn", "name_ko": "핀", "role": "Captain"},
    19: {"name": "Blackfeather", "name_ko": "흑깃", "role": "Assassin"},
    20: {"name": "Skye", "name_ko": "스카이", "role": "Mage"},
    21: {"name": "Kestrel", "name_ko": "케스트럴", "role": "Sniper"},
    22: {"name": "Alpha", "name_ko": "알파", "role": "Warrior"},
    23: {"name": "Lance", "name_ko": "랜스", "role": "Captain"},
    24: {"name": "Ozo", "name_ko": "오조", "role": "Warrior"},
    25: {"name": "Lyra", "name_ko": "라이라", "role": "Captain"},
    26: {"name": "Samuel", "name_ko": "사무엘", "role": "Mage"},
    27: {"name": "Baron", "name_ko": "바론", "role": "Sniper"},
    28: {"name": "Gwen", "name_ko": "그웬", "role": "Sniper"},
    29: {"name": "Flicker", "name_ko": "플리커", "role": "Captain"},
    30: {"name": "Idris", "name_ko": "이드리스", "role": "Assassin"},
    
    # Season 3 Heroes  
    31: {"name": "Grumpjaw", "name_ko": "사슬니", "role": "Warrior"},
    32: {"name": "Baptiste", "name_ko": "바티스트", "role": "Mage"},
    33: {"name": "Grace", "name_ko": "그레이스", "role": "Captain"},
    34: {"name": "Reza", "name_ko": "레자", "role": "Assassin"},
    35: {"name": "Churnwalker", "name_ko": "어둠추적자", "role": "Captain"},
    36: {"name": "Lorelai", "name_ko": "로렐라이", "role": "Captain"},
    37: {"name": "Tony", "name_ko": "토니", "role": "Warrior"},
    38: {"name": "Varya", "name_ko": "바리야", "role": "Mage"},
    39: {"name": "Malene", "name_ko": "말렌", "role": "Mage"},
    40: {"name": "Kensei", "name_ko": "켄세이", "role": "Warrior"},
    41: {"name": "Kinetic", "name_ko": "키네틱", "role": "Sniper"},
    42: {"name": "San Feng", "name_ko": "삼봉", "role": "Warrior"},
    43: {"name": "Silvernail", "name_ko": "실버네일", "role": "Sniper"},
    44: {"name": "Yates", "name_ko": "예이츠", "role": "Captain"},
    45: {"name": "Inara", "name_ko": "이나라", "role": "Warrior"},
    
    # Season 4+ Heroes
    46: {"name": "Magnus", "name_ko": "마그누스", "role": "Mage"},
    47: {"name": "Caine", "name_ko": "케인", "role": "Sniper"},
    48: {"name": "Leo", "name_ko": "레오", "role": "Warrior"},
    49: {"name": "Viola", "name_ko": "비올라", "role": "Captain"},
    50: {"name": "Warhawk", "name_ko": "워호크", "role": "Sniper"},
    51: {"name": "Anka", "name_ko": "앙카", "role": "Assassin"},
    52: {"name": "Miho", "name_ko": "미호", "role": "Assassin"},
    53: {"name": "Karas", "name_ko": "카라스", "role": "Mage"},  # CP ranged dealer
    54: {"name": "Shin", "name_ko": "신", "role": "Captain"},
    55: {"name": "Ishtar", "name_ko": "이슈타르", "role": "Sniper"},
    56: {"name": "Ylva", "name_ko": "일바", "role": "Assassin"},
    57: {"name": "Amael", "name_ko": "아마엘", "role": "Captain"},  # tank/support
}

# Reverse lookup: name to ID
HERO_NAME_TO_ID: Dict[str, int] = {
    info["name"].lower(): id for id, info in HERO_ID_MAP.items()
}

# Item ID Mapping — composed 16-bit id keys (qty*256 + low_byte)
# =============================================================================
# The [10 04 3D] acquire event stores a 16-bit BIG-ENDIAN item id:
#   high byte = qty field (+9)  →  1 (ids 457-511) or 2 (ids 512-539)
#   low  byte = id field  (+10)
# Confirmed against real .vgr bytes and VGNA /replay/result ground truth
# (VGNA_REPLAY_SERVER_2026-07-30.md §5, ITEM_LIST_KR_EN.md §0).
#
# status vocabulary:
#   confirmed      code(price/co-buy) + VGNA + local all agree
#   vgna_verified  conflict re-checked on local replays; VGNA won
#   local_override local evidence refuted VGNA (493: 500g x10 = Weapon Infusion)
#   vgna           adopted from VGNA, locally plausible, not recipe-verified
#   unknown        not in VGNA sample; identity tentative
# =============================================================================
ITEM_ID_MAP: Dict[int, Dict] = {
    # External ground truth calls this Halcyon Potion, which cannot be right:
    # that item is 3v3-only and has since been removed, while this one is handed
    # to every player in a corpus that is overwhelmingly 5v5 (4970 vs 105 HF
    # matches). It is the Healing Flask instead. That also settles a
    # contradiction in ITEM_LIST_KR_EN.md, which argued Halcyon Potion could not
    # be a removed item because "it shows up in real matches" - what shows up is
    # this id, under the wrong name.
    457: {"name": "Healing Flask", "category": "Consumable", "tier": 0, "status": "local_override", "qty": 1, "low": 201},
    458: {"name": "Weapon Blade", "category": "Weapon", "tier": 1, "status": "confirmed", "qty": 1, "low": 202},
    459: {"name": "Crystal Bit", "category": "Crystal", "tier": 1, "status": "confirmed", "qty": 1, "low": 203},
    460: {"name": "Swift Shooter", "category": "Weapon", "tier": 1, "status": "confirmed", "qty": 1, "low": 204},
    461: {"name": "Six Sins", "category": "Weapon", "tier": 2, "status": "confirmed", "qty": 1, "low": 205},
    462: {"name": "Eclipse Prism", "category": "Crystal", "tier": 2, "status": "confirmed", "qty": 1, "low": 206},
    463: {"name": "Blazing Salvo", "category": "Weapon", "tier": 2, "status": "confirmed", "qty": 1, "low": 207},
    464: {"name": "Sorrowblade", "category": "Weapon", "tier": 3, "status": "confirmed", "qty": 1, "low": 208},
    465: {"name": "Shatterglass", "category": "Crystal", "tier": 3, "status": "confirmed", "qty": 1, "low": 209},
    466: {"name": "Tornado Trigger", "category": "Weapon", "tier": 3, "status": "confirmed", "qty": 1, "low": 210},
    467: {"name": "Oakheart", "category": "Defense", "tier": 1, "status": "confirmed", "qty": 1, "low": 211},
    468: {"name": "Dragonheart", "category": "Defense", "tier": 2, "status": "confirmed", "qty": 1, "low": 212},
    469: {"name": "Light Armor", "category": "Defense", "tier": 1, "status": "confirmed", "qty": 1, "low": 213},
    470: {"name": "Coat of Plates", "category": "Defense", "tier": 2, "status": "confirmed", "qty": 1, "low": 214},
    471: {"name": "Metal Jacket", "category": "Defense", "tier": 3, "status": "confirmed", "qty": 1, "low": 215},  # read off the result screen for two players (Reim, Grumpjaw)
    472: {"name": "Energy Battery", "category": "Crystal", "tier": 1, "status": "confirmed", "qty": 1, "low": 216},
    473: {"name": "Hourglass", "category": "Crystal", "tier": 1, "status": "confirmed", "qty": 1, "low": 217},
    474: {"name": "Void Battery", "category": "Crystal", "tier": 2, "status": "confirmed", "qty": 1, "low": 218},
    475: {"name": "Chronograph", "category": "Crystal", "tier": 2, "status": "confirmed", "qty": 1, "low": 219},
    476: {"name": "Clockwork", "category": "Crystal", "tier": 3, "status": "confirmed", "qty": 1, "low": 220},
    477: {"name": "Sprint Boots", "category": "Utility", "tier": 1, "status": "confirmed", "qty": 1, "low": 221},
    478: {"name": "Travel Boots", "category": "Utility", "tier": 2, "status": "confirmed", "qty": 1, "low": 222},
    479: {"name": "Serpent's Mask", "category": "Weapon", "tier": 3, "status": "confirmed", "qty": 1, "low": 223},
    480: {"name": "Tension Bow", "category": "Weapon", "tier": 3, "status": "confirmed", "qty": 1, "low": 224},  # read off the result screen (Gwen); all six of that build's items matched
    481: {"name": "Flare", "category": "Consumable", "tier": 0, "status": "vgna_verified", "qty": 1, "low": 225},
    482: {"name": "Bonesaw", "category": "Weapon", "tier": 3, "status": "confirmed", "qty": 1, "low": 226},
    484: {"name": "Shiversteel", "category": "Defense", "tier": 3, "status": "vgna", "qty": 1, "low": 228},
    485: {"name": "Reflex Block", "category": "Defense", "tier": 2, "status": "confirmed", "qty": 1, "low": 229},
    486: {"name": "Frostburn", "category": "Crystal", "tier": 3, "status": "confirmed", "qty": 1, "low": 230},
    487: {"name": "Fountain of Renewal", "category": "Defense", "tier": 3, "status": "confirmed", "qty": 1, "low": 231},
    488: {"name": "Crucible", "category": "Defense", "tier": 3, "status": "confirmed", "qty": 1, "low": 232},
    # Every one of its 4 buyers acquires it within 1-3s of a tier-3 boots
    # purchase (War Treads / Halcyon Chargers / Teleport Boots), while their
    # Sprint and Travel Boots came hundreds of seconds earlier. Its low byte
    # also sits inside the boots run: 221 Sprint, 222 Travel, 233 here,
    # 234 Halcyon Chargers, 241 War Treads. Journey Boots is the only real
    # boots left without an id and matches the rarity, but several tier-3
    # boots sharing one timestamp is unexplained, so this stays a hypothesis.
    489: {"name": "Unknown 489", "category": "Utility", "tier": 3, "status": "unknown", "qty": 1, "low": 233},  # ~1400g single-purchase = equipment (NOT consumable); 4 captain buyers, no recipe signal
    490: {"name": "Halcyon Chargers", "category": "Utility", "tier": 3, "status": "confirmed", "qty": 1, "low": 234},
    491: {"name": "Tyrant's Monocle", "category": "Weapon", "tier": 3, "status": "vgna_verified", "qty": 1, "low": 235},
    492: {"name": "Aftershock", "category": "Crystal", "tier": 3, "status": "confirmed", "qty": 1, "low": 236},
    493: {"name": "Weapon Infusion", "category": "Consumable", "tier": 0, "status": "local_override", "qty": 1, "low": 237},
    494: {"name": "Crystal Infusion", "category": "Consumable", "tier": 0, "status": "confirmed", "qty": 1, "low": 238},
    495: {"name": "Scout Trap", "category": "Consumable", "tier": 0, "status": "unknown", "qty": 1, "low": 239},
    496: {"name": "Broken Myth", "category": "Crystal", "tier": 3, "status": "confirmed", "qty": 1, "low": 240},
    497: {"name": "War Treads", "category": "Utility", "tier": 3, "status": "vgna_verified", "qty": 1, "low": 241},
    498: {"name": "Atlas Pauldron", "category": "Defense", "tier": 3, "status": "confirmed", "qty": 1, "low": 242},
    499: {"name": "Book of Eulogies", "category": "Weapon", "tier": 1, "status": "confirmed", "qty": 1, "low": 243},
    500: {"name": "Barbed Needle", "category": "Weapon", "tier": 2, "status": "confirmed", "qty": 1, "low": 244},
    501: {"name": "Light Shield", "category": "Defense", "tier": 1, "status": "confirmed", "qty": 1, "low": 245},
    502: {"name": "Kinetic Shield", "category": "Defense", "tier": 2, "status": "confirmed", "qty": 1, "low": 246},
    503: {"name": "Aegis", "category": "Defense", "tier": 3, "status": "confirmed", "qty": 1, "low": 247},
    504: {"name": "Lifespring", "category": "Defense", "tier": 2, "status": "confirmed", "qty": 1, "low": 248},
    505: {"name": "Heavy Steel", "category": "Weapon", "tier": 2, "status": "confirmed", "qty": 1, "low": 249},
    506: {"name": "Piercing Spear", "category": "Weapon", "tier": 2, "status": "confirmed", "qty": 1, "low": 250},
    507: {"name": "Breaking Point", "category": "Weapon", "tier": 3, "status": "confirmed", "qty": 1, "low": 251},
    508: {"name": "Lucky Strike", "category": "Weapon", "tier": 2, "status": "confirmed", "qty": 1, "low": 252},
    509: {"name": "Alternating Current", "category": "Crystal", "tier": 3, "status": "confirmed", "qty": 1, "low": 253},
    510: {"name": "Piercing Shard", "category": "Crystal", "tier": 2, "status": "confirmed", "qty": 1, "low": 254},
    511: {"name": "Eve of Harvest", "category": "Crystal", "tier": 3, "status": "confirmed", "qty": 1, "low": 255},
    512: {"name": "Heavy Prism", "category": "Crystal", "tier": 2, "status": "confirmed", "qty": 2, "low": 0},
    513: {"name": "Stormguard Banner", "category": "Utility", "tier": 2, "status": "vgna_verified", "qty": 2, "low": 1},
    # Both buyers get it at t=1.2s and t=1.9s, ahead of the two items every
    # player is handed at the start, so it is granted rather than bought. Only
    # 2 of 502 players have it though, unlike 457/526 which reach 456, so it
    # looks conditional on mode or situation. Too few samples for STARTER_IDS.
    515: {"name": "Unknown 515", "category": "Weapon", "tier": 3, "status": "unknown", "qty": 2, "low": 3},
    # 518 precedes 516 in both players that own both (755->925s, 1028->1072s),
    # which is what a component looks like. All buyers are captains and buy
    # only defensive items alongside. Neither wiki lists a matching item, so
    # these may post-date the sources - candidates for a VG:CE-era addition.
    516: {"name": "Unknown 516", "category": "Defense", "tier": 3, "status": "unknown", "qty": 2, "low": 4},
    517: {"name": "Minion's Foot", "category": "Weapon", "tier": 1, "status": "vgna_verified", "qty": 2, "low": 5},
    518: {"name": "Unknown 518", "category": "Defense", "tier": 2, "status": "unknown", "qty": 2, "low": 6},  # obs ~600g reads T2
    519: {"name": "Stormcrown", "category": "Utility", "tier": 3, "status": "local_override", "qty": 2, "low": 7},  # VGNA said Teleport Boots; local: Chronograph 82% + Stormguard Banner 96% co-buy (= recipe) + jungle 41% -> Stormcrown. Teleport Boots now unlocated.
    520: {"name": "Poisoned Shiv", "category": "Weapon", "tier": 3, "status": "confirmed", "qty": 2, "low": 8},
    522: {"name": "Spellfire", "category": "Crystal", "tier": 3, "status": "confirmed", "qty": 2, "low": 10},
    523: {"name": "Dragon's Eye", "category": "Crystal", "tier": 3, "status": "confirmed", "qty": 2, "low": 11},
    524: {"name": "Spellsword", "category": "Weapon", "tier": 3, "status": "confirmed", "qty": 2, "low": 12},
    525: {"name": "Slumbering Husk", "category": "Defense", "tier": 3, "status": "confirmed", "qty": 2, "low": 13},
    # Auto-granted to every player at match start, not bought. Same detection
    # signature as 457: 456/502 players, and per match either all players have
    # it (51) or none do (5, start frames missing) - never partial. External
    # ground truth calls it a purchased "Vision Totem"; that is wrong.
    526: {"name": "Scout Camera", "category": "Utility", "tier": 0, "status": "local_override", "qty": 2, "low": 14},
    527: {"name": "SuperScout 2000", "category": "Utility", "tier": 3, "status": "local_override", "qty": 2, "low": 15},  # VGNA said Stormcrown; local: captain-only + ScoutTuff 94%/ScoutPak 87% co-buy, Chronograph+SGB only 16% -> scout-line, not Stormcrown
    # Components of SuperScout 2000 (527), not consumables - an earlier pass
    # demoted them to tier 0 on the strength of a "500g 소모품" doc line and had
    # to be reverted. They vanish from a build by being upgraded away, which is
    # UPGRADE_TREE's job, not the slot ranking's.
    528: {"name": "ScoutTuff", "category": "Utility", "tier": 2, "status": "vgna_verified", "qty": 2, "low": 16},  # captain + ~200g rules out old-code Contraption (2100g)
    529: {"name": "ScoutPak", "category": "Utility", "tier": 2, "status": "vgna_verified", "qty": 2, "low": 17},  # captain + ~500g rules out old-code War Treads (1900g)
    530: {"name": "Teleport Boots", "category": "Utility", "tier": 3, "status": "local_override", "qty": 2, "low": 18},  # VGNA said Journey Boots; truth match6 (Finals g3): 530-holders = Kinetic/Reim/San Feng, user-confirmed as Teleport buyers. Co-occurs with other boots because Teleport is bought for backdoor via sell+rebuy (boots NOT mutually exclusive in acquire log). Journey Boots is rarely bought (inefficient) -> true id unlocated.
    531: {"name": "Rook's Decree", "category": "Defense", "tier": 3, "status": "vgna_verified", "qty": 2, "low": 19},  # truth-confirmed: Lorelai (Acex) build, match5 (user-confirmed)
    532: {"name": "Flare Loader", "category": "Utility", "tier": 2, "status": "vgna_verified", "qty": 2, "low": 20},  # 5v5 vision item (3v3 counterpart is "Flare Gun"). truth icon = gold spark-gun (user-ID'd as Flare Gun; official 5v5 name = Flare Loader per VaingloryFire). VGNA was correct here.
    533: {"name": "Pulseweave", "category": "Defense", "tier": 3, "status": "confirmed", "qty": 2, "low": 21},
    534: {"name": "Capacitor Plate", "category": "Defense", "tier": 3, "status": "confirmed", "qty": 2, "low": 22},
    535: {"name": "Protector Contract", "category": "Defense", "tier": 2, "status": "vgna_verified", "qty": 2, "low": 23},  # captain + 600g exact match
    536: {"name": "Dragonblood Contract", "category": "Utility", "tier": 2, "status": "vgna_verified", "qty": 2, "low": 24},  # truth-confirmed: Fortress (Dawg) purple item, match2 (user-confirmed)
    538: {"name": "Warmail", "category": "Defense", "tier": 2, "status": "confirmed", "qty": 2, "low": 26},
    539: {"name": "Celestial Shroud", "category": "Crystal", "tier": 3, "status": "vgna_verified", "qty": 2, "low": 27},
}

# Reverse lookup: item name to ID
ITEM_NAME_TO_ID: Dict[str, int] = {
    info["name"].lower(): id for id, info in ITEM_ID_MAP.items()
}

# Skin Tier Mapping
SKIN_TIERS = {
    0: "Default",
    1: "Rare (Tier I)",
    2: "Epic (Tier II)",
    3: "Legendary (Tier III)",
    4: "Special Edition (SE)",
    5: "Limited Edition (LE)",
}


class VGRMapping:
    """Mapping utility for Vainglory game data"""
    
    @staticmethod
    def get_hero_by_id(hero_id: int) -> Optional[Dict]:
        """Get hero info by ID"""
        return HERO_ID_MAP.get(hero_id)
    
    @staticmethod
    def get_hero_by_name(name: str) -> Optional[Dict]:
        """Get hero info by name"""
        name_lower = name.lower()
        for id, info in HERO_ID_MAP.items():
            if info["name"].lower() == name_lower or info["name_ko"] == name:
                return {"id": id, **info}
        return None
    
    @staticmethod
    def get_item_by_id(item_id: int) -> Optional[Dict]:
        """Get item info by ID"""
        return ITEM_ID_MAP.get(item_id)
    
    @staticmethod
    def get_item_by_name(name: str) -> Optional[Dict]:
        """Get item info by name"""
        name_lower = name.lower()
        for id, info in ITEM_ID_MAP.items():
            if info["name"].lower() == name_lower:
                return {"id": id, **info}
        return None
    
    @staticmethod
    def get_all_heroes() -> List[Dict]:
        """Get all heroes with IDs"""
        return [{"id": id, **info} for id, info in HERO_ID_MAP.items()]
    
    @staticmethod
    def get_all_items() -> List[Dict]:
        """Get all items with IDs"""
        return [{"id": id, **info} for id, info in ITEM_ID_MAP.items()]
    
    @staticmethod
    def search_hero(query: str) -> List[Dict]:
        """Search heroes by partial name match"""
        query_lower = query.lower()
        results = []
        for id, info in HERO_ID_MAP.items():
            if query_lower in info["name"].lower() or query_lower in info.get("name_ko", ""):
                results.append({"id": id, **info})
        return results
    
    @staticmethod
    def search_item(query: str) -> List[Dict]:
        """Search items by partial name match"""
        query_lower = query.lower()
        results = []
        for id, info in ITEM_ID_MAP.items():
            if query_lower in info["name"].lower():
                results.append({"id": id, **info})
        return results
    
    @staticmethod
    def export_mapping(output_path: str = "vg_mapping.json"):
        """Export all mappings to JSON file"""
        data = {
            "heroes": [{"id": id, **info} for id, info in HERO_ID_MAP.items()],
            "items": [{"id": id, **info} for id, info in ITEM_ID_MAP.items()],
            "skin_tiers": SKIN_TIERS
        }
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return output_path


def main():
    """CLI for VGR Mapping"""
    import argparse
    
    parser = argparse.ArgumentParser(description='VGR Mapping - Hero/Item ID Lookup')
    parser.add_argument('command', choices=['heroes', 'items', 'search', 'export'],
                        help='Command to run')
    parser.add_argument('-q', '--query', help='Search query')
    parser.add_argument('-i', '--id', type=int, help='ID to lookup')
    parser.add_argument('-o', '--output', default='vg_mapping.json', help='Output file')
    
    args = parser.parse_args()
    mapping = VGRMapping()
    
    if args.command == 'heroes':
        if args.id:
            hero = mapping.get_hero_by_id(args.id)
            if hero:
                print(f"ID {args.id}: {hero['name']} ({hero['name_ko']}) - {hero['role']}")
            else:
                print(f"Hero ID {args.id} not found")
        else:
            print(f"{'ID':>3} {'Name':<15} {'한글':<10} {'Role':<10}")
            print("-" * 45)
            for hero in mapping.get_all_heroes():
                print(f"{hero['id']:>3} {hero['name']:<15} {hero['name_ko']:<10} {hero['role']:<10}")
    
    elif args.command == 'items':
        if args.id:
            item = mapping.get_item_by_id(args.id)
            if item:
                print(f"ID {args.id}: {item['name']} ({item['category']}, Tier {item['tier']})")
            else:
                print(f"Item ID {args.id} not found")
        else:
            current_category = None
            for item in mapping.get_all_items():
                if item['category'] != current_category:
                    current_category = item['category']
                    print(f"\n=== {current_category} ===")
                print(f"  {item['id']:>3}: [{item['tier']}] {item['name']}")
    
    elif args.command == 'search':
        if not args.query:
            print("Usage: vgr_mapping.py search -q <query>")
        else:
            heroes = mapping.search_hero(args.query)
            items = mapping.search_item(args.query)
            
            if heroes:
                print("Heroes:")
                for h in heroes:
                    print(f"  ID {h['id']}: {h['name']} ({h['name_ko']})")
            
            if items:
                print("Items:")
                for i in items:
                    print(f"  ID {i['id']}: {i['name']}")
            
            if not heroes and not items:
                print("No results found")
    
    elif args.command == 'export':
        output = mapping.export_mapping(args.output)
        print(f"✓ Mapping exported to: {output}")
        print(f"  - Heroes: {len(HERO_ID_MAP)}")
        print(f"  - Items: {len(ITEM_ID_MAP)}")


if __name__ == '__main__':
    main()


# Direct recipes: result id -> the ids consumed to make it. Taken from
# item_price_verify.OFFICIAL_RECIPES, which UPGRADE_TREE was derived from but
# flattened transitively, losing which components a specific result actually
# eats. Replaying purchases against this table gives an exact inventory, since
# the same component bought three times and upgraded twice leaves one behind -
# something a set of purchased ids cannot express.
# Journey Boots and Contraption are absent: neither has a known item id yet.
RECIPES = {
    461: (458,),  # Six Sins <- Weapon Blade
    462: (459,),  # Eclipse Prism <- Crystal Bit
    463: (460,),  # Blazing Salvo <- Swift Shooter
    464: (505, 461,),  # Sorrowblade <- Heavy Steel + Six Sins
    465: (512, 462,),  # Shatterglass <- Heavy Prism + Eclipse Prism
    466: (463, 508,),  # Tornado Trigger <- Blazing Salvo + Lucky Strike
    468: (467,),  # Dragonheart <- Oakheart
    470: (469,),  # Coat of Plates <- Light Armor
    471: (470,),  # Metal Jacket <- Coat of Plates
    474: (472,),  # Void Battery <- Energy Battery
    475: (473,),  # Chronograph <- Hourglass
    476: (474, 475,),  # Clockwork <- Void Battery + Chronograph
    478: (477,),  # Travel Boots <- Sprint Boots
    479: (505, 500,),  # Serpent's Mask <- Heavy Steel + Barbed Needle
    480: (461, 506,),  # Tension Bow <- Six Sins + Piercing Spear
    482: (506, 463,),  # Bonesaw <- Piercing Spear + Blazing Salvo
    484: (468, 463,),  # Shiversteel <- Dragonheart + Blazing Salvo
    485: (467,),  # Reflex Block <- Oakheart
    486: (512, 462,),  # Frostburn <- Heavy Prism + Eclipse Prism
    487: (504, 502,),  # Fountain of Renewal <- Lifespring + Kinetic Shield
    488: (468, 485,),  # Crucible <- Dragonheart + Reflex Block
    490: (478, 474,),  # Halcyon Chargers <- Travel Boots + Void Battery
    491: (461, 508,),  # Tyrant's Monocle <- Six Sins + Lucky Strike
    492: (462, 475,),  # Aftershock <- Eclipse Prism + Chronograph
    496: (512, 510,),  # Broken Myth <- Heavy Prism + Piercing Shard
    497: (478, 468,),  # War Treads <- Travel Boots + Dragonheart
    498: (470,),  # Atlas Pauldron <- Coat of Plates
    500: (499,),  # Barbed Needle <- Book of Eulogies
    502: (501,),  # Kinetic Shield <- Light Shield
    503: (485, 502,),  # Aegis <- Reflex Block + Kinetic Shield
    504: (467,),  # Lifespring <- Oakheart
    505: (458,),  # Heavy Steel <- Weapon Blade
    506: (458,),  # Piercing Spear <- Weapon Blade
    507: (505, 463,),  # Breaking Point <- Heavy Steel + Blazing Salvo
    508: (517,),  # Lucky Strike <- Minion's Foot
    509: (512, 463,),  # Alternating Current <- Heavy Prism + Blazing Salvo
    510: (459,),  # Piercing Shard <- Crystal Bit
    511: (512, 474,),  # Eve of Harvest <- Heavy Prism + Void Battery
    512: (459,),  # Heavy Prism <- Crystal Bit
    513: (467,),  # Stormguard Banner <- Oakheart
    519: (513, 475,),  # Stormcrown <- Stormguard Banner + Chronograph
    520: (463, 500,),  # Poisoned Shiv <- Blazing Salvo + Barbed Needle
    522: (512, 462,),  # Spellfire <- Heavy Prism + Eclipse Prism
    523: (512, 462,),  # Dragon's Eye <- Heavy Prism + Eclipse Prism
    524: (505, 475,),  # Spellsword <- Heavy Steel + Chronograph
    525: (470, 502,),  # Slumbering Husk <- Coat of Plates + Kinetic Shield
    527: (529, 528,),  # SuperScout 2000 <- ScoutPak + ScoutTuff
    528: (532,),  # ScoutTuff <- Flare Loader
    529: (473,),  # ScoutPak <- Hourglass
    530: (478,),  # Teleport Boots <- Travel Boots
    531: (468, 475,),  # Rook's Decree <- Dragonheart + Chronograph
    532: (467,),  # Flare Loader <- Oakheart
    533: (468, 504,),  # Pulseweave <- Dragonheart + Lifespring
    534: (468, 475,),  # Capacitor Plate <- Dragonheart + Chronograph
    535: (467,),  # Protector Contract <- Oakheart
    538: (469, 501,),  # Warmail <- Light Armor + Light Shield
}
