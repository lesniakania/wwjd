# Application adjudication findings

The human reviewer completed all eight discussion cases. Original blind judgments, AI judgments,
and the three-dimensional adjudications remain separate and unchanged.

| Dimension | Human adjudications |
| --- | --- |
| Textual faithfulness | 4 faithful, 4 unsupported |
| Situation fit | 1 direct, 1 supporting, 6 off target |
| Harm risk | 8 no identified risk |

These cases were deliberately selected for disagreement and received assistant commentary before
adjudication. Their rates are neither an unbiased estimate of application quality nor evidence of
independent judge agreement. Do not extrapolate them to the 88 applications or overwrite their
original single-label ratings using an implicit conversion rule.

## Operational rubric for the next experiment

- Evaluate textual faithfulness and situation fit separately. A plausible explanation of a passage
  can still miss the user's main concern, as the reviewer judged John 14:27 for doubts about God's presence.
- Assess the entire application, including qualifications. Distinguish the passage's teaching from
  an explicitly marked practical inference. A reasonable recommendation is not automatically what
  the quoted text teaches.
- Main concerns take priority over incidental words: exclusion is not merely anxiety, and spreading
  an unverified claim is not primarily a question of benefit levels.
- Absence of identified harm does not imply relevance or textual faithfulness.
- Keep uncertain judgments and reviewer/assistant disagreements visible; do not force consensus.

## Remaining interpretive disagreement

The reviewer accepted Matthew 18:33's application as faithful and direct. The assistant still
questions the wording that forgiveness should be based on reciprocity between partners: the
passage compares mercy received from the master with mercy owed to a fellow servant. This
reservation is not a change to the human label.

The reviewer accepted the lament application in 2 Samuel 1:23 as faithful but off target, with no
identified harm. The assistant's narrower reservation concerns the additional sentence imposing
an expectation that grief should not continue indefinitely; that claim is not supplied by the
quoted lament. Again, the human judgment is preserved.

These differences show that the automated assessor is not yet a substitute for human review of
fine interpretive claims. A future review should specify whether faithfulness covers every
substantive claim, not just the first sentence or general theme.

## Consequences for the comparison and next experiment

Passage judgments were not changed by application adjudication. The previous result remains:
baseline 31/51 acceptable passages, reranker 12/32 decided passages plus five uncertain; confirmed
case hits 17/20 versus 9/20 (up to 12/20 after resolving uncertainty). This supports baseline within
the reviewed development sample, not a universal conclusion about reranking.

The application quality comparison remains provisional. Do not recompute it by silently mapping
these eight new multidimensional judgments into the older appropriate/problematic labels.

The next isolated generation experiment should hold situations, selected sources, source context,
and model settings fixed. Compare the existing prompt with a variant that removes the mandatory
"This does not mean that..." sentence, distinguishes text meaning from application, and permits
acknowledging weak fit rather than inventing support. Record failures as well as successful output.
Assess each dimension independently on a new anonymized comparison. This prompt experiment has
not been run as part of this adjudication analysis; literary-unit retrieval remains a separate task.
