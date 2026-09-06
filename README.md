# What Would Jesus Do?

Deployed to: https://conatojezus.info

A privacy-conscious, source-grounded Bible reflection app. Users describe a situation, the backend retrieves relevant passages from the public-domain World English Bible, and an optional language model turns those passages into a short, cautious reflection. Scripture quotations always come from the local corpus, never from the language model.

The interface is bilingual. Polish is the default and users can switch to English at any time. Polish quotations use the Updated Gdansk Bible under CC BY-ND 4.0; English quotations use the public-domain World English Bible.

## Stack

- Vue 3 + TypeScript + Vite
- FastAPI + Pydantic
- PostgreSQL 17
- Local hybrid retrieval (BM25 plus multilingual MiniLM embeddings, then BGE reranking)
- Optional Hugging Face chat-completion generation
- 66-book World English Bible (WEB), public domain

The default development mode requires no API key. It returns an extractive reflection based on the highest-ranked passages. Set `HF_TOKEN` and `HF_MODEL` to enable generated prose.

## Run with Docker

Docker Compose runs PostgreSQL, FastAPI, and the Vite development server. Backend and frontend
source directories are bind-mounted, so both development servers reload after edits. Before the
backend starts, a one-shot `build-indexes` service creates any missing semantic indexes. Existing
model-specific indexes are reused.

```bash
cp .env.example .env
docker compose up --build
```

Open http://localhost:5173. The API is also available directly at http://localhost:8000, and
PostgreSQL is exposed on port 5434 by default (`POSTGRES_PORT` can override it). Data, frontend dependencies, and the Hugging Face model cache
are kept in named Docker volumes. Stop the stack with `docker compose down`; add `--volumes` only
when you intentionally want to delete its database and caches.

To rebuild indexes after changing a verse corpus or `EMBEDDING_MODEL`, remove the corresponding
generated `.npy` files from `backend/app/data` and run:

```bash
docker compose run --rm build-indexes
```

## Run directly

Backend (Python 3.11+):

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

Frontend (Node 20+):

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. Vite proxies `/api` to FastAPI on port 8000.

## Deploy with Render, Neon, and Cloudflare Pages

The committed `render.yaml` creates a Standard Render web service for the FastAPI backend. Connect
the repository as a Render Blueprint and provide these secret values when prompted:

- `DATABASE_URL`: the pooled Neon PostgreSQL connection string, including `sslmode=require`
- `ALLOWED_ORIGINS`: the Cloudflare Pages production origin, for example
  `https://wwjd.pages.dev` (multiple origins are comma-separated)
- `HF_TOKEN`: optional; leave empty to use local extractive generation

Render installs the default sentence-transformer and builds the verse indexes during its build
phase. The resulting files are part of the deployed artifact, so the service does not require a
persistent disk and does not download the model on every start. Changing `EMBEDDING_MODEL` triggers
a new build with matching indexes.

Create a Cloudflare Pages project with the following settings:

```text
Root directory: frontend
Build command: npm run build
Build output directory: dist
```

Set `VITE_API_BASE_URL` to the Render service origin without an `/api` suffix, for example
`https://wwjd-api.onrender.com`. Optionally set `VITE_GA_MEASUREMENT_ID`. Local development leaves
`VITE_API_BASE_URL` empty and continues to use Vite's `/api` proxy.

## Configuration

Copy `.env.example` to `.env` or export the values before starting FastAPI.

| Variable | Default | Purpose |
| --- | --- | --- |
| `HF_TOKEN` | empty | Enables Hugging Face inference |
| `HF_MODEL` | `Qwen/Qwen3-4B-Instruct-2507` | Chat model ID |
| `HF_MODEL_PL` | `speakleash/Bielik-11B-v3.0-Instruct` | Polish-specialized chat model ID |
| `HF_BASE_URL` | Hugging Face router | OpenAI-compatible endpoint |
| `HF_MAX_TOKENS` | `1200` | Maximum generated tokens per reflection |
| `HF_TIMEOUT_SECONDS` | `45` | Timeout for one remote model attempt |
| `ALLOWED_ORIGINS` | localhost Vite URLs | Comma-separated CORS origins |
| `MAX_SITUATION_LENGTH` | `3000` | Input limit |
| `EMBEDDING_MODEL` | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` | FastEmbed model for semantic candidate retrieval; empty disables it |
| `RERANKER_MODEL` | `BAAI/bge-reranker-v2-m3` | Cross-encoder reranker; empty disables it |
| `RERANKER_CANDIDATES` | `50` | Number of BM25 + MiniLM candidates BGE scores per query |
| `DATABASE_URL` | `postgresql://wwjd:secret@localhost:5434/wwjd` | PostgreSQL connection URL for explicitly shared reflections |
| `VITE_GA_MEASUREMENT_ID` | empty | GA4 measurement ID (`G-...`); enables consent-based frontend analytics |

Frontend variables belong in `frontend/.env`. Copy `frontend/.env.example` there and add your GA4 measurement ID before building or starting Vite.

