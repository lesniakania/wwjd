# Selection ablation

Input: `runs/intent-analysis-v2-full.json`, 100 reviewed cases. No new model calls and no gold changes.
Results: `runs/selection-ablation-with-control.json`.

| Ordering | Per-book limit | Selected recall | Case hit rate |
| --- | ---: | ---: | ---: |
| Alphabetical themes (control) | 1 | 23.0% | 53% |
| Model theme priority | 1 | 24.3% | 54% |
| Retrieval ranking | 1 | 24.0% | 54% |
| Retrieval ranking | 2 | 20.7% | 46% |
| Retrieval ranking | Unrestricted | 16.3% | 41% |

The control matches the recorded production selected-stage aggregate (23% recall, 53% hit).
This does not prove identical per-case selections: the replay uses only saved candidates and
replaces adjacent-start deduplication with overlap deduplication. All replay variants share these
conditions. Each selects at most six passages; these are not final-response scores.

Removing the per-book limit is counterproductive on this pool. Favoring the model's theme order
recovers four additional editorial targets across 300, a modest gain that does not address the
main recall deficit. No production selection behavior has been changed on this evidence.

The next substantial experiment should change candidate retrieval representations, using passage
meaning/context and measuring coverage before generation. Further tuning of selection alone is
unlikely to recover targets absent from the initial pool. Any such experiment must keep the
reviewed target list out of the production retrieval configuration.
