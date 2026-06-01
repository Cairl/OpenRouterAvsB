from pydantic import BaseModel


class ModelPricing(BaseModel):
    prompt_per_m: float
    completion_per_m: float
    prompt_per_m_usd: float
    completion_per_m_usd: float


class AAIndices(BaseModel):
    intelligence: float | None = None
    coding: float | None = None
    agentic: float | None = None


class AAPercentiles(BaseModel):
    intelligence_percentile: int | None = None
    coding_percentile: int | None = None
    agentic_percentile: int | None = None


class DesignArenaCategory(BaseModel):
    elo: float
    win_rate: float


class DesignArenaData(BaseModel):
    models_arena: dict[str, DesignArenaCategory] = {}
    agents_arena: dict[str, DesignArenaCategory] = {}


class ModelData(BaseModel):
    id: str
    name: str
    provider: str
    context_length: int
    max_output: int = 0
    created: int = 0
    canonical_slug: str = ""
    pricing: ModelPricing
    modality: str
    aa_indices: AAIndices = AAIndices()
    aa_percentiles: AAPercentiles = AAPercentiles()
    benchmarks: dict[str, float] = {}
    design_arena: DesignArenaData = DesignArenaData()
    error: str | None = None


class BenchmarksResponse(BaseModel):
    data: list[ModelData]
    failed: list[str] = []
    exchange_rate: float = 1.0
