# IMPACT Living Document — Module 4 (A + C)

_Signal Triage Digest. Organized from my own interview answers. Gaps I have not answered yet are marked **⚠ NEEDS ME** rather than filled in._

---

## Section 4 — Failure Mode Map (Accuracy & Safety)

**Core question: what does the product do when the AI is wrong?**

| # | Failure mode (how it hurts me) | Cost | Product-level response (the safety net) |
|---|---|---|---|
| FM1 | **A miss (false negative).** A real customer signal exists — e.g. a partner flags an Observability gap — but the tool doesn't pull it into the digest. I walk into Monday's sync blind. | **High — ARR risk.** This is my load-bearing error from Intent. | The tool surfaces low-confidence signals in a **`⚠️ REVIEW FIRST — you look`** section at the **top** of the digest, never hidden or held back. When it's unsure, the signal gets *more* of my attention, not less. |
| FM2 | **Noise (false positive).** The tool pulls something into the digest that isn't a real signal (a stray Slack message, a keyword-matched newsletter). | **Low — a few minutes of skimming.** Accepted on purpose (see Tradeoffs). | Kept, not fought. Noise lands in REVIEW where I skim and dismiss it. My filter is deliberately wide/high-recall, so I'd rather read a false positive than miss FM1. |
| FM3 | **A source silently comes back empty** — e.g. I forget the manual Oracle PFR export, so an entire channel of signals is missing. | **High — a hidden version of FM1.** | The digest opens with a **Coverage check** that counts rows per source and flags any expected source with **0 rows** ("⚠️ EMPTY — did this export run?"). |

**Note to self (the thing this module grades):** my first instinct was to *hold back* low-confidence items for a later run. That was wrong — it hides exactly the blocker I'm most afraid of missing. Because my expensive error is a **miss**, the safety net has to run **toward** me (surface), not away (suppress). FM1's response is built that way.

**⚠ NEEDS ME (not yet interviewed):** a fourth candidate failure mode is **mis-grouping** — a real signal gets filed under the wrong product area and I skim past it. Decide whether that's worth its own safety net or is covered by "it's still in the digest, just in the wrong bucket."

---

## Section 5 — Tradeoffs Table (Cost & Constraints)

**Core question: what am I giving up to ship this, and what did I cut?**

| Tradeoff | My decision | Why |
|---|---|---|
| **Recall vs. precision** (the one I made) | Tune **wide / high-recall**. Accept more false positives to avoid a single false negative. | A false positive costs minutes; a missed blocker costs ARR. The cost of being wrong is asymmetric, so I buy recall with precision. |
| **Autonomy** | Tool **retrieves, groups, and flags only.** No auto-prioritization. | Keeps Module 2's boundary intact — I retain urgency, escalation, and ownership. Raising autonomy here would need accuracy I don't have in v1. |
| **Latency** | ⚠ NEEDS ME | How fresh does the digest need to be? (It's a manual file-drop, run Friday PM — is "runs in seconds when I trigger it" the whole budget, or do I need it faster / scheduled?) |
| **Dollar cost** | ⚠ NEEDS ME | v1 is plain keyword matching = ~free. Name the tradeoff if/when I swap in an LLM for grouping (better clustering vs. per-run cost). |
| **What I cut from v1** | ⚠ NEEDS ME | Candidates already visible: direct Oracle/n8n integration (hard constraint), Salesforce as a 4th source (raised, out of scope), and LLM-based semantic grouping. Confirm the cut list. |

**One tradeoff I can name and defend right now:** recall over precision — I accept noise to protect against a miss, because the cost of being wrong is asymmetric.

---

### Honest read
Strong: FM1 and its safety net are clear, defensible, and actually built into the tool; the recall-vs-precision tradeoff is solid. Thin: the Cost letter is half-done — latency, dollar cost, and the v1 cut list are still **⚠ NEEDS ME**. Ten minutes on those three closes Section 5.
