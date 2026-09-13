# Retrieval diagnostic findings

Dataset: 100 approved Polish cases; SHA-256 `bb55f27ad9d58fbbc2478acd5224b82f93145a26880364c56f3d1f397f9b8622`.
The approved dataset was not modified. Additional acceptable passages remain pending human review.

## Full retrieval comparison (100 cases)

These results measure candidates, not generated answers. All four variants use the same corpus,
embedding model, thematic router, and 50-candidate window. Only the reranker setting differs.

| Variant | Hit before reranking (50) | Hit immediately after reranking (6) | Hit sent to generation (up to 6) | Selected recall | Selected verse coverage |
| --- | ---: | ---: | ---: | ---: | ---: |
| disabled | 21.00% | 14.00% | 12.00% | 5.67% | 6.65% |
| raw | 21.00% | 1.00% | 6.00% | 2.00% | 2.62% |
| fused | 21.00% | 9.00% | 9.00% | 3.67% | 4.53% |
| thematic_fused | 21.00% | 13.00% | 9.00% | 3.33% | 4.17% |

Per-case traces: [retrieval experiment reports](runs/diagnostic-retrieval/).

## Repeated generated responses (exploratory subset)

Three sequential runs per configuration on the same 11 deliberately selected cases:
`pl-001, pl-029, pl-053, pl-056, pl-061, pl-066, pl-073, pl-077, pl-083, pl-094, pl-099`.
This is not a random sample or a held-out test set, and its percentages cannot be compared
directly with the earlier 100-case results. Repetitions use real configured Bielik inference.

| Configuration | Hit in each run | Mean precision | Mean recall | Mean MRR | Local responses | HTTP/response errors |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| baseline | 4/11, 4/11, 4/11 | 21.21% | 18.18% | 0.273 | 0 | 0 |
| raw | 2/11, 2/11, 2/11 | 9.09% | 6.06% | 0.091 | 0 | 0 |

[Baseline repetitions](runs/repeats-baseline.json) · [Raw reranker repetitions](runs/repeats-raw.json).

The identical scores across these repetitions do not establish determinism or statistical significance.
Retrieval experiments ran alongside some generation measurements; elapsed times are not a controlled latency comparison.

## What the traces establish

- Before reranking, only 21/100 cases have a complete accepted target in the candidate window.
  Only 30/100 have even one verse belonging to an accepted target. Improving candidate retrieval is essential.
- 48 of the 300 editorial targets span multiple verses, while retrieval currently selects individual verses.
  Strict whole-target matching therefore misses some partial coverage; the new verse coverage metric exposes this gap.
- The raw reranker loses directly relevant candidates. For `pl-001`, Luke 10:27, James 2:1, and
  Leviticus 19:33 are available before reranking but absent from the six selected passages afterwards.
- Theme routing misclassifies `pl-058` (keeping excess change) and `pl-073` (pressure to donate)
  as prejudice. `pl-094` (taking belongings without permission) is routed to fear and generosity.
  This is a separate upstream issue; a thematic reranker query inherits these errors.
- On eight sampled Polish corpus rows, fresh and cached embeddings had cosine similarity at least 0.999999.
  This spot check does not indicate a stale index; it does not validate every index row.
- Offline rescoring of the two original reports reproduced their scores and separately exposed the three
  local fallback responses in the original reranker run. No inference was needed for rescoring.

## Recommended next implementation

Keep the original reranker disabled for the next baseline (`RERANKER_MODEL=''`). The experiments
do not establish a production improvement. Preserve these reports before further changes.
Prioritize recognizing the actual ethical concern and the speaker’s role before selecting passage anchors.
An accusation about a group must not be treated as established misconduct by that group.
Validate routing on separate examples; do not copy this evaluation set into production rules.
Then remeasure candidate coverage and address multi-verse passage selection before changing generation.

Review [the eight alternative proposals](alternative-review.md) independently of the scores.
After approval, create a separately versioned dataset and rescore both old variants against it.
The main `cases.pl.json` still contains exactly three approved proposals per case.

## Reproducibility and validation

The checkout base commit was `0d5e0369ec385dd0536f09e1357c1ff9ddc6d65f` with uncommitted diagnostic changes.
Each diagnostic response records the source fingerprint and allowlisted model/settings metadata.
`SOURCE_COMMIT` was not exported for these runs, so their commit field is `unknown`; the checkout base
is documented here separately rather than retroactively rewriting the reports.
The embedding model was `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`,
the cross-encoder `BAAI/bge-reranker-v2-m3`, and Polish generation
`speakleash/Bielik-11B-v3.0-Instruct` with temperature 0.15.

Validation: 133 backend tests, 20 frontend tests, Ruff, Bandit, ESLint, and frontend build passed.
Backend tests used `LOKY_MAX_CPU_COUNT=2` to avoid sandbox restrictions on physical-core detection.
No production default or approved evaluation target was changed.
