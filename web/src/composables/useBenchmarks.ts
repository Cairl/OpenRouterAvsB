import type { ModelData } from "../types";
import { useAppState, persistModelSelection, getPersistedModelIds } from "./useState";

export function useBenchmarks() {
  const state = useAppState();

  async function fetchModelList() {
    state.loading = true;
    state.error = null;
    try {
      const resp = await fetch("/api/models");
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data: ModelData[] = await resp.json();
      state.models = data;
      state.loadProgress = data.length;
    } catch (e) {
      state.error = e instanceof Error ? e.message : "未知错误";
    } finally {
      state.loading = false;
    }
  }

  async function fetchModelBenchmark(modelId: string): Promise<ModelData | null> {
    try {
      const resp = await fetch(`/api/benchmarks/${encodeURIComponent(modelId)}`);
      if (!resp.ok) return null;
      return await resp.json();
    } catch {
      return null;
    }
  }

  function loadModelABenchmark(modelId: string) {
    state.modelALoading = true;
    fetchModelBenchmark(modelId).then((full) => {
      if (full) {
        state.modelA = full;
        const idx = state.models.findIndex((m) => m.id === modelId);
        if (idx >= 0) state.models[idx] = full;
      }
      state.modelALoading = false;
    });
  }

  function loadModelBBenchmark(modelId: string) {
    state.modelBLoading = true;
    fetchModelBenchmark(modelId).then((full) => {
      if (full) {
        state.modelB = full;
        const idx = state.models.findIndex((m) => m.id === modelId);
        if (idx >= 0) state.models[idx] = full;
      }
      state.modelBLoading = false;
    });
  }

  function selectModelA(model: ModelData) {
    state.modelA = model;
    persistModelSelection(state.modelA?.id ?? null, state.modelB?.id ?? null);
    loadModelABenchmark(model.id);
  }

  function selectModelB(model: ModelData) {
    state.modelB = model;
    persistModelSelection(state.modelA?.id ?? null, state.modelB?.id ?? null);
    loadModelBBenchmark(model.id);
  }

  function swapModels() {
    const temp = state.modelA;
    state.modelA = state.modelB;
    state.modelB = temp;
    persistModelSelection(state.modelA?.id ?? null, state.modelB?.id ?? null);
  }

  function restorePersistedModels() {
    const { modelAId, modelBId } = getPersistedModelIds();
    if (modelAId) {
      const found = state.models.find((m) => m.id === modelAId);
      if (found) {
        state.modelA = found;
        loadModelABenchmark(modelAId);
      }
    }
    if (modelBId) {
      const found = state.models.find((m) => m.id === modelBId);
      if (found) {
        state.modelB = found;
        loadModelBBenchmark(modelBId);
      }
    }
  }

  function selectModelAById(modelId: string) {
    const existing = state.models.find((m) => m.id === modelId);
    if (existing) {
      selectModelA(existing);
      return;
    }
    const placeholder: ModelData = {
      id: modelId,
      name: modelId.split("/").pop() ?? modelId,
      provider: modelId.split("/")[0] ?? "",
      context_length: 0,
      max_output: 0,
      created: 0,
      canonical_slug: "",
      pricing: { prompt_per_m: 0, completion_per_m: 0, prompt_per_m_usd: 0, completion_per_m_usd: 0 },
      modality: "",
      aa_indices: { intelligence: null, coding: null, agentic: null },
      aa_percentiles: { intelligence_percentile: null, coding_percentile: null, agentic_percentile: null },
      benchmarks: {},
      design_arena: { models_arena: {}, agents_arena: {} },
      error: null,
    };
    state.modelA = placeholder;
    persistModelSelection(modelId, state.modelB?.id ?? null);
    loadModelABenchmark(modelId);
  }

  function selectModelBById(modelId: string) {
    const existing = state.models.find((m) => m.id === modelId);
    if (existing) {
      selectModelB(existing);
      return;
    }
    const placeholder: ModelData = {
      id: modelId,
      name: modelId.split("/").pop() ?? modelId,
      provider: modelId.split("/")[0] ?? "",
      context_length: 0,
      max_output: 0,
      created: 0,
      canonical_slug: "",
      pricing: { prompt_per_m: 0, completion_per_m: 0, prompt_per_m_usd: 0, completion_per_m_usd: 0 },
      modality: "",
      aa_indices: { intelligence: null, coding: null, agentic: null },
      aa_percentiles: { intelligence_percentile: null, coding_percentile: null, agentic_percentile: null },
      benchmarks: {},
      design_arena: { models_arena: {}, agents_arena: {} },
      error: null,
    };
    state.modelB = placeholder;
    persistModelSelection(state.modelA?.id ?? null, modelId);
    loadModelBBenchmark(modelId);
  }

  return { fetchModelList, selectModelA, selectModelB, selectModelAById, selectModelBById, swapModels, restorePersistedModels };
}