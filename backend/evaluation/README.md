# Verse selection evaluation

100 original, synthetic Polish situations: 50 about prejudice and 50 about other
concerns. Each includes three proposed passages with rationales. The dataset is not
used by production retrieval or response generation.

## Review

Read `review.pl.md` for full quotations from the local UBG corpus. Edit `cases.pl.json`:
change or add `expected_sources`, record comments in `review_notes`, and set
`reviewed: true` after reviewing the case. References may use Polish or canonical
English book names. Ranges use the format `Luke 10:25-28` within a single chapter.
The list represents acceptable selections; a response does not need to include every
passage. Do not add overlapping variants of the same passage as separate targets.

Check whether each passage addresses the specific concern, whether its application
respects the context, and whether the response avoids justifying prejudice, blaming
the person being harmed, or pressuring someone into reconciliation or intimacy.
Consider adding more direct alternatives to general passages. AI-generated proposals
require your judgment.

Regenerate the review document from the `backend` directory:

```bash
uv run python scripts/evaluation_review.py
```

## Running and comparing evaluations

Start the backend with the configuration you want to evaluate. The script sends one
`POST /api/reflections` request per case, sequentially, without retrying failures.
If the backend uses an external model, the evaluation also calls that model and may
consume paid usage. The default address is `http://localhost:8000`.

From the `backend` directory, evaluate the first configuration:

```bash
uv run python scripts/evaluate.py --label architecture-a --output evaluation/runs/a.json
```

After changing the architecture and restarting the backend:

```bash
uv run python scripts/evaluate.py --label architecture-b --baseline evaluation/runs/a.json --output evaluation/runs/b.json
```

Options include `--url`, `--timeout` (seconds per request, default: 180), `--limit 5`
for a trial run, and `--reviewed-only` to evaluate only approved cases. Drafts are
included by default, and the report records their count. Reports can only be compared
when the dataset file and selected case IDs are identical. After editing the dataset,
create a new baseline. An HTTP error, invalid JSON, missing sources, or an unsupported
reference results in a score of zero; the report is still saved, and the script exits
with code 1. Do not overwrite the baseline file.

## Interpreting results

Scores range from 0 to 1; higher is better:

- `hit`: proportion of situations with at least one matching passage.
- `precision`: average proportion of returned sources that match the editorial
  targets. Repeating the same target earns no additional credit. This measures
  agreement with the editorial list, not objective theological quality: a relevant
  verse that is absent from the list receives no credit.
- `recall`: average proportion of proposed passages found. This is a supporting
  coverage metric; a good response does not need to include every alternative.
- `mrr`: mean reciprocal rank of the first match; no match scores zero.

Consider `precision`, `hit`, the error count, and individual responses together.
Results are also grouped by category; half the dataset deliberately concerns prejudice.
A match requires the returned range to contain the entire expected passage. A neighboring
verse is insufficient. A longer range containing the target is accepted; the relevance
of the rest of that range requires human review.

The JSON report preserves full responses, errors, request durations, the configuration
identifier (`--label`), the dataset's SHA-256 hash, averages, and differences from the
baseline. Record the commit, models, and key settings in the label; the report does not
read the server configuration. `generated_with` is preserved inside each API response.

The automated evaluation does not assess quotation accuracy, the meaning of the
commentary, tone, or the safety of suggested actions. Review those aspects in the saved
`response`; the metrics only assess reference selection. With stochastic generation,
run each configuration several times. Do not treat a single small increase as conclusive
evidence of improvement. If you tune the architecture using these examples, reserve a
separate dataset that is not used during tuning for the final evaluation.

## Retrieval diagnostics and controlled experiments

Opt-in diagnostics capture the same search used to generate the response. Enable them
on the server with `EVALUATION_DIAGNOSTICS=true`, then restart it and pass
`--diagnostics` to the benchmark. Requests for diagnostics return HTTP 403 when the
server option is disabled. Ordinary requests do not collect candidate traces.

Alternatively, run the actual application in-process with `--local`; this enables
requested diagnostics for that process and does not require a running HTTP server:

