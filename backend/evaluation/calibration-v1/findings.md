# Human calibration findings

The completed human review covers the same 20 development situations: 10 prejudice cases and
one from each other category. Original judgments and provisional AI judgments are preserved.
Computed results: `comparison.json`; reproducible with `scripts/compare_review.py`.

| Measure | Baseline | Reranker |
| --- | ---: | ---: |
| Direct passages / decided passages | 18/51 (35.3%) | 6/32 (18.8%) |
| Direct or supporting / decided passages | 31/51 (60.8%) | 12/32 (37.5%) |
| Uncertain passages | 0 | 5 |
| Cases with a confirmed direct/supporting passage | 17/20 | 9/20 |
| Additional cases whose hit status remains unresolved | 0 | 3 |
| Appropriate applications | 24 | 16 |
| Problematic applications | 15 | 13 |
| Uncertain applications | 12 | 8 |
| Problematic / decided applications | 15/39 (38.5%) | 13/29 (44.8%) |

Precision is micro-averaged over unique case/reference pairs. Uncertain items are excluded from
the decided denominator, not counted as failures. Even if all five uncertain reranker passages
became acceptable, its inclusive precision would be 17/37 (45.9%), below baseline's 60.8% on this
sample. Its case hit rate ranges from 9/20 to 12/20, compared with baseline's 17/20.

This supports baseline over the tested reranker run within this sample. It does not establish
that rerankers generally worsen quality or that these percentages generalize to all 100 cases.
Generation and fallback behavior are included in the observed outputs. No new inference was run.
These are human relevance precision and hit metrics, not full recall.

Application scores remain provisional because the existing rubric merges textual faithfulness,
situational relevance, and harm. The difference between systems on applications should not be
used as a firm quality verdict before adjudication. The shortlist in `adjudication.pl.md` contains
representative issues and new blank fields, without changing the original ratings.

Next: resolve the shortlist, calibrate the application rubric, then test a generation prompt
change on fixed sources. Removing the mandatory qualification sentence is a separate experiment
from passage retrieval and should not be bundled into an architecture comparison.
