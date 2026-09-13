# Contextual passage retrieval experiment

## Scope

All 100 approved cases, frozen queries from the Bielik-analysis report, 50 candidates per variant. No new generation calls, no changes to the editorial dataset or production retrieval. The experiment encodes each verse together with its immediate neighbors within the chapter using the same multilingual MiniLM model. It measures local textual context, not generated theological interpretations.

## Results

| Representation | Target recall@50 | Cases with a target |
| --- | ---: | ---: |
| Existing hybrid candidates | 26.3% | 57% |
| verse_embeddings | 8.7% | 26% |
| verse_embeddings_expanded | 12.0% | 33% |
| context_embeddings | 14.3% | 35% |
| existing_plus_context | 28.0% | 62% |

The expansion-only control scores 12.0%, compared with 14.3% for context embeddings. Thus the gain over verse embeddings is partly due to longer output ranges (8.7% to 12.0%) and partly to changed representations/ranking (12.0% to 14.3%). Neither semantic-only variant beats existing hybrid retrieval. Combining existing and context candidates raises recall by 1.7 percentage points, from 79 to 84 of 300 targets. These are candidate metrics, not final answer metrics.

The combined variant improves target recall in 10 cases and regresses in 6. It recovers candidates for pressure to donate (pl-073), fear of layoffs (pl-076), and disclosure of a private story (pl-092), but loses the target candidate for reading a partner’s messages without consent (pl-091).

## Weak categories: combined variant

| Category | Original candidate recall | Combined candidate recall |
| --- | ---: | ---: |
| granice_i_szacunek | 13.3% | 20.0% |
| lek_i_niepewnosc | 13.3% | 20.0% |
| skrucha_i_odpowiedzialnosc | 0.0% | 0.0% |

## Decision and limitations

Do not replace production retrieval with this context index: the isolated variant is worse, and the combined gain is small and uneven. Local context alone is insufficient. The next representation experiment would need explicit, independently prepared descriptions of passage meaning/application or a better suited semantic model, assessed on fresh cases as well as this development set. That work is not implemented here.

- Three-verse windows are mechanical boundaries. They can omit longer arguments and include unrelated neighboring material.
- Exact duplicate references are removed; overlapping ranges remain separate candidates. More text per candidate is why the expansion control is essential.
- Equal reciprocal-rank fusion treats different reference ranges separately, even if they overlap; this is a simple exploratory combination, not a tuned production ranking.
- Existing hybrid retrieval includes lexical scoring and thematic priors, whereas the isolated semantic variants do not. Only the verse/expanded/context comparison isolates representation changes.
- The existing single-verse cache is reused; the context cache is keyed by model and all input texts. The verified rerun used the cache and reproduced all per-case results.
- Results use the existing development dataset, not an unseen test set. They do not establish improved final response quality.

## Artifacts and validation

- Script: `backend/scripts/evaluate_passages.py` (see README for invocation).
- Verified report: `runs/passage-representations-verified.json`.
- 148 backend tests, 20 frontend tests, Ruff, Bandit, ESLint, and frontend build passed.
- The approved dataset remained unchanged. No deployment performed.