```bash
RERANKER_MODEL='' uv run python scripts/evaluate.py --local --diagnostics --reviewed-only --label baseline-diagnostic --output evaluation/runs/baseline-diagnostic.json
```

`--local` uses the configured inference provider. It is not an offline simulation.
Provider timeouts still apply; `--timeout` controls HTTP mode and does not impose an
end-to-end deadline on in-process ASGI calls.

Each response includes request-local `diagnostics.searches` with the initial query,
detected themes, reranker query, candidates before and after reranking, and the final
retrieval selection. A fallback query gets a separate trace. Candidate scores named
`retrieval_score` and `confidence` belong to the original retriever, not the cross-encoder.
The before/after lists cover `RERANKER_CANDIDATES` passages (default: 50).

Reports aggregate these stages:

- `initial_before_rerank`: candidate window for the original user query.
- `before_rerank`: candidate window for the search actually used (possibly fallback).
- `after_rerank_top6`: first six candidates immediately after reranking.
- `selected`: passages after confidence, diversity, and theme filters; sent to generation.
- `final`: passages selected by generation.

`verse_coverage` measures coverage of individual expected verses, including their union
across separate returned sources. It helps diagnose multi-verse targets when retrieval
only returns individual verses. Existing `hit` and `recall` still require one source to
contain the complete target. Do not substitute coverage for a human assessment of context.

The report includes allowlisted model/settings metadata, a Python source fingerprint,
and `SOURCE_COMMIT` (or `RENDER_GIT_COMMIT`, otherwise `unknown`). Set the commit variable
when launching the server or local runner. Tokens and database URLs are not included.
`local_extractive` counts local responses separately from request errors. With remote
inference enabled, these indicate fallback responses; with inference disabled, they are
the expected generation mode. Inspect `configuration_consistent` before comparing runs.

For retrieval-only comparisons using cached models and no generation calls:

```bash
uv run python scripts/evaluate_retrieval.py --output-dir evaluation/runs/retrieval-experiment
```

This compares reranking disabled, `raw` (the existing default), `fused` (equal-weight
reciprocal-rank fusion of initial and cross-encoder ranks, constant 50), and
`thematic_fused` (the same fusion with a Polish task/concern description added to the
query). The thematic variant is a Polish evaluation experiment. It is not validated for
English. Production defaults remain unchanged. Select a variant explicitly with
`RERANKER_STRATEGY=raw`, `fused`, or `thematic_fused`; disable the model with `RERANKER_MODEL=''`.
Retrieval-only reports have `kind: retrieval-only`; their selection metrics describe
up to six candidates, not generated responses. They are not full benchmark baselines.

## Repeated runs and offline rescoring

Use `--repeat 3` to save three individual reports and a separate aggregate containing
means, sample standard deviations, and all individual scores:

```bash
uv run python scripts/evaluate.py --local --diagnostics --reviewed-only --repeat 3 --label repeated --output evaluation/runs/repeated.json
```

This creates `repeated-1.json` through `repeated-3.json`; `repeated.json` contains the
aggregate. Use an individual report, not the aggregate, with `--baseline`. Existing
files are never overwritten. `--case-ids pl-001,pl-053,pl-083` selects a fixed subset;
use exactly the same selection across variants and report subset results as exploratory.
Repetitions run sequentially and reuse loaded local models.

After human approval of additional references, rescore saved responses without calling
any model. Use a separately versioned dataset with the accepted additions:

```bash
uv run python scripts/evaluate.py --rescore evaluation/runs/baseline.json --dataset evaluation/cases.revised.pl.json --label baseline-rescored --output evaluation/runs/baseline-rescored.json
```

Rescoring requires identical case IDs and situation texts. It preserves responses,
records the previous dataset hash, recomputes metrics, and removes obsolete comparisons.
Rescore both variants against the same revised dataset before comparing them.
`alternative-proposals.json` and `alternative-review.md` are pending editorial proposals,
not additional production retrieval rules or automatically accepted evaluation targets.

## Optional situation analysis before retrieval

