# Fixed-source application prompt experiment

32 real Bielik calls: eight adjudicated situations, two prompt variants, two repetitions each.
Both variants receive identical sources and saved context cards, with temperature 0.15 and the same
output-token limit. Request order was shuffled with seed 20260913. There was no retrieval, retry,
or fallback. Production prompts and settings were not modified.

The control uses the current production system prompt, but the shared user prompt forces exactly
one frozen source. The candidate removes the mandatory qualification sentence and adds instructions
to preserve textual meaning, mark analogies, address the main concern, and acknowledge weak fit.
This tests that instruction bundle, not the causal effect of removing one sentence alone.

## Execution

- Both variants produced 16/16 outputs accepted by the existing production parser.
- All 16 control responses used a list of sentences instead of the required string. The runner
  records these as strict-format errors; production normalizes the lists successfully. They are
  not HTTP failures or automatic evidence of poor relevance.
- The candidate had no strict-format errors.
- Each case/variant repeated the same normalized application twice: 16 distinct applications.
  This does not establish general determinism.
- Raw responses, exact prompt payloads, timing, and input hash are in
  `../runs/application-prompts-v1/report.json`; no credentials are stored.

## Preliminary assistant observations (not calibrated scores)

The new prompt sometimes describes limits more clearly, notably that a cultic payment rule does
not directly address modern benefits. It removes the control's awkward grief qualification and
its mistaken description of 2 Samuel as a psalm. However, it still connects anxiety teaching to
exclusion of a child, and stretches the Nehemiah narrative into advice about suspicions. A more
natural sentence is not proof of a faithful or relevant application.

No winner is declared and no production change is made. The human comparison is in `review.pl.md`
and `human-review.json`; provenance is separate. Exact repetitions were merged to reduce review
work. Style may reveal a variant, so blinding is imperfect. These eight deliberately selected,
previously discussed cases are a development check, not an independent quality estimate.

Judge all substantive claims, including added qualifications, in three separate dimensions:
textual faithfulness, situation fit, and harm risk. Acknowledging weak fit can be faithful without
being a directly helpful answer. Original calibration/adjudication labels remain unchanged.
