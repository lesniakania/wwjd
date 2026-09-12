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
