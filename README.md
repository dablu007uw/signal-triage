# Signal Triage Digest

A small command-line tool that turns a pile of raw customer and partner signals
into **one grouped digest** I can scan before a Monday partner sync. Built for the
TMMBA 522 "AI Builder for PMs" course (IMPACT framework, Module 4).

## What it does

Every week, customer/partner signals land in three places:

- a shared **Slack** channel with sales,
- keyword-filtered **email** ("feature request", "customer ask", ...),
- the Oracle **PFR tracker** (exported by hand to a spreadsheet).

Reading all three by hand is slow, and the real risk is **missing a blocker** that
then blows up in the Monday sync. This tool reads those exports (as `.csv` files
dropped in one folder) and produces a Markdown digest that:

1. **Checks coverage** — counts rows per source and shouts if one came back
   **empty** (so a forgotten PFR export can't silently cost me a signal).
2. **Puts uncertain signals FIRST** — anything the tool isn't confident about goes
   in a `⚠️ REVIEW FIRST — not sure, you look` section at the top. It never hides
   what it's unsure of, because a **miss** is my expensive error.
3. **Groups the confident signals** by product area (Observability, DR, Networking,
   Database, Partner/Ops).

It deliberately does **not** prioritize or rank. I keep urgency, escalation, and
ownership — the tool only retrieves, groups, and flags.

## How to run it

You need Python 3 (no other installs — it's all standard library).

1. Put your exports as `.csv` files in a folder (e.g. `sample_data/`). Any columns
   work; the tool looks for a text/message/summary/body column and falls back to
   reading the whole row.
2. From this folder, run:

   ```
   python triage.py --input sample_data --output digest.md --expect slack,email,pfr
   ```

   - `--input`  folder holding your `.csv` exports
   - `--output` where to write the digest (Markdown)
   - `--expect` the source names you EXPECT this run, so the tool can warn if one is missing

3. Open `digest.md`. Read the REVIEW section first, then the grouped signals.

Run it with the included `sample_data/` to see it work end to end.

## Why it's built this way (the product decisions)

- **Wide / high-recall filter.** It over-pulls on purpose. Extra noise costs me a
  few minutes of skimming; a dropped blocker costs real ARR. When in doubt, the
  signal goes to REVIEW, never to the trash.
- **Safety net runs toward me.** Low-confidence items are surfaced with *more*
  attention, not deprioritized — the opposite of a tool whose expensive error is a
  false positive.
- **Human keeps the judgment calls.** No auto-prioritization by design.

To tune what it catches, edit the keyword lists at the top of `triage.py`.

## Files

- `triage.py` — the tool
- `sample_data/` — example Slack / email / PFR exports to try it on
- `digest.md` — example output (generated)
