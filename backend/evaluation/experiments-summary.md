# Experiment summary

Status: 2026-09-13. The original 100-case dataset remains unchanged. It is now a development set,
not an independent final test. Unless stated otherwise, metrics measure agreement with its three
approved references per case, not overall answer quality.

## Completed experiments

| Experiment | Result | Conclusion |
| --- | --- | --- |
| Original baseline vs raw reranker, 100 generated responses | Final recall: 4.0% → 2.0%; case hit rate: 9% → 6%. Reranker run included 3 generation fallbacks. | Reranker reduced reference agreement; human review was needed to judge alternative verses. |
| Retrieval-only reranker variants, 100 cases | Selected recall: disabled 5.7%, raw 2.0%, fused 3.7%, thematic fused 3.3%. | No tested reranker improved retrieval. Subsequent experiments disabled it. |
| Local routing changes + short-anchor completion, 100 responses | Final recall 4.7%; hit rate 13%. | Small improvement over the original baseline. |
| Additional Bielik situation analysis, 100 responses | Final recall 17.3%; hit rate 42%. Candidate recall@50 26.3%. Analysis: 99 successes, 1 fallback; mean added analysis time ~3.35 s. | Largest observed gain, but recall remains low and role recognition is fallible. Feature remains opt-in. |
| Selection rules, frozen candidates from 100 cases | Selected recall: alphabetical theme order 23.0%, theme priority 24.3%; no per-book limit 16.3%. | Small ordering gain; removing book diversity worsened results. No production selection change. |
| Context embeddings, frozen queries from 100 cases | Candidate recall@50: verse-only semantic 8.7%, same ranking with expanded quotations 12.0%, context embeddings 14.3%; existing hybrid 26.3%, hybrid + context 28.0%. | Neighboring verses help slightly; not a replacement for current retrieval. These are mechanical windows, not literary units. |
| Human blind calibration, 20 cases | Acceptable passage precision: baseline 31/51 (60.8%), reranker 12/32 decided (37.5%), with 5 uncertain. Confirmed case hits: 17/20 vs 9/20 (up to 12/20). | Baseline also wins under broader human relevance judgments in this sample. These are precision/hit metrics, not full recall. |
| Application adjudication, 8 selected disagreements | Human judgments: 4 unsupported by text; 6 off target; no identified harm in all 8. | Score textual faithfulness, situation fit, and harm separately. Selected discussion cases do not estimate overall error rates. |

Repeated generation checks used 11 exploratory cases, three runs per variant: original baseline
hit 4/11 each time, raw reranker 2/11, revised Bielik-analysis variant 6/11. These repetitions do
not establish determinism or generalization. Some experiments ran concurrently; latency comparisons
were not controlled. Do not compare candidate, selected-passage, and final-response recall as if
they measured the same output.

## Original plan: current status

1. **Reranker:** implemented and tested; no improvement demonstrated for the tested configurations.
2. **Literary-unit retrieval with verse-level precision:** **not implemented**. The context-window
   experiment does not fulfill this step. Retrieval using meaning descriptions is also untested.
3. **Dense + lexical → RRF:** already present in the base retriever, alongside thematic anchor
   bonuses. Their individual contributions have not yet been fully isolated.

## Next steps

- Review the completed fixed-source application prompt comparison described below before choosing
  a production prompt.
- Then return to actual literary-unit retrieval and measure both unit coverage and precise verse
  selection. Revisit reranking after candidate quality improves.
- Preserve exact-reference metrics, add calibrated human relevance/application metrics, and prepare
  fresh held-out situations. The automated assessor is not yet a validated replacement for review.

## Detailed records

- [Initial diagnostics](diagnostic-findings.md)
- [Bielik analysis](situation-analysis-findings.md)
- [Selection ablation](selection-findings.md)
- [Context representations](passage-findings.md)
- [Human calibration](calibration-v1/findings.md)
- [Application adjudication](calibration-v1/adjudication-findings.md)

No production deployment was performed. Latest implementation checks: 154 backend tests,
20 frontend tests, Ruff, Bandit, ESLint, and frontend build passed.

## Update: fixed-source prompt comparison completed

The previously pending application experiment has now run: 32 Bielik calls on eight adjudicated
cases (two variants × two repetitions), producing 16 distinct normalized applications. Both
variants were accepted by the production parser in every request. The candidate avoids mandatory
qualifications, but still makes some strained connections; human quality comparison is pending.
Production is unchanged. See [prompt experiment](application-prompts-v1/findings.md) and
[anonymous review](application-prompts-v1/review.pl.md).