`SITUATION_ANALYSIS=true` enables a separate structured model call before retrieval.
It uses the existing Polish model (`HF_MODEL_PL`) or English model (`HF_MODEL`) and
inference provider. This adds latency and provider usage; it is disabled by default.
`ANALYSIS_TIMEOUT_SECONDS` defaults to 20. There is one analysis attempt, with no retry.

The model returns the speaker's role, a description of the concern, up to three IDs
from the existing theme catalog, and a search query describing useful principles or
comfort. It receives no evaluation targets and cannot add verses to the corpus.
Successful analysis replaces literal keyword routing for that search, so allegations
about other people need not be treated as established wrongdoing. Assigned theme
weights (0.95, 0.90, 0.85) are ranking priors by order, not calibrated model confidence.
The role and problem description are recorded for review; retrieval uses the query and
theme IDs. The original situation still drives safety detection and final generation.

Schema, provider, and timeout failures fall back to the ordinary retrieval path.
Diagnostics record the profile, elapsed analysis time, and error type without provider
response text or credentials. `analysis_successes` and `analysis_fallbacks` in the report
are separate from generation fallback counts. A schema-valid analysis can still be
semantically wrong; inspect the profiles rather than treating success as correctness.

Compare the additional model call against the same local retrieval changes:

```bash
SITUATION_ANALYSIS=false RERANKER_MODEL='' uv run python scripts/evaluate.py --local --diagnostics --reviewed-only --label local-routing --output evaluation/runs/local-routing.json
SITUATION_ANALYSIS=true RERANKER_MODEL='' uv run python scripts/evaluate.py --local --diagnostics --reviewed-only --label analyzed-routing --baseline evaluation/runs/local-routing.json --output evaluation/runs/analyzed-routing.json
```

The local router now abstains when its two leading eligible themes differ in cosine
similarity by less than 0.05. Selected verses belonging to existing thematic anchor
ranges of at most four verses are returned as those complete ranges. Longer anchors
remain individual verses. This uses the production anchor catalog, not evaluation
answers, and does not automatically attach arbitrary neighboring verses. Range
completion happens after ranking, so complete-target coverage can increase between
the candidate-window and selected stages.

### Replay selection on saved candidates

To isolate selection from changes in model-generated queries, use an existing diagnostic report:

```bash
uv run python scripts/evaluate_selection.py evaluation/runs/intent-analysis-v2-full.json \
  --output evaluation/runs/selection-ablation-new.json
```

This makes no network or model calls. It compares one, two, and unrestricted passages per book,
with ranking order, theme priority, and alphabetical theme order. All variants use the same saved
candidate pools, short-anchor expansion, confidence threshold, and overlap deduplication.
Results measure the six passages selected for generation, not final answers. Saved traces contain
only the configured top candidates, and production uses a different adjacent-start deduplication
rule, so this is a controlled ablation rather than a complete production replay. Existing output
files are never overwritten.

### Compare verse and context representations

```bash
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 uv run python scripts/evaluate_passages.py \
  evaluation/runs/intent-analysis-v2-full.json \
  --output evaluation/runs/passage-representations-new.json
```

This experiment uses the existing embedding model and the saved first retrieval query for each
case, including any analysis fallback. It builds embeddings for each verse with its previous and
next verse within the same chapter. This captures local textual context; it does not generate
interpretations or encode reviewed evaluation answers. The first run builds an index for the
whole corpus; later runs reuse a cache keyed by model and complete input texts. The existing
single-verse embedding cache is required, and the model must match the diagnostic report.

It compares 50 candidates from:

- Single-verse semantic embeddings, without thematic anchors or lexical scoring.
- The same ranking with neighboring verses included in returned ranges (expansion control).
- Semantic embeddings computed from the neighboring verses together.
- Equal reciprocal-rank fusion of the existing saved candidates and context candidates.

The expansion control is necessary: a longer returned range can match more targets without
improving ranking. Exact duplicate ranges are removed; overlapping ranges remain candidates.
The index uses fixed local windows rather than editorial passage boundaries. Metrics describe
candidate coverage before selection/generation, not final answer quality. Production retrieval
is unchanged by this experiment.
