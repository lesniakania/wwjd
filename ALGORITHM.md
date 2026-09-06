# Main application flow

The app turns a user's situation into a cautious, Bible-grounded reflection. It uses the Updated Gdansk Bible (UBG) for Polish and the World English Bible (WEB) for English. Scripture and its displayed context always come from these local, language-specific corpora; the language model may only compose the reflection from passages supplied by the backend.

```text
Situation + language
        |
        v
Validate and normalize input
        |
        +--> detect urgent safety terms --> attach support message
        |
        v
Classify ethical themes
        |
        v
Retrieve and rank local Bible verses
        |
        v
Load reviewed context for each candidate
        |
        v
Generate and validate a reflection
        |
        v
Return summary, actions, 1-3 sourced passages, and limitations
```

## Reflection algorithm

### Accept input

The Vue client sends the situation and selected language (`pl` or `en`) to `POST /api/reflections`. FastAPI collapses whitespace and enforces the configured length limits.

### Check safety

Urgent self-harm, violence, or abuse phrases add an immediate support message. This does not stop retrieval, but makes safety guidance prominent in the result.

### Detect themes

Theme detection has two stages. First, predefined Polish and English keyword and phrase patterns match themes from the 21-theme catalog, including forgiveness, conflict, fear, honesty, boundaries and consent, dignity, stewardship, and others. Second, semantic routing uses the multilingual `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` model through ONNX Runtime to compare the overall meaning of the situation with predefined theme profiles. If the text strongly implies a theme that the keyword patterns missed, semantic routing can add that one theme. For example, repeatedly comparing yourself with a colleague may indicate envy even if the user never writes the word "envy." Without semantic routing, theme detection relies only on the keyword and phrase patterns; passage retrieval still uses lexical relevance and the Bible anchors associated with the themes they detect. [`backend/app/themes.py`](backend/app/themes.py) contains the 21 production theme identifiers, bilingual lexical rules, and manually written semantic text in `THEME_PROFILES`.

The theme catalog was created based on the MIT-licensed [**ETHICS commonsense dataset**](https://github.com/hendrycks/ethics) through an offline editorial workflow. The workflow abstracts 6,000 scenarios into general ethical principles, embeds and groups those principles into 90 clusters, and produces bilingual labels and summaries for human review. The raw scenarios, generated clusters, and cluster centroids are research artifacts and are **not loaded by the production app**. Runtime detection uses explicit bilingual rules, manually written general profiles, and the 42 approved bilingual candidate summaries grouped under the 21 production themes. Thus, a user's situation is never matched directly against an ETHICS scenario; embeddings compare it with approved abstract profiles instead.

### Retrieve passages

The selected local Bible corpus is searched using:
   - BM25-style lexical relevance;
   - embedding similarity, when configured;
   - a cautious boost for reviewed theme anchors and a small Gospel preference.

The ranker merges these signals and sends its top 50 candidates to the local `BAAI/bge-reranker-v2-m3` cross-encoder. It then rejects low-confidence and near-duplicate results, limits repetition from one book, and keeps up to six candidates. If none qualify, it retries with a language-specific general wisdom query. Setting `RERANKER_MODEL` to an empty value disables this step for baseline comparison.

### Attach context

To help the user understand each verse as part of its surrounding biblical passage—not as an isolated quotation—the app attaches the narrowest matching bilingual context card from the 200-card reviewed collection. Some cards were created based on World English Bible passage text, using Berean Standard Bible headings only to define literary-unit boundaries; others were prepared from biblical passages with supporting sources such as the Catechism of the Catholic Church, USCCB notes, or OpenBible.info data. Each card displays clickable links to its supporting sources, allowing users to inspect the underlying religious material and independently verify the editorial context.

### Create the reflection

Turn the selected passages and approved context into a clear, natural, and practical reflection. A language-specific Hugging Face model improves readability and makes the guidance feel more coherent and human, but it does not introduce new sources or context. It selects 1–3 candidate passages and returns a structured summary, practical actions, and a qualified application for each. Its output is strictly validated and retried once if necessary. The feature also works without Hugging Face: a deterministic local fallback produces the same core guidance, though its wording may be more extractive and less natural.

### Assemble the response

The backend copies quotations directly from the local corpus, combines them with context and generated applications, and adds translation details, safety guidance, and an explicit limitation that the result is not certain or professional advice. The frontend renders this structured response.

## Optional sharing flow

Nothing is persisted during normal reflection generation. When the user explicitly shares a result, the complete snapshot is stored as JSON in PostgreSQL under a random, unguessable ID. Opening `/share/{id}` retrieves and displays that snapshot without regenerating it.
