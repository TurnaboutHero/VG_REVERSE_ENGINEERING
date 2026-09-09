# Windows replay acceptance follow-up

The offline entity-context and counter-audit tools remain separate from final
scoreboard acceptance. On 2026-09-10 KST, an unmodified practice replay played
through its result screen, while the C16 replacement returned to the home menu.
C16's late-game event and KDA comparison therefore remains unverified.

The runtime used Windows 11, active console session 1 with a fresh WTS unlock
check before each input/capture, and executable SHA-256
`659f9eed557a426db57554d2a768efe34ba9fe02ba1085d77db64390b0d92642`.
The decoder/research snapshot was `aa014b23a365fc1abb15e38b33ad963a3ab55076`.

## Observations

| Experiment | Observed result | Boundary |
|---|---|---|
| C16 source and replacement | All 171 source sections matched the existing corpus hashes; all 171 substituted sections matched the source. | Matching files do not establish successful replay initialization. |
| C16 replay entry | Home menu after the replay click and again about 44 seconds later; game process remained alive. | Cause is unknown. No C16 gameplay or result-screen comparison was obtained. |
| Unmodified practice control | A separate practice match and its replay both ended at HUD 2:44, surrender, K/D/A 0/0/0. Intermediate replay HUDs showed 0:55 and 2:18. | Confirms basic replay operation for this recording, not C16 compatibility, replacement-slot correctness or non-surrender score semantics. |

The normal control ran after restarting the game, in a different process and
slot. A fresh successful replacement of one normal recording into another slot
was not performed during this follow-up. The C16 click coordinates were inside
the replay button in the preceding screenshot, but that screenshot preceded the
click by about two minutes; all intervening UI states were not captured.
These differences prevent attributing the home-menu return to C16 content alone.

## Next acceptance steps

1. Replace a fresh slot with the preserved normal control recording and verify
   playback. Preserve original files and compare all copied section hashes.
2. Under matching observation conditions, compare normal and C16 file-open and
   initialization paths. Capture the screen immediately before the replay click
   and identify the first different processing result. Do not infer a texture
   failure or unsupported format from the home menu alone.
3. If C16 playback succeeds, observe before native game time 27:45 and compare
   the final same-timestamp score group near 27:49.626, the later Silvernail death
   near 27:51.296, and the final display. These are frame-anchor interpolation
   targets, not independently measured callback or HUD rendering times.

The recorded expectation is Silvernail `5/7/13 -> 6/7/13` and Miho
`9/8/12 -> 9/9/12`; the later Silvernail death has no recorded death-counter
increment. Those are offline expectations, not values observed in C16 gameplay
here. See the [0452 investigation](POSTGAME_OFFLINE_2026-09-09.md) and
[counter audit](TERMINAL_COUNTER_AUDIT_2026-09-09.md). No cutoff, credited-killer
rule or final-stat acceptance policy was changed.

## Evidence and cleanup

The [anonymized observation record](evidence/2026-09-10-replay-acceptance.json)
includes hashes of the retained private screenshots and source report.
Those originals contain player/session context and are not distributed here;
their hashes identify the originals and do not substitute for public visual
inspection. The public record is a derived report of the observed run.

The 171 substituted files were archived and the original 17 slot files restored
with matching hashes before the second practice experiment. That later control
created its own 17-section recording, retained separately for the next test.
Original C16 inputs were only read. Owned game/worker processes and the temporary
scheduled task were removed; the pre-existing Steam process was preserved.
