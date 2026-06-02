import asyncio
import logging
import re
import time
from typing import Any
from urllib.parse import quote

import aiohttp

from server.config import (
    MAX_CONCURRENT_REQUESTS,
    OPENROUTER_AA_BENCHMARKS_API,
    OPENROUTER_API_BASE,
    OPENROUTER_DA_BENCHMARKS_API,
    SCRAPING_TIMEOUT,
)
from server.models import (
    AAIndices,
    AAPercentiles,
    BenchmarksResponse,
    DesignArenaCategory,
    DesignArenaData,
    ModelData,
    ModelPricing,
)

logger = logging.getLogger(__name__)

_USD_CNY_RATE: float | None = None
_RATE_TIMESTAMP: float = 0
_RATE_TTL = 3600
_FALLBACK_RATE = 7.25


async def get_usd_cny_rate(session: aiohttp.ClientSession | None = None) -> float:
    global _USD_CNY_RATE, _RATE_TIMESTAMP
    if _USD_CNY_RATE and (time.time() - _RATE_TIMESTAMP) < _RATE_TTL:
        return _USD_CNY_RATE
    try:
        own_session = session is None
        if own_session:
            session = aiohttp.ClientSession()
        try:
            async with session.get(
                "https://open.er-api.com/v6/latest/USD",
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json(content_type=None)
                    rate = data.get("rates", {}).get("CNY")
                    if rate:
                        _USD_CNY_RATE = float(rate)
                        _RATE_TIMESTAMP = time.time()
                        logger.info("Fetched USD→CNY rate: %.4f", _USD_CNY_RATE)
                        return _USD_CNY_RATE
        finally:
            if own_session:
                await session.close()
    except Exception as e:
        logger.warning("Failed to fetch exchange rate: %s", e)
    if not _USD_CNY_RATE:
        _USD_CNY_RATE = _FALLBACK_RATE
        _RATE_TIMESTAMP = time.time()
        logger.info("Using fallback USD→CNY rate: %.4f", _FALLBACK_RATE)
    return _USD_CNY_RATE

AA_INDEX_MAP = {
    "artificial_analysis_intelligence_index": "intelligence",
    "artificial_analysis_coding_index": "coding",
    "artificial_analysis_agentic_index": "agentic",
}

BENCHMARK_KEY_MAP = {
    "gpqa": "GPQA Diamond",
    "hle": "HLE",
    "ifbench": "IFBench",
    "tau2": "τ²-Bench Telecom",
    "lcr": "AA-LCR",
    "gdpval_aa": "GDPval-AA",
    "critpt": "CritPt",
    "scicode": "SciCode",
    "terminalbench_hard": "Terminal-Bench Hard",
    "aa_omniscience_accuracy": "AA-Omniscience Accuracy",
    "aa_omniscience_non_hallucination_rate": "AA-Omniscience Non-Hallucination Rate",
}


async def fetch_models_info_and_slugs(
    session: aiohttp.ClientSession, model_ids: list[str]
) -> tuple[dict[str, dict], dict[str, str]]:
    url = f"{OPENROUTER_API_BASE}/models"
    try:
        async with session.get(
            url, timeout=aiohttp.ClientTimeout(total=SCRAPING_TIMEOUT)
        ) as resp:
            if resp.status != 200:
                logger.error("Failed to fetch models list: %s", resp.status)
                return {}, {}
            data = await resp.json(content_type=None)
            info_map: dict[str, dict] = {}
            slug_map: dict[str, str] = {}
            for m in data.get("data", []):
                if m["id"] in model_ids:
                    info_map[m["id"]] = m
                    slug_map[m["id"]] = m.get("canonical_slug", m["id"])
            return info_map, slug_map
    except Exception as e:
        logger.error("Error fetching models list: %s", e)
        return {}, {}


def _parse_aa_benchmark_variant(evaluations: dict) -> dict:
    aa_indices: dict[str, float] = {}
    for api_key, model_key in AA_INDEX_MAP.items():
        val = evaluations.get(api_key)
        if val is not None:
            aa_indices[model_key] = val

    benchmarks: dict[str, float] = {}
    for api_key, label in BENCHMARK_KEY_MAP.items():
        val = evaluations.get(api_key)
        if val is not None:
            benchmarks[label] = round(val * 100, 1)

    return {"aa_indices": aa_indices, "benchmarks": benchmarks}


async def fetch_model_benchmarks(
    session: aiohttp.ClientSession, canonical_slug: str, model_id: str
) -> dict:
    url = f"{OPENROUTER_AA_BENCHMARKS_API}?slug={quote(canonical_slug, safe='')}"
    try:
        async with session.get(
            url, timeout=aiohttp.ClientTimeout(total=SCRAPING_TIMEOUT)
        ) as resp:
            if resp.status != 200:
                return {
                    "aa_indices": {},
                    "benchmarks": {},
                    "error": f"AA API returned {resp.status}",
                }
            data = await resp.json(content_type=None)
            variants = data.get("data", [])
            if not variants:
                return {
                    "aa_indices": {},
                    "benchmarks": {},
                    "error": "No benchmark data available",
                }

            variant = variants[0]
            if len(variants) > 1:
                best_score = -1.0
                for v in variants:
                    ev = v.get("benchmark_data", {}).get("evaluations", {})
                    score = ev.get("artificial_analysis_intelligence_index")
                    if score is not None and score > best_score:
                        best_score = score
                        variant = v

            evaluations = variant.get("benchmark_data", {}).get("evaluations", {})
            result = _parse_aa_benchmark_variant(evaluations)

            percentiles = variant.get("percentiles", {})
            result["aa_percentiles"] = {
                "intelligence_percentile": percentiles.get("intelligence_percentile"),
                "coding_percentile": percentiles.get("coding_percentile"),
                "agentic_percentile": percentiles.get("agentic_percentile"),
            }

            for v in variants:
                ev = v.get("benchmark_data", {}).get("evaluations", {})
                if "aa_omniscience_hallucination_rate" in ev and "AA-Omniscience Hallucination Rate" not in result["benchmarks"]:
                    result["benchmarks"]["AA-Omniscience Hallucination Rate"] = round(
                        ev["aa_omniscience_hallucination_rate"] * 100, 1
                    )

            return result
    except Exception as e:
        logger.error("Error fetching AA benchmarks for %s: %s", canonical_slug, e)
        return {"aa_indices": {}, "benchmarks": {}, "error": str(e)}


async def fetch_design_arena(
    session: aiohttp.ClientSession, canonical_slug: str
) -> DesignArenaData:
    url = f"{OPENROUTER_DA_BENCHMARKS_API}?slug={quote(canonical_slug, safe='')}"
    try:
        async with session.get(
            url, timeout=aiohttp.ClientTimeout(total=SCRAPING_TIMEOUT)
        ) as resp:
            if resp.status != 200:
                return DesignArenaData()
            data = await resp.json(content_type=None)
            records = data.get("data", {}).get("records", [])

            models_arena: dict[str, DesignArenaCategory] = {}
            agents_arena: dict[str, DesignArenaCategory] = {}
            for record in records:
                category = record.get("category", "").lower().replace(" ", "-")
                arena_type = record.get("arena", "")
                entry = DesignArenaCategory(
                    elo=record.get("elo", 0),
                    win_rate=record.get("win_rate", 0),
                )
                if "Models" in arena_type:
                    models_arena[category] = entry
                elif "Agents" in arena_type:
                    agents_arena[category] = entry

            return DesignArenaData(models_arena=models_arena, agents_arena=agents_arena)
    except Exception as e:
        logger.error("Error fetching design arena for %s: %s", canonical_slug, e)
        return DesignArenaData()


async def fetch_effective_pricing(
    session: aiohttp.ClientSession, canonical_slug: str, model_id: str
) -> dict[str, str] | None:
    url = f"https://openrouter.ai/{quote(canonical_slug, safe='/')}"
    try:
        async with session.get(
            url,
            timeout=aiohttp.ClientTimeout(total=SCRAPING_TIMEOUT),
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
        ) as resp:
            if resp.status != 200:
                logger.warning("Overview page returned %s for %s", resp.status, url)
                return None
            html = await resp.text()

        search_str = '\\"pricing\\":{'
        idx = html.find(search_str)
        if idx == -1:
            logger.warning("No pricing block found in overview for %s", model_id)
            return None

        start = idx + len(search_str)
        depth = 1
        end = start
        while depth > 0 and end < len(html):
            if html[end] == '{':
                depth += 1
            elif html[end] == '}':
                depth -= 1
            end += 1

        pricing_json_str = '{' + html[start:end - 1] + '}'
        pricing_json_str = pricing_json_str.replace('\\"', '"')

        try:
            import json
            pricing_data = json.loads(pricing_json_str)
            prompt_price = pricing_data.get("prompt")
            completion_price = pricing_data.get("completion")
            if prompt_price is not None and completion_price is not None:
                return {"prompt": str(prompt_price), "completion": str(completion_price)}
        except json.JSONDecodeError:
            pass

        logger.warning("Failed to parse pricing JSON for %s", model_id)
        return None
    except Exception as e:
        logger.error("Error fetching effective pricing for %s: %s", canonical_slug, e)
        return None


def build_model_data(
    model_id: str,
    basic_info: dict | None,
    benchmarks_data: dict,
    design_arena_data: DesignArenaData,
    exchange_rate: float = 1.0,
    effective_pricing: dict[str, str] | None = None,
) -> ModelData:
    if basic_info:
        name = basic_info.get("name", model_id)
        provider = model_id.split("/")[0]
        pricing_source = effective_pricing if effective_pricing else basic_info.get("pricing", {})
        prompt_usd = float(pricing_source.get("prompt", "0")) * 1_000_000
        completion_usd = float(pricing_source.get("completion", "0")) * 1_000_000
        prompt_price = prompt_usd * exchange_rate
        completion_price = completion_usd * exchange_rate
        context_length = basic_info.get("context_length", 0)
        max_output = (basic_info.get("top_provider") or {}).get("max_completion_tokens", 0) or 0
        created = basic_info.get("created", 0) or 0
        canonical_slug = basic_info.get("canonical_slug", "")
        modality = basic_info.get("architecture", {}).get("modality", "")
    else:
        name = model_id
        provider = model_id.split("/")[0]
        prompt_usd = 0.0
        completion_usd = 0.0
        prompt_price = 0.0
        completion_price = 0.0
        context_length = 0
        max_output = 0
        created = 0
        canonical_slug = ""
        modality = ""

    return ModelData(
        id=model_id,
        name=name,
        provider=provider,
        context_length=context_length,
        max_output=max_output,
        created=created,
        canonical_slug=canonical_slug,
        pricing=ModelPricing(
            prompt_per_m=prompt_price,
            completion_per_m=completion_price,
            prompt_per_m_usd=prompt_usd,
            completion_per_m_usd=completion_usd,
        ),
        modality=modality,
        aa_indices=AAIndices(**benchmarks_data.get("aa_indices", {})),
        aa_percentiles=AAPercentiles(**benchmarks_data.get("aa_percentiles", {})),
        benchmarks=benchmarks_data.get("benchmarks", {}),
        design_arena=design_arena_data,
        error=benchmarks_data.get("error"),
    )


async def _fetch_model_all_data(
    session: aiohttp.ClientSession,
    model_id: str,
    canonical_slug: str,
) -> tuple[str, dict, DesignArenaData, dict[str, str] | None]:
    benchmarks_data, design_arena_data, effective_pricing = await asyncio.gather(
        fetch_model_benchmarks(session, canonical_slug, model_id),
        fetch_design_arena(session, canonical_slug),
        fetch_effective_pricing(session, canonical_slug, model_id),
    )
    return model_id, benchmarks_data, design_arena_data, effective_pricing


async def scrape_all_benchmarks(session: aiohttp.ClientSession, model_ids: list[str]) -> BenchmarksResponse:
    exchange_rate = await get_usd_cny_rate(session)
    info_map, slug_map = await fetch_models_info_and_slugs(session, model_ids)

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

    async def _limited_fetch(mid: str, slug: str):
        async with semaphore:
            return await _fetch_model_all_data(session, mid, slug)

    tasks = []
    for mid in model_ids:
        slug = slug_map.get(mid, mid)
        tasks.append(_limited_fetch(mid, slug))

    results = await asyncio.gather(*tasks)

    data: list[ModelData] = []
    failed: list[str] = []
    for mid, benchmarks_data, design_arena_data, effective_pricing in results:
        model = build_model_data(mid, info_map.get(mid), benchmarks_data, design_arena_data, exchange_rate, effective_pricing)
        if model.error:
            failed.append(mid)
        data.append(model)

    return BenchmarksResponse(data=data, failed=failed, exchange_rate=exchange_rate)


async def scrape_single_benchmark(session: aiohttp.ClientSession, model_id: str) -> ModelData:
    exchange_rate = await get_usd_cny_rate(session)
    info_map, slug_map = await fetch_models_info_and_slugs(session, [model_id])
    slug = slug_map.get(model_id, model_id)
    benchmarks_data, design_arena_data, effective_pricing = await asyncio.gather(
        fetch_model_benchmarks(session, slug, model_id),
        fetch_design_arena(session, slug),
        fetch_effective_pricing(session, slug, model_id),
    )
    return build_model_data(
        model_id, info_map.get(model_id), benchmarks_data, design_arena_data, exchange_rate, effective_pricing
    )
