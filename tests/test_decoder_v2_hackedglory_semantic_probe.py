import unittest

from vg.decoder_v2.hackedglory_semantic_probe import build_semantic_probe


class TestHackedGlorySemanticProbe(unittest.TestCase):
    def test_build_probe_marks_local_semantic_coverage(self) -> None:
        parsed = {
            "replay_name": "match",
            "replay_file": "match.0.vgr",
            "match_info": {"mode": "GameMode_5v5_Ranked"},
            "teams": {
                "left": [
                    {
                        "name": "left1",
                        "uuid": "uuid-left",
                        "team": "left",
                        "entity_id": 56581,
                        "hero_name": "Kestrel",
                    }
                ],
                "right": [
                    {
                        "name": "right1",
                        "uuid": "uuid-right",
                        "team": "right",
                        "entity_id": 56325,
                        "hero_name": "Celeste",
                    }
                ],
            },
        }
        debug_payload = {
            "safe_output": {
                "accepted_fields": {"winner": "left", "gold": {"accepted_for_index": True}},
                "players": [
                    {
                        "name": "left1",
                        "team": "left",
                        "entity_id": 56581,
                        "hero_name": "Kestrel",
                        "kills": 1,
                        "deaths": 0,
                        "assists": 1,
                        "gold": 5000,
                        "gold_status": "accepted",
                    },
                    {
                        "name": "right1",
                        "team": "right",
                        "entity_id": 56325,
                        "hero_name": "Celeste",
                        "kills": 0,
                        "deaths": 1,
                        "assists": 0,
                        "gold": 4500,
                        "gold_status": "accepted",
                    },
                ],
            },
            "completeness": {
                "status": "complete_confirmed",
                "signals": {
                    "max_death_header_ts": 100.0,
                    "max_item_ts": 90.0,
                },
            },
            "duration": {"estimate_seconds": 100},
            "winner_debug": {"accepted": True, "winner": "left"},
            "kda_debug": {
                "accepted": True,
                "players": [
                    {
                        "player_name": "left1",
                        "kills": 1,
                        "deaths": 0,
                        "assists": 1,
                    },
                    {
                        "player_name": "right1",
                        "kills": 0,
                        "deaths": 1,
                        "assists": 0,
                    },
                ],
            },
            "minion_candidates": [{"player_name": "left1"}],
        }

        report = build_semantic_probe(parsed, debug_payload)
        targets = {item["target"]: item for item in report["targets"]}

        self.assertEqual(report["schema_version"], "hackedglory_semantic_probe.v1")
        self.assertEqual(targets["roster_identity"]["status"], "covered")
        self.assertEqual(targets["uuid_identity"]["status"], "covered")
        self.assertEqual(targets["kill_attribution"]["status"], "covered")
        self.assertEqual(targets["gold_xp_total"]["status"], "partial")
        self.assertEqual(targets["creep_score_minions"]["status"], "partial")
        self.assertEqual(report["summary"]["local_semantic_ready_players"], 2)
        readiness = report["summary"]["scoreboard_readiness"]
        self.assertEqual(readiness["identity_players"], 2)
        self.assertEqual(readiness["kda_players"], 2)
        self.assertEqual(readiness["gold_players"], 2)
        self.assertEqual(readiness["local_export_ready_players"], 2)
        self.assertEqual(readiness["strict_hackedglory_replay_ready_players"], 0)
        self.assertEqual(readiness["blocking_fields"], ["xp_total", "level"])


if __name__ == "__main__":
    unittest.main()
