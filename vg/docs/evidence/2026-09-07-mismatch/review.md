# Bounded mismatch evidence review

Verdict: PASS for cause investigation and evidence report, not production decoder completion.

Reviewed 2026-09-07 against stated source HEAD `645756e6734f8ee3e4130e780acae36981ce835f`; reviewed reconciliation script SHA-256 `cf5788fadc78ac02f26a72b8b3839e832841f86c11687016d2a9ac597f0eda29` and reconciled JSON `f69fb0a1c5c30b87916f29d901a9e9b2a5829240626f061f08bbe974614db699`.

Executed `python3 work/mismatch-audit/verify_reconciliation.py`: exit 0, PASS, repeated output equals saved evidence. M5 4→0; M6 raw11, baseline-only4, clock-only7, both0. Earliest-baseline and latest-checkpoint reconstructions agree at both bounds of each capture second. M9 emits no corrected numeric scores.

Independently parsed source exports: 13,110 snapshots have payload length746 and 110 length750; every observed payload326 flag is0. Implementation checks both length alternatives and flag before stat use. Every exported relevant event is ADD mode0, with attribute layer0 or resource layerNone, consistent with the bounded accumulation algorithm. This is not general SET support.

M9 clock jumps verified directly: frame6→7 −1111.0875015s,9→10 +1131.0978851s,32→33 −1111.0939331s. Archive evidence contains85 members whose recorded original/current SHA-256 strings all agree;41 ZIPs searched,1 matching archive. This review verifies exported archive evidence, not remote ZIP reread.

107 matched actors confirmed: all11 matches have10 decoded actors;M5,M6,M9 each have9 matched truth actors. 294 accepted KDA values plus27 unscorable values account for107×3;78 accepted resource14/CS plus9 unscorable account for87. Report explicitly preserves missing-row caveat and does not count M9 as repaired or silently convert missing values to zero.

Native disassembly spotcheck confirms receiver skip branch at0x828a58, stat payload loads/stores listed in native report, and clock float load at0x82b504/store at0x8bd488. Clock-to-UI rendering remains untraced and report says so; resource14 display label is qualified. Full native reverse engineering was not independently repeated.

No actionable contradictions found within requested scope. Production implementation, exact event frame timings, broader input support, unseen actor truth rows, and repairing M9 remain explicitly outside this result. Report correctly states no production decoder change and avoids claiming overall100% accuracy. Verification script was rerun and rewrote its identical verification artifact as its documented behavior; only review.md was otherwise authored by this reviewer.
