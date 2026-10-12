# CLAUDE.md — working rules for this repository

## What this repo is

USRT (Unified Substrate Reality Theory) is a speculative "space is a medium" research programme. It has four parts:

- **The original material:** `UNIFIED_SUBSTRATE_REALITY_THEORY_TREATISE.md`, `RESEARCH_PREPRINT_USRT.md` and 45 simulation scripts (moved to `archive/usrt_legacy/` on 2026-10-12).
- **`audit/`:** the independent verification of the original claims. Start with `audit/USRT_AUDIT_REPORT.md`. Run it with `python3 audit/run_all.py` and regenerate its figures with `python3 audit/make_figures.py`.
- **`research/`:** all new exploration after the audit. Each question becomes a script `rNN_topic.py`. Its output goes to `research/results/` and its plots to `research/figures/`. The running record is **`research/LAB_NOTEBOOK.md`**. Read the notebook first to see what has already been done and what is queued.
- **`README.md`:** the public overview and gallery.

## The persistence rule (requested by the repo owner): nothing gets lost

Every calculation, plot, formulation, simulation, experiment and substantive line of reasoning done in a session must be saved in the repo **and pushed before the turn ends**. Concretely:

1. **Code:** put the calculation in `research/rNN_<topic>.py`, numbered after the last existing script. Do not leave it in a scratch directory. Use `research/lab.py`:
   - `Report` prints the results and saves them to `research/results/rNN_<topic>.txt`;
   - `save_fig` writes PNGs to `research/figures/`;
   - `style` applies the chart conventions.
2. **Notebook:** append a dated entry to `research/LAB_NOTEBOOK.md` and add its row to the index table. Each entry has:
   - the question, in the user's words;
   - the method;
   - the results, with numbers;
   - the interpretation;
   - a status (established / computed here / open / ruled out);
   - references;
   - links to the files.

   Update the E9 synthesis and its "Next steps" queue when the picture changes.
3. **Never rewrite history:** append. A correction is a new dated note under the entry it corrects. Do not overwrite old conclusions silently.
4. **Pure reasoning counts too.** A conceptual discussion with no code still gets a notebook entry: the argument, the conclusion and the references.
5. **Commit and push to the working branch at the end of every turn that changed anything.** A Stop hook (`.claude/hooks/require_saved_work.py`) blocks finishing while there are uncommitted or unpushed changes.
6. **README:** if a new result is a highlight, add it to the "Research log" section of `README.md`.

## Scientific honesty rules (carried over from the audit)

- **Compare with real measurements and their uncertainties** (CODATA 2022, PDG 2024, Planck 2018 values live in `audit/common.py`). Report σ, not "% accuracy".
- **Never tune a constant to hit a target.** If a fit is used, say so and count how many forms were tried (look-elsewhere effect).
- **Separate inputs from outputs.** Label identities, things typed in by hand, and illustrative curves as such.
- **Credit prior art.** Volovik, Levin–Wen, Nottale, Koide, Brannen, Lenz, Page–Wootters, Bohm and others are cited in the notebook and the report.
- **Look at every figure after generating it.** Check for overlaps and for titles that claim more than the data show.

## Chart conventions

- **Palette:** use `research/lab.py` colours (blue `#2a78d6`, orange `#eb6834`, aqua `#1baf7a`) with at most three series per chart. Colour follows the entity across panels. Reference lines are muted grey dashes.
- **Annotations:** direct labels must not sit on data. A title states what the plot shows, not a verdict it doesn't support.
