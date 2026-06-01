import { inject, reactive, type InjectionKey } from "vue";
import type { ModelData } from "../types";

interface AppState {
  models: ModelData[];
  modelA: ModelData | null;
  modelB: ModelData | null;
  loading: boolean;
  loadProgress: number;
  error: string | null;
  modelALoading: boolean;
  modelBLoading: boolean;
}

export const AppStateKey: InjectionKey<AppState> = Symbol("AppState");

const STORAGE_KEY = "openrouter_spar_selected_models";

export function getPersistedModelIds(): { modelAId: string | null; modelBId: string | null } {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      return {
        modelAId: typeof parsed.modelAId === "string" ? parsed.modelAId : null,
        modelBId: typeof parsed.modelBId === "string" ? parsed.modelBId : null,
      };
    }
  } catch {
    // ignore
  }
  return { modelAId: null, modelBId: null };
}

export function persistModelSelection(modelAId: string | null, modelBId: string | null) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ modelAId, modelBId }));
  } catch {
    // ignore
  }
}

export function createAppState(): AppState {
  return reactive<AppState>({
    models: [],
    modelA: null,
    modelB: null,
    loading: false,
    loadProgress: 0,
    error: null,
    modelALoading: false,
    modelBLoading: false,
  });
}

export function useAppState(): AppState {
  const state = inject(AppStateKey);
  if (!state) throw new Error("AppState not provided");
  return state;
}