The application does not persist user situations unless a user explicitly creates a share link. A shared snapshot is stored in PostgreSQL and is readable by anyone with its unguessable link. Google Analytics is loaded only after explicit consent and never receives the situation text. Avoid enabling request-body logging at the proxy or hosting-provider layer. A remote inference provider may have its own retention policy.

## Bible data, literary context, and retrieval

The committed English and Polish corpora were generated from eBible.org's official `engwebp_usfx.zip` and `polubg_usfx.zip` archives. Regenerate either with:

```bash
python backend/scripts/import_usfx.py path/to/engwebp_usfx.xml backend/app/data/web_verses.json
```

Retrieval uses multilingual embeddings executed with ONNX Runtime together with BM25 lexical ranking. It passes the top 50 fused candidates to the Apache-2.0 `BAAI/bge-reranker-v2-m3` cross-encoder before applying confidence, diversity, and context rules. It ranks individual verses, filters low-confidence results, and avoids automatically quoting unrelated neighboring verses. The default embedding model is `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`; `EMBEDDING_MODEL` can be set to another model supported by FastEmbed. Set `RERANKER_MODEL` to an empty value to retain the pre-reranker baseline.

Ethical-theme routing combines high-confidence bilingual lexical rules with general bilingual
semantic profiles. A semantic profile may add at most one concern not already detected by the
rules. Themes act as cautious priors for reviewed passage anchors and never exclude strong direct
retrieval results. The catalog currently covers 18 concerns, and tests require every theme to have
rules, profiles, anchors, and Polish and English display names.

Theme discovery uses licensed external scenarios as editorial evidence rather than copying isolated
examples into production profiles. Download the MIT-licensed ETHICS archive and build the
non-publishable 90-cluster review set with:

```bash
curl -L https://people.eecs.berkeley.edu/~hendrycks/ethics.tar -o /tmp/ethics.tar
cd backend
uv run python scripts/theme_discovery.py /tmp/ethics.tar
```

The script first abstracts 6,000 scenarios into general ethical principles, then clusters those
principles and proposes bilingual labels and summaries. It caches the auditable abstractions in
`theme_principle_cache.json`; reruns do not repeat that API work. The generated
`theme_cluster_drafts.json` retains source record IDs, principles, coherence scores, and starts
with every cluster unassigned and unreviewed. `theme_cluster_centroids.npy` contains the
corresponding normalized centroids. None of these artifacts is loaded by the production router.
Licensing decisions and excluded sources are documented in
`backend/app/data/THEME_DATA_LICENSES.md`.

Human consolidation decisions are stored separately in `theme_cluster_review.json`; generated
clusters are never edited in place. Rebuild the deduplicated editorial queue with:

```bash
cd backend
uv run python scripts/theme_cluster_review.py
```

The resulting `theme_candidates.json` excludes rejected broad or non-ethical clusters and applies
approved renames and merges. `theme_candidate_alignment.json` maps every candidate exactly once:
either to the original 18-theme catalog or to one of three approved new concerns. When the
alignment has `status: approved`, the application loads the 42 bilingual candidate summaries as
semantic profile enrichment for the resulting 21 production themes. Raw ETHICS scenarios and
cluster centroids are never loaded by production routing.

```bash
cd backend
uv run python scripts/build_indexes.py
```

Displayed context comes from versioned, bilingual literary-unit cards in
`backend/app/data/context_cards.json`. Only cards with explicit human review are used; uncovered
passages receive a deliberately limited chapter-level fallback. Validate cards or create a draft
editorial queue with `python backend/scripts/context_cards.py CARD_FILE`.

To prepare a broad 200-card target set from public-domain BSB literary headings, run
`generate_context_card_drafts.py` with `--prepare-only`. Removing that flag generates bilingual
drafts through the configured Hugging Face model. Generated cards always remain `reviewed: false`
until a human editor approves them. The committed `context_card_generation_queue.json` contains
the current 177-unit expansion plan; it covers 72 books, while the existing Sirach card completes
coverage of all 73 Catholic-canon books.

The importer recognizes the seven deuterocanonical books and the additions carried by Catholic
Esther and Daniel source files. English can be migrated to the public-domain World English Bible
Catholic Edition. The Polish production corpus remains the licensed 66-book UBG until written
digital-use permission for Biblia Tysiąclecia is obtained; no protected text is bundled here.

## Verification

```bash
cd backend && uv run pytest
cd backend && uv run ruff check .
cd backend && uv run bandit -r app
cd frontend && npm run lint && npm run test && npm run build
```

The same checks run on every push and pull request in GitHub Actions. Trivy additionally scans
the locked backend and frontend dependencies for known high and critical vulnerabilities.

## Product boundary

The result is described as an AI-generated, Bible-grounded reflection—not a certain declaration of what Jesus would do. Emergency, self-harm, and abuse-related language receives an immediate safety message, and the app explicitly does not replace emergency, medical, legal, mental-health, or pastoral help.

## Verse selection evaluation

A draft Polish evaluation set contains 100 synthetic situations (50 about prejudice,
50 covering other concerns), with suggested scripture references and rationales for
human review. See [the review document](backend/evaluation/review.pl.md) and
[the evaluation instructions](backend/evaluation/README.md) for editing the dataset,
running the API benchmark, and comparing architecture variants.
