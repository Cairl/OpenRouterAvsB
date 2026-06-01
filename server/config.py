from pathlib import Path
import re

_MODELS_FILE = Path(__file__).resolve().parent.parent / "models.txt"


def _natural_sort_key(s: str) -> list[str | int]:
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r"(\d+)", s)]


def _load_models() -> list[str]:
    if not _MODELS_FILE.exists():
        return []
    lines = _MODELS_FILE.read_text(encoding="utf-8").splitlines()
    raw = [line.strip() for line in lines if line.strip() and not line.strip().startswith("#")]
    seen: set[str] = set()
    models: list[str] = []
    for m in raw:
        if m not in seen:
            seen.add(m)
            models.append(m)
    models.sort(key=_natural_sort_key)
    _MODELS_FILE.write_text("\n".join(models) + "\n", encoding="utf-8")
    return models


MODELS = _load_models()

OPENROUTER_BASE_URL = "https://openrouter.ai"
OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"
OPENROUTER_AA_BENCHMARKS_API = "https://openrouter.ai/api/internal/v1/artificial-analysis-benchmarks"
OPENROUTER_DA_BENCHMARKS_API = "https://openrouter.ai/api/internal/v1/design-arena-benchmarks"
SCRAPING_TIMEOUT = 30
MAX_CONCURRENT_REQUESTS = 4
