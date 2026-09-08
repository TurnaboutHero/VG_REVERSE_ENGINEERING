# Event semantics implementation and verification plan

Base:76977986e0287850bcc5e000f05a9f2d7429e60b. Branch:codex/event-semantics-20260906.

The user requested tracing event meaning to completion with available evidence, treating VGNA as fallible. Existing remote data and six pre-existing dirty documents must remain intact.

- [x] Add a strict, lossless event timeline with numeric section order, owning timestamps, complete payloads, and safe output paths; independent packed fixtures and actual M1 CLI validation.
- [x] Trace four native event families through pinned C exports, matching official engine constructors, vtables, serializers and handlers; document exact engine hash and limits.
- [x] Repair established structural extraction errors in legacy KDA while preserving import compatibility and existing counting policies. Validate full56replay before/after outputs.
- [x] Trace named native KDA getters and expose verified meanings in the timeline without final-score aggregation. Preserve SET/ADD, all layers, rawflags, offsets and evidence identity.
- [x] Compare screenshot-backed truth and inspect available local video candidates; record unmatched/missing video evidence separately.

Acceptance evidence: task reviews and scoped fixes, a final whole-branch review, the full unittest suite, actual CLI happy/error/help paths, and recorded corpus comparisons. The execution ledger binds each result to its exact commit. Reports include both established meanings and unresolved evidence; no aggregate count is silently promoted to final-score truth.

Rulings: keep the in-place remote corpus on a feature branch (a later isolated checkout requires data paths); treat external names and outputs as hypotheses until direct handler/getter evidence closes the link (unverified fields remain unknown); retain legacy aggregate policies for comparison while delivering a native interpretation layer (final-score policy still requires initial state/completeness/endgame validation).

Residual research: resource9/10 and other enum names, physical death/respawn video alignment, replay-producer build equivalence, initial state/clamping bounds, reliable final-score cutoff, and minion-count discrepancies. None is filled by guessing or by fitting existing totals. No push/merge/deployment is part of this plan.
