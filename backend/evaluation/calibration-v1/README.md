# Blind relevance calibration

Start with `review.pl.md` and enter judgments in `human-review.json` only.
Do not read `ai-review.json` or `provenance.json` until the independent review is complete.
Model names and prior target membership are hidden in the human packet, but complete blinding
cannot be guaranteed: reviewers may remember earlier examples or recognize model style.

## Sample

20 development cases: 10 randomly selected prejudice cases, and one random case from each of the
10 other categories. Fixed seed: 20260912. This preserves the original 50/50 allocation but is not
a new held-out dataset. It contains 134 distinct case/passage pairs and 88 distinct applications.
The pool contains original baseline outputs, original reranker outputs, and the approved targets.
Canonical reference equality removes duplicate passages; overlapping ranges remain separate.
Repeated applications are merged only when their passage and exact text match.

## Rubric

Passage `rating`:

- `direct`: addresses the specific concern without inventing circumstances or reversing roles.
- `supporting`: useful secondary support or a defensible analogy; does not directly address the core issue.
- `irrelevant`: only a word/topic match, unsupported analogy, or wrong situation/role.
- `uncertain`: the reviewer cannot reliably decide from the supplied context.

Application `rating`:

- `appropriate`: a defensible application to the situation, without distorting the passage or blaming the harmed person.
- `problematic`: misrepresents the passage, invents important circumstances, reinforces harm, or applies it to the wrong person.
- `uncertain`: requires closer contextual review.

Use `notes` to explain borderline judgments. Leave `null` for unreviewed entries. Uncertain and
unreviewed are different states and must not be counted as irrelevant automatically. A generic
but harmless application is not automatically problematic; consider whether its interpretation
and connection to the situation are defensible. Assess passage relevance independently of the
model's application. The local context is three verses on either side, not a full commentary.

## Provisional AI assessment

`ai-review.json` contains the assistant's judgments made in this conversation. These are not human
approvals, not an independent model experiment, and not a replacement for the approved dataset.
The assistant has seen previous project examples, so its assessment is not fully blind. Its
application notes identify case-level concerns; uncertain cases need human adjudication.
No architecture winner or new quality score is declared before calibration.

After the human review, compare direct versus non-direct agreement and acceptable
(direct + supporting) versus irrelevant agreement, excluding uncertain judgments and explicitly
reporting their count. Compare applications separately. For system quality, report both strict
and inclusive relevance precision and case hit rates, plus problematic-application rates.
Do not call these metrics full recall. Pool-relative recall remains incomplete and sensitive to
the systems included in the pool. Original exact-target metrics remain available separately.

The packet uses corpus quotations so source formatting does not reveal the model. It does not
assess transcription errors in model quotations or the full summary/actions of a response.
The three local-extractive responses in the original reranker run remain part of that run;
this packet evaluates observed output, not a reranker-only causal effect.

Regeneration: from `backend`, run `uv run python scripts/prepare_blind_review.py` only when creating
a fresh packet. The script refuses to overwrite this directory and any human judgments.
