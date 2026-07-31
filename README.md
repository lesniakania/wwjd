# What Would Jesus Do?

A privacy-conscious, source-grounded Bible reflection app. Users describe a situation, the backend retrieves relevant passages from the public-domain World English Bible, and an optional language model turns those passages into a short, cautious reflection. Scripture quotations always come from the local corpus, never from the language model.

The interface is bilingual. Polish is the default and users can switch to English at any time. Polish quotations use the Updated Gdansk Bible under CC BY-ND 4.0; English quotations use the public-domain World English Bible.

## Stack

- Vue 3 + TypeScript + Vite
- FastAPI + Pydantic
- PostgreSQL 17
- Local hybrid retrieval (BM25-style lexical score plus deterministic semantic hashing)
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
| `DATABASE_URL` | `postgresql://wwjd:secret@localhost:5434/wwjd` | PostgreSQL connection URL for explicitly shared reflections |
| `VITE_GA_MEASUREMENT_ID` | empty | GA4 measurement ID (`G-...`); enables consent-based frontend analytics |

Frontend variables belong in `frontend/.env`. Copy `frontend/.env.example` there and add your GA4 measurement ID before building or starting Vite.

The application does not persist user situations unless a user explicitly creates a share link. A shared snapshot is stored in PostgreSQL and is readable by anyone with its unguessable link. Google Analytics is loaded only after explicit consent and never receives the situation text. Avoid enabling request-body logging at the proxy or hosting-provider layer. A remote inference provider may have its own retention policy.

## Bible data, literary context, and retrieval

The committed English and Polish corpora were generated from eBible.org's official `engwebp_usfx.zip` and `polubg_usfx.zip` archives. Regenerate either with:

```bash
python backend/scripts/import_usfx.py path/to/engwebp_usfx.xml backend/app/data/web_verses.json
```

Retrieval uses multilingual Sentence Transformers embeddings together with BM25 lexical ranking. It ranks individual verses, filters low-confidence results, and avoids automatically quoting unrelated neighboring verses. The default model is `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`; set `EMBEDDING_MODEL=BAAI/bge-m3` for a GPU-backed deployment. Build or refresh the local semantic indexes with:

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
cd frontend && npm run test && npm run build
```

## Product boundary

The result is described as an AI-generated, Bible-grounded reflection—not a certain declaration of what Jesus would do. Emergency, self-harm, and abuse-related language receives an immediate safety message, and the app explicitly does not replace emergency, medical, legal, mental-health, or pastoral help.
