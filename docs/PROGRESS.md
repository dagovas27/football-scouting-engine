# Progress log

## 2026-11-18 — Phase 0 — Data inspection and scope definition
**Branch:** `docs/phase0-data-inspection` · **PR:** [#1](https://github.com/dagovas27/football-scouting-engine/pull/1) (merged)
**Done:**
- Read-only inspection of `~/Documents/data-sc/` (Wyscout, Transfermarkt, StatsBomb) answering the 10
  Phase 0 questions with numbers: `docs/data-inspection/phase0-report.md`.
- `docs/data-sources.md` (files, sizes, versions, licenses, citations) and `docs/scope.md` (hypotheses,
  module support, decisions).
- Inspection scripts kept outside the repository by request (not versioned).
**Decisions:** scope and D1–D9 approved on 2026-11-18 — [ADR-0001](decisions/ADR-0001-phase0-data-scope.md).
**Data/quality findings:**
- H1–H6 confirmed, H7 partially confirmed (WC 2018 needed only for the StatsBomb benchmark).
- Derived minutes match PlayeRank 99.0%; Brighton 2017/18 table passes sanity checks.
- Linking 90.8% (DOB + surname) / 96.6% (+ name tokens); Dale Stephens is the only unlinked Brighton player.
- Valuation coverage 99.9% / 97.0% / 90.6% at 2018 / 2020 / 2022.
- 1,152 Wyscout player names are double-escaped; `referees.json` is truncated.
- No salary or contract history (contract risk uses user inputs and pooled calibration).
**Blockers / open questions:** none (PR merged; manual updated locally with the confirmed scope).
**Next session starts with:** applying the approved scope to CLAUDE.md, then S1 infrastructure.
**Status:** done
