import logging
from contextlib import asynccontextmanager

import aiohttp
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from server.config import MODELS
from server.models import BenchmarksResponse, DesignArenaData, ModelData
from server.scraper import (
    build_model_data,
    fetch_effective_pricing,
    fetch_models_info_and_slugs,
    get_usd_cny_rate,
    scrape_all_benchmarks,
    scrape_single_benchmark,
)

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    connector = aiohttp.TCPConnector(enable_cleanup_closed=True)
    app.state.http_session = aiohttp.ClientSession(connector=connector)
    yield
    await app.state.http_session.close()


app = FastAPI(title="OpenRouterAvsB", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/models")
async def get_models(request: Request) -> list[ModelData]:
    import asyncio

    session = request.app.state.http_session
    exchange_rate = await get_usd_cny_rate(session)
    info_map, slug_map = await fetch_models_info_and_slugs(session, MODELS)

    async def _fetch_official(mid: str):
        slug = slug_map.get(mid, mid)
        return await fetch_effective_pricing(session, slug, mid)

    pricing_results = await asyncio.gather(*[_fetch_official(mid) for mid in MODELS])

    data = []
    for mid, effective_pricing in zip(MODELS, pricing_results):
        model = build_model_data(
            mid,
            info_map.get(mid),
            {"aa_indices": {}, "benchmarks": {}},
            DesignArenaData(),
            exchange_rate,
            effective_pricing,
        )
        data.append(model)
    return data


@app.get("/api/benchmarks")
async def get_benchmarks(request: Request) -> BenchmarksResponse:
    session = request.app.state.http_session
    return await scrape_all_benchmarks(session, MODELS)


@app.get("/api/benchmarks/{model_id:path}")
async def get_benchmark(model_id: str, request: Request) -> ModelData:
    session = request.app.state.http_session
    return await scrape_single_benchmark(session, model_id)
