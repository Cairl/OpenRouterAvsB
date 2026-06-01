# AGENTS.md

## Project Overview

OpenRouterAvsB is a web application for fetching and comparing AI model benchmark data from OpenRouter in real-time. It features a 1v1 model comparison mode with table, radar chart, and bar chart views. All data is fetched live from OpenRouter APIs with no local caching.

**Architecture**: Python FastAPI backend + Vue 3 + Vite + TypeScript frontend

**Key technologies**:
- Backend: Python 3.12, FastAPI, aiohttp, Pydantic
- Frontend: Vue 3, TypeScript, Vite, ECharts (vue-echarts)
- Data sources: OpenRouter public API, OpenRouter internal benchmarks API

## Project Structure

```
OpenRouterAvsB/
├── server/                     # Python FastAPI backend
│   ├── __init__.py
│   ├── config.py               # API URLs, timeout/concurrency settings; reads model list from models.txt
│   ├── main.py                 # FastAPI app, API endpoints
│   ├── models.py               # Pydantic data models
│   └── scraper.py              # Data fetching from OpenRouter APIs
├── web/                        # Vue 3 + Vite frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── BarView.vue         # Bar chart comparison
│   │   │   ├── BenchmarkContent.vue # View switcher container
│   │   │   ├── FooterBar.vue       # Data source footer
│   │   │   ├── IndexCards.vue      # AA index cards (intelligence/coding/agentic)
│   │   │   ├── ModelSelector.vue   # Dual dropdown + VS text
│   │   │   ├── NavBar.vue          # Dark navigation bar
│   │   │   ├── RadarView.vue       # Radar chart comparison
│   │   │   └── TableView.vue       # Table comparison view
│   │   ├── composables/
│   │   │   ├── useBenchmarks.ts    # Data fetching logic
│   │   │   └── useState.ts         # Reactive state management (provide/inject)
│   │   ├── types/
│   │   │   └── index.ts            # TypeScript interfaces
│   │   ├── App.vue
│   │   ├── main.ts
│   │   ├── style.css
│   │   └── vite-env.d.ts
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts          # Dev proxy /api -> :8000
├── requirements.txt            # Python dependencies
├── models.txt                  # Model ID list (one per line, auto-sorted)
├── run.bat                     # One-click launcher (single window, auto port release)
└── changelog.md
```

## Setup Commands

- Install Python dependencies: `pip install -r requirements.txt`
- Install Node.js dependencies: `cd web && npm install`
- One-click start: `run.bat` (installs deps and launches both servers)

## Development Workflow

- Start backend: `python -m uvicorn server.main:app --host 0.0.0.0 --port 8000`
- Start frontend: `cd web && npm run dev`
- Frontend dev server runs at `http://localhost:5173` with `/api` proxied to backend at `:8000`
- Build frontend: `cd web && npm run build` (output to `web/dist/`)
- Preview production build: `cd web && npm run preview`

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/models` | List all models with basic info (no benchmarks) |
| GET | `/api/benchmarks` | Fetch all models with full benchmark data |
| GET | `/api/benchmarks/{model_id:path}` | Fetch single model with full benchmark data |

## Data Sources

| Source | API | Data |
|--------|-----|------|
| `models.txt` | Local file | Single source of truth for model IDs (one per line, supports `#` comments and empty lines, auto-sorted) |
| OpenRouter Models | `https://openrouter.ai/api/v1/models` | Model names, pricing, context length, modality, canonical_slug |
| OpenRouter AA Benchmarks | `https://openrouter.ai/api/internal/v1/artificial-analysis-benchmarks?slug={canonical_slug}` | AA indices, GPQA, HLE, IFBench, etc. |
| OpenRouter Design Arena | `https://openrouter.ai/api/internal/v1/design-arena-benchmarks?slug={canonical_slug}` | Elo ratings, win rates by category |

The `canonical_slug` is required for internal API calls — it is resolved from the model ID via the `/api/v1/models` endpoint. For the AA benchmarks API, when multiple variants exist, the scraper matches the variant by extracting the portion after `/` from the model ID, replacing `.` with `-`, and matching against OpenRouter's `aa_slug` field (e.g., `z-ai/glm-5.1` → `glm-5-1`). Variant selection by name keywords is unreliable and must be avoided.

## Frontend Data Flow

Data loading follows a lazy async pattern to minimize initial load time:

1. On page load, `/api/models` is called to fetch all model metadata (name, provider, pricing, context_length) — no benchmark data is loaded at this stage
2. When a user selects a model in ModelSelector, `/api/benchmarks/{model_id}` is called to fetch full benchmark data for that model only
3. Loaded benchmark data is cached in `state.models` via the `useState` composable (provide/inject pattern) to avoid duplicate requests for previously selected models
4. The `useBenchmarks` composable orchestrates model selection and dispatches benchmark fetch calls

## Design Conventions

- **Comparison philosophy**: Use "领先" (lead) framing — always show which model is ahead and by what margin with `+` prefix, never show abstract difference values or minus signs
- **Numeric display**: All benchmark values use `toFixed(1)` for exactly one decimal place with trailing zeros; context_length displays raw integer without unit suffixes (no K/M)
- **Typography**: All numeric values use monospace fonts (`var(--font-mono)`) for vertical alignment and scanability
- **Color scheme**: Model A = `#6fa3a7` (teal gray), Model B = `#e8a882` (warm apricot) — applied consistently across ModelSelector, IndexCards, TableView, BarView, and RadarView
- **Bar chart**: Overlapping design with `barGap: -100%`, semi-transparent fills (`rgba` at 0.55 opacity), solid borders at full opacity, 3px rounded corners

## Code Style

### Python (Backend)
- Python 3.12+ with type hints (`float | None`, `dict[str, str]`)
- Pydantic v2 models for all API responses
- Async-first: all data fetching uses `aiohttp` and `asyncio`
- No comments in code unless explicitly requested
- Logging via standard `logging` module, not `print()`

### TypeScript / Vue (Frontend)
- Vue 3 Composition API with `<script setup lang="ts">`
- State management via `provide/inject` pattern in composables (`useState.ts`, `useBenchmarks.ts`)
- ECharts via `vue-echarts` wrapper
- No comments in code unless explicitly requested
- Chinese UI text, English code identifiers
- All benchmark values formatted via `toFixed(1)`; context_length displayed as raw integer (no unit suffix)
- Event listeners (document click, etc.) must be cleaned up in `onUnmounted`
- Frontend typecheck: `cd web && npx vue-tsc --noEmit`

## Build and Deployment

- Frontend production build: `cd web && npm run build` → `web/dist/`
- Backend serves API only; frontend is a separate SPA
- In production, serve `web/dist/` as static files and proxy `/api` to the FastAPI backend

## Troubleshooting

- **`/api/benchmarks` returns empty data**: Check network connectivity to `openrouter.ai`. The internal APIs may be rate-limited; `MAX_CONCURRENT_REQUESTS` in `config.py` controls concurrency (default: 4).
- **Port 8000 already in use**: `run.bat` auto-kills processes on ports 8000/5173 before starting. To manually kill: find PID via `netstat -aon | findstr ":8000"` then `taskkill /PID <pid> /F`.
- **Frontend shows "部分模型数据获取失败"**: One or more models failed to fetch. Check backend logs for specific errors.
