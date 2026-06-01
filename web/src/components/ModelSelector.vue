<template>
  <div class="selector-area" v-if="!state.loading">
    <div class="section-label">选择模型</div>
    <div class="split-selectors">
      <div class="split-card split-card-a">
        <div class="split-model split-a">
          <div class="model-chip-wrap" ref="triggerA">
            <div class="model-chip chip-a">
              <input
                v-model="inputA"
                @focus="onFocusA"
                @blur="onBlurA"
                @keydown.enter="onEnterA"
                placeholder="输入模型 ID..."
              />
              <a class="chip-link" v-if="state.modelA" :href="'https://openrouter.ai/' + state.modelA.id" target="_blank" rel="noopener" @mousedown.prevent>
                <svg viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M5 2h7v7M11 2L4 9"/></svg>
              </a>
              <button class="chip-toggle" @click="openA = !openA" tabindex="-1">
                <svg viewBox="0 0 12 12" fill="none" stroke-width="1.5" stroke-linecap="round"><path d="M3 5l3 3 3-3"/></svg>
              </button>
            </div>
            <Transition name="dropdown">
              <div class="select-dropdown" v-if="openA && groupedModels.length">
                <template v-for="group in groupedModels" :key="group.provider">
                  <div class="select-group-label">{{ group.provider }}</div>
                  <div
                    v-for="m in group.models"
                    :key="m.id"
                    :class="['select-option', { active: m.id === state.modelA?.id }]"
                    @mousedown.prevent="pickA(m.id)"
                  >
                    {{ m.name.indexOf(": ") !== -1 ? m.name.slice(m.name.indexOf(": ") + 2) : m.name }}
                  </div>
                </template>
              </div>
            </Transition>
          </div>
          <span class="model-date" v-if="state.modelA?.created">{{ formatDate(state.modelA.created) }}</span>
        </div>
      </div>
      <div class="shrink-spacer shrink-spacer-a"></div>
      <div class="split-vs" ref="vsContainer" data-hover="" @mousemove="onVsMouseMove" @mouseleave="onVsMouseLeave">
        <span class="vs-label a" data-target="a">A</span>
        <span class="vs-divider" data-target="vs">VS</span>
        <span class="vs-exclaim exclaim-left">!</span>
        <span class="vs-exclaim exclaim-right">!</span>
        <span class="vs-label b" data-target="b">B</span>
      </div>
      <div class="shrink-spacer shrink-spacer-b"></div>
      <div class="split-card split-card-b">
        <div class="split-model split-b">
          <div class="model-chip-wrap" ref="triggerB">
            <div class="model-chip chip-b">
              <input
                v-model="inputB"
                @focus="onFocusB"
                @blur="onBlurB"
                @keydown.enter="onEnterB"
                placeholder="输入模型 ID..."
              />
              <a class="chip-link" v-if="state.modelB" :href="'https://openrouter.ai/' + state.modelB.id" target="_blank" rel="noopener" @mousedown.prevent>
                <svg viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M5 2h7v7M11 2L4 9"/></svg>
              </a>
              <button class="chip-toggle" @click="openB = !openB" tabindex="-1">
                <svg viewBox="0 0 12 12" fill="none" stroke-width="1.5" stroke-linecap="round"><path d="M3 5l3 3 3-3"/></svg>
              </button>
            </div>
            <Transition name="dropdown">
              <div class="select-dropdown" v-if="openB && groupedModels.length">
                <template v-for="group in groupedModels" :key="group.provider">
                  <div class="select-group-label">{{ group.provider }}</div>
                  <div
                    v-for="m in group.models"
                    :key="m.id"
                    :class="['select-option', { active: m.id === state.modelB?.id }]"
                    @mousedown.prevent="pickB(m.id)"
                  >
                    {{ m.name.indexOf(": ") !== -1 ? m.name.slice(m.name.indexOf(": ") + 2) : m.name }}
                  </div>
                </template>
              </div>
            </Transition>
          </div>
          <span class="model-date" v-if="state.modelB?.created">{{ formatDate(state.modelB.created) }}</span>
        </div>
      </div>
    </div>

    <div class="index-cards" v-if="state.modelA && state.modelB">
      <div class="index-card" v-for="idx in indices" :key="idx.key">
        <div class="ic-label">{{ idx.shortLabel }}</div>
        <div class="ic-vals">
          <span class="ic-val a">{{ formatIndexValue(idx.valueA) }}</span>
          <span class="ic-val b">{{ formatIndexValue(idx.valueB) }}</span>
        </div>
        <div class="ic-chart" :data-side="idxHover && idxHover.key === idx.key ? idxHover.side : ''" @mousemove="onIdxMouseMove($event, idx)" @mouseleave="idxHover = null">
          <div class="ic-center-line"></div>
          <div class="ic-bar-a" :style="barStyleA(idx)"></div>
          <div class="ic-bar-b" :style="barStyleB(idx)"></div>
          <div class="ic-dot" :class="[dotClass(idx), { 'ic-dot-hover': idxHover && idxHover.key === idx.key }]" :style="dotStyle(idx)"></div>
          <div class="ic-tooltip" :class="idxTooltipClass(idx)" :style="idxTooltipStyle(idx)">
            <span class="ic-tip-text">{{ idxHover?.text }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="meta-cards" v-if="state.modelA && state.modelB">
      <div class="meta-card" v-for="m in metaMetrics" :key="m.key">
        <div class="mc-label">{{ m.label }}</div>
        <div class="mc-vals">
          <div class="mc-val-wrap a" :class="{ 'mc-wins': m.winner === 'a' }">
            <span class="mc-price-main">{{ m.displayA }}</span>
            <span class="mc-tip-unit" v-if="m.usdA">¥<span class="mc-per-unit" v-if="m.key === 'input' || m.key === 'output'">/M tokens</span></span>
          </div>
          <div class="mc-val-wrap b" :class="{ 'mc-wins': m.winner === 'b' }">
            <span class="mc-price-main">{{ m.displayB }}</span>
            <span class="mc-tip-unit" v-if="m.usdB">¥<span class="mc-per-unit" v-if="m.key === 'input' || m.key === 'output'">/M tokens</span></span>
          </div>
        </div>
        <div class="mc-chart" :data-side="metaHover && metaHover.key === m.key ? metaHover.side : ''" @mousemove="onMetaMouseMove($event, m)" @mouseleave="metaHover = null">
          <div class="mc-center-line"></div>
          <div class="mc-bar-a" :style="metaBarA(m)"></div>
          <div class="mc-bar-b" :style="metaBarB(m)"></div>
          <div class="mc-dot" :class="[metaDotClass(m), { 'mc-dot-hover': metaHover && metaHover.key === m.key }]" :style="metaDotStyle(m)"></div>
          <div class="mc-tooltip" :class="metaTooltipClass(m)" :style="metaTooltipStyle(m)">
              <template v-if="m.key === 'ctx'">
                <span class="mc-tip-label">最大输出</span>
                <span class="mc-tip-value">{{ (metaHover?.side === 'a' ? m.maxOutputA : m.maxOutputB) ? formatCompactNumber(metaHover?.side === 'a' ? m.maxOutputA : m.maxOutputB) : '—' }}</span>
              </template>
              <template v-else>
                <span class="mc-tip-currency">USD</span>
                <span class="mc-tip-value">{{ metaHover?.usd?.replace('$', '') }}</span>
                <span class="mc-tip-unit">$</span>
              </template>
            </div>
        </div>
      </div>
    </div>
    <div class="meta-cards meta-cards-single" v-else-if="state.modelA || state.modelB">
      <div class="meta-card">
        <div class="meta-side">
          <template v-if="state.modelA">
            <span>上下文长度: {{ formatNumber(state.modelA.context_length) }}</span>
            <span>输入价格<span class="price-unit">/M</span>: {{ formatPricePair(state.modelA.pricing.prompt_per_m_usd, state.modelA.pricing.prompt_per_m) }}</span>
            <span>输出价格<span class="price-unit">/M</span>: {{ formatPricePair(state.modelA.pricing.completion_per_m_usd, state.modelA.pricing.completion_per_m) }}</span>
          </template>
          <template v-else-if="state.modelB">
            <span>上下文长度: {{ formatNumber(state.modelB.context_length) }}</span>
            <span>输入价格<span class="price-unit">/M</span>: {{ formatPricePair(state.modelB.pricing.prompt_per_m_usd, state.modelB.pricing.prompt_per_m) }}</span>
            <span>输出价格<span class="price-unit">/M</span>: {{ formatPricePair(state.modelB.pricing.completion_per_m_usd, state.modelB.pricing.completion_per_m) }}</span>
          </template>
        </div>
      </div>
    </div>
  </div>
  <div class="selector-skeleton" v-else>
    <div class="skeleton-card"></div>
    <div class="skeleton-vs">VS</div>
    <div class="skeleton-card"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from "vue";
import { useAppState } from "../composables/useState";
import { useBenchmarks } from "../composables/useBenchmarks";

const state = useAppState();
const { selectModelA, selectModelB, selectModelAById, selectModelBById } = useBenchmarks();

const openA = ref(false);
const openB = ref(false);
const inputA = ref("");
const inputB = ref("");
const triggerA = ref<HTMLElement | null>(null);
const triggerB = ref<HTMLElement | null>(null);
const vsContainer = ref<HTMLElement | null>(null);

let hoverDebounceTimer: ReturnType<typeof setTimeout> | null = null;
let leaveDebounceTimer: ReturnType<typeof setTimeout> | null = null;
let pendingTarget = "";
let wobbleA = 0;
let wobbleVs = 0;
let wobbleB = 0;
let wobbleRaf = 0;
let targetWobbleA = 0;
let targetWobbleVs = 0;
let targetWobbleB = 0;

function onVsMouseMove(e: MouseEvent) {
  const container = vsContainer.value;
  if (!container) return;

  if (leaveDebounceTimer !== null) {
    clearTimeout(leaveDebounceTimer);
    leaveDebounceTimer = null;
  }

  const rect = container.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;
  const children = container.querySelectorAll<HTMLElement>("[data-target]");
  let closest: string | null = null;
  let minDist = Infinity;
  for (const child of children) {
    const cr = child.getBoundingClientRect();
    const cx = cr.left + cr.width / 2 - rect.left;
    const cy = cr.top + cr.height / 2 - rect.top;
    const dist = Math.hypot(x - cx, y - cy);
    if (dist < minDist) {
      minDist = dist;
      closest = child.dataset.target ?? null;
    }
  }

  const target = closest ?? "";

  if (target !== pendingTarget) {
    pendingTarget = target;
    if (hoverDebounceTimer !== null) {
      clearTimeout(hoverDebounceTimer);
    }
    hoverDebounceTimer = setTimeout(() => {
      applySpacerWidths(target);
      container.dataset.hover = target;
      hoverDebounceTimer = null;
    }, 80);
  }

  targetWobbleA = 0;
  targetWobbleVs = 0;
  targetWobbleB = 0;

  if (target === 'a') {
    const el = container.querySelector('[data-target="a"]') as HTMLElement;
    if (el) {
      const cr = el.getBoundingClientRect();
      const cx = cr.left + cr.width / 2 - rect.left;
      targetWobbleA = ((x - cx) / (cr.width / 2)) * 16;
    }
  } else if (target === 'vs') {
    const el = container.querySelector('[data-target="vs"]') as HTMLElement;
    if (el) {
      const cr = el.getBoundingClientRect();
      const cx = cr.left + cr.width / 2 - rect.left;
      targetWobbleVs = ((x - cx) / (cr.width / 2)) * 16;
    }
  } else if (target === 'b') {
    const el = container.querySelector('[data-target="b"]') as HTMLElement;
    if (el) {
      const cr = el.getBoundingClientRect();
      const cx = cr.left + cr.width / 2 - rect.left;
      targetWobbleB = ((x - cx) / (cr.width / 2)) * 16;
    }
  }

  startWobbleAnimation();
}

function startWobbleAnimation() {
  cancelAnimationFrame(wobbleRaf);
  const step = () => {
    let settled = true;
    const lerp = 0.12;

    const diffA = targetWobbleA - wobbleA;
    if (Math.abs(diffA) > 0.05) { wobbleA += diffA * lerp; settled = false; }
    else wobbleA = targetWobbleA;

    const diffVs = targetWobbleVs - wobbleVs;
    if (Math.abs(diffVs) > 0.05) { wobbleVs += diffVs * lerp; settled = false; }
    else wobbleVs = targetWobbleVs;

    const diffB = targetWobbleB - wobbleB;
    if (Math.abs(diffB) > 0.05) { wobbleB += diffB * lerp; settled = false; }
    else wobbleB = targetWobbleB;

    applyWobble();

    if (!settled) {
      wobbleRaf = requestAnimationFrame(step);
    }
  };
  step();
}

function applyWobble() {
  const container = vsContainer.value;
  if (!container) return;
  container.style.setProperty('--wobble-a', `${wobbleA.toFixed(2)}deg`);
  container.style.setProperty('--wobble-vs', `${wobbleVs.toFixed(2)}deg`);
  container.style.setProperty('--wobble-b', `${wobbleB.toFixed(2)}deg`);
}

function onVsMouseLeave() {
  const container = vsContainer.value;
  if (!container) return;

  pendingTarget = "";
  targetWobbleA = 0;
  targetWobbleVs = 0;
  targetWobbleB = 0;

  if (hoverDebounceTimer !== null) {
    clearTimeout(hoverDebounceTimer);
    hoverDebounceTimer = null;
  }

  startWobbleAnimation();

  leaveDebounceTimer = setTimeout(() => {
    if (container) {
      applySpacerWidths("");
      container.dataset.hover = "";
    }
    leaveDebounceTimer = null;
  }, 150);
}

function applySpacerWidths(hover: string) {
  const container = vsContainer.value?.closest('.split-selectors') as HTMLElement;
  if (!container) return;

  const cardA = container.querySelector('.split-card-a') as HTMLElement;
  const cardB = container.querySelector('.split-card-b') as HTMLElement;
  const spacerAEl = container.querySelector('.shrink-spacer-a') as HTMLElement;
  const spacerBEl = container.querySelector('.shrink-spacer-b') as HTMLElement;
  const labelAEl = container.querySelector('.vs-label.a') as HTMLElement;
  const labelBEl = container.querySelector('.vs-label.b') as HTMLElement;
  const dividerEl = container.querySelector('.vs-divider') as HTMLElement;
  const vsEl = container.querySelector('.split-vs') as HTMLElement;

  if (!cardA || !cardB || !spacerAEl || !spacerBEl || !vsEl) return;

  if (!hover) {
    cardA.style.flex = '';
    spacerAEl.style.flex = '';
    cardB.style.flex = '';
    spacerBEl.style.flex = '';
    return;
  }

  const containerWidth = container.getBoundingClientRect().width;
  const vsWidth = vsEl.getBoundingClientRect().width;
  const gapTotal = 40;
  const availableSpace = containerWidth - vsWidth - gapTotal;

  if (availableSpace <= 0) return;

  const w = (el: Element | null) => el ? (el as HTMLElement).offsetWidth : 0;
  const scale = 2;
  const translateOffset = 30;

  let spacerAPx = 0;
  let spacerBPx = 0;

  if (hover === 'a') {
    spacerAPx = w(labelAEl) * (scale - 1);
  } else if (hover === 'b') {
    spacerBPx = w(labelBEl) * (scale - 1);
  } else if (hover === 'vs') {
    const vsExtra = w(dividerEl) * (scale - 1) / 2;
    spacerAPx = vsExtra + translateOffset;
    spacerBPx = vsExtra + translateOffset;
  }

  const maxRatio = 0.25;
  const ratioA = Math.min(spacerAPx / availableSpace, maxRatio);
  const ratioB = Math.min(spacerBPx / availableSpace, maxRatio);

  cardA.style.flex = `${1 - 2 * ratioA}`;
  spacerAEl.style.flex = `${2 * ratioA}`;
  cardB.style.flex = `${1 - 2 * ratioB}`;
  spacerBEl.style.flex = `${2 * ratioB}`;
}

watch(() => state.modelA, (m) => {
  if (m) inputA.value = m.id;
  else inputA.value = "";
}, { immediate: true });

watch(() => state.modelB, (m) => {
  if (m) inputB.value = m.id;
  else inputB.value = "";
}, { immediate: true });

const groupedModels = computed(() => {
  const map = new Map<string, typeof state.models>();
  for (const m of state.models) {
    const list = map.get(m.provider) ?? [];
    list.push(m);
    map.set(m.provider, list);
  }
  return Array.from(map.entries())
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([provider, models]) => ({ provider, models }));
});

function onFocusA() {
  openA.value = true;
}

function onFocusB() {
  openB.value = true;
}

function submitA() {
  const id = inputA.value.trim();
  if (!id) return;
  openA.value = false;
  const existing = state.models.find((m) => m.id === id);
  if (existing) {
    selectModelA(existing);
  } else {
    selectModelAById(id);
  }
}

function submitB() {
  const id = inputB.value.trim();
  if (!id) return;
  openB.value = false;
  const existing = state.models.find((m) => m.id === id);
  if (existing) {
    selectModelB(existing);
  } else {
    selectModelBById(id);
  }
}

function onBlurA() {
  setTimeout(() => {
    if (!openA.value) return;
    openA.value = false;
    submitA();
  }, 150);
}

function onBlurB() {
  setTimeout(() => {
    if (!openB.value) return;
    openB.value = false;
    submitB();
  }, 150);
}

function onEnterA() {
  submitA();
}

function onEnterB() {
  submitB();
}

function pickA(id: string) {
  const m = state.models.find((m) => m.id === id);
  if (m) selectModelA(m);
  openA.value = false;
}

function pickB(id: string) {
  const m = state.models.find((m) => m.id === id);
  if (m) selectModelB(m);
  openB.value = false;
}

function onClickOutside(e: MouseEvent) {
  if (openA.value && triggerA.value && !triggerA.value.contains(e.target as Node)) {
    openA.value = false;
  }
  if (openB.value && triggerB.value && !triggerB.value.contains(e.target as Node)) {
    openB.value = false;
  }
}

onMounted(() => document.addEventListener("click", onClickOutside));
onUnmounted(() => {
  document.removeEventListener("click", onClickOutside);
  if (hoverDebounceTimer !== null) clearTimeout(hoverDebounceTimer);
  if (leaveDebounceTimer !== null) clearTimeout(leaveDebounceTimer);
  cancelAnimationFrame(wobbleRaf);
});

function formatNumber(v: number): string {
  return v.toLocaleString("en-US");
}

function formatDate(unix: number): string {
  if (!unix) return "";
  const d = new Date(unix * 1000);
  return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, "0")}.${String(d.getDate()).padStart(2, "0")}`;
}

function formatPrice(usd: number, cny: number): string {
  const usdStr = usd.toFixed(2);
  const cnyStr = cny.toFixed(2);
  return `${usdStr}$ (${cnyStr}¥)`;
}

function formatPricePair(usd: number, cny: number): string {
  return formatPrice(usd, cny);
}

const indices = computed(() => {
  const a = state.modelA?.aa_indices;
  const b = state.modelB?.aa_indices;
  const pctA = state.modelA?.aa_percentiles;
  const pctB = state.modelB?.aa_percentiles;
  return [
    { key: "intelligence", label: "智能指数", shortLabel: "智能指数", valueA: a?.intelligence ?? null, valueB: b?.intelligence ?? null, max: 70, pctA: pctA?.intelligence_percentile ?? null, pctB: pctB?.intelligence_percentile ?? null },
    { key: "coding", label: "编程指数", shortLabel: "编程指数", valueA: a?.coding ?? null, valueB: b?.coding ?? null, max: 60, pctA: pctA?.coding_percentile ?? null, pctB: pctB?.coding_percentile ?? null },
    { key: "agentic", label: "自主指数", shortLabel: "自主指数", valueA: a?.agentic ?? null, valueB: b?.agentic ?? null, max: 80, pctA: pctA?.agentic_percentile ?? null, pctB: pctB?.agentic_percentile ?? null },
  ];
});

function formatIndexValue(v: number | null): string {
  if (v === null) return "--";
  return v.toFixed(1);
}

function dotPos(idx: { valueA: number | null; valueB: number | null; max: number }): number {
  const a = idx.valueA;
  const b = idx.valueB;
  if (a === null || b === null) return 50;
  const delta = a - b;
  const maxDelta = idx.max * 0.5;
  const offset = (delta / maxDelta) * 50;
  return Math.max(0, Math.min(100, 50 + offset));
}

function dotStyle(idx: { valueA: number | null; valueB: number | null; max: number }): Record<string, string> {
  return { left: `${dotPos(idx)}%` };
}

function dotClass(idx: { valueA: number | null; valueB: number | null }): string {
  const a = idx.valueA;
  const b = idx.valueB;
  if (a === null || b === null) return "";
  if (Math.abs(a - b) < 0.05) return "tied";
  return a > b ? "lead-a" : "lead-b";
}

function barStyleA(idx: { valueA: number | null; valueB: number | null; max: number }): Record<string, string> {
  const pos = dotPos(idx);
  return { width: `${pos}%` };
}

function barStyleB(idx: { valueA: number | null; valueB: number | null; max: number }): Record<string, string> {
  const pos = dotPos(idx);
  return { width: `${100 - pos}%` };
}

interface MetaMetric {
  key: string;
  label: string;
  valueA: number;
  valueB: number;
  displayA: string;
  displayB: string;
  usdA: string | null;
  usdB: string | null;
  higherIsBetter: boolean;
  max: number;
  winner: "a" | "b" | "";
  maxOutputA: number;
  maxOutputB: number;
}

const metaMetrics = computed((): MetaMetric[] => {
  const a = state.modelA;
  const b = state.modelB;
  if (!a || !b) return [];

  const ctxA = a.context_length;
  const ctxB = b.context_length;
  const inA = a.pricing.prompt_per_m_usd;
  const inB = b.pricing.prompt_per_m_usd;
  const outA = a.pricing.completion_per_m_usd;
  const outB = b.pricing.completion_per_m_usd;

  function winner(valA: number, valB: number, higherIsBetter: boolean): "a" | "b" | "" {
    if (Math.abs(valA - valB) < 0.005) return "";
    const aBetter = higherIsBetter ? valA > valB : valA < valB;
    return aBetter ? "a" : "b";
  }

  return [
    {
      key: "ctx",
      label: "上下文长度",
      valueA: ctxA,
      valueB: ctxB,
      displayA: formatCompactNumber(ctxA),
      displayB: formatCompactNumber(ctxB),
      usdA: null,
      usdB: null,
      higherIsBetter: true,
      max: Math.max(ctxA, ctxB, 1) * 2,
      winner: winner(ctxA, ctxB, true),
      maxOutputA: a.max_output ?? 0,
      maxOutputB: b.max_output ?? 0,
    },
    {
      key: "input",
      label: "输入价格",
      valueA: inA,
      valueB: inB,
      displayA: formatCNY(a.pricing.prompt_per_m),
      displayB: formatCNY(b.pricing.prompt_per_m),
      usdA: `${inA.toFixed(2)}$`,
      usdB: `${inB.toFixed(2)}$`,
      higherIsBetter: false,
      max: Math.max(inA, inB, 0.01) * 2,
      winner: winner(inA, inB, false),
      maxOutputA: 0,
      maxOutputB: 0,
    },
    {
      key: "output",
      label: "输出价格",
      valueA: outA,
      valueB: outB,
      displayA: formatCNY(a.pricing.completion_per_m),
      displayB: formatCNY(b.pricing.completion_per_m),
      usdA: `${outA.toFixed(2)}$`,
      usdB: `${outB.toFixed(2)}$`,
      higherIsBetter: false,
      max: Math.max(outA, outB, 0.01) * 2,
      winner: winner(outA, outB, false),
      maxOutputA: 0,
      maxOutputB: 0,
    },
  ];
});

function formatCompactNumber(v: number): string {
  if (v >= 1_000) return `${(v / 1_000).toFixed(1)}K`;
  return v.toLocaleString("en-US");
}

function formatCNY(cny: number): string {
  return cny.toFixed(2);
}

const metaHover = ref<{ key: string; side: string; usd: string | null; mouseX: number } | null>(null);

const idxHover = ref<{ key: string; side: string; text: string | null; mouseX: number } | null>(null);

function onIdxMouseMove(e: MouseEvent, idx: { key: string; valueA: number | null; valueB: number | null; max: number; pctA: number | null; pctB: number | null }) {
  const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
  const x = e.clientX - rect.left;
  const ratio = x / rect.width;
  const pos = dotPos(idx) / 100;
  const side = ratio < pos ? "a" : "b";
  const pct = side === "a" ? idx.pctA : idx.pctB;
  const text = pct !== null ? `领先 ${pct}% 同类模型` : null;
  idxHover.value = { key: idx.key, side, text, mouseX: x };
}

const idxTooltipCache: Record<string, string> = {};

function idxTooltipClass(idx: { key: string }): Record<string, boolean> {
  if (!idxHover.value || idxHover.value.key !== idx.key) return {};
  const side = idxHover.value.side;
  return {
    "tip-visible": !!idxHover.value.text,
    "tip-a": side === "a",
    "tip-b": side === "b",
  };
}

function idxTooltipStyle(idx: { key: string }): Record<string, string> {
  if (!idxHover.value || idxHover.value.key !== idx.key || !idxHover.value.text) {
    const cached = idxTooltipCache[idx.key];
    if (cached) return { left: cached };
    return {};
  }
  const left = `${idxHover.value.mouseX}px`;
  idxTooltipCache[idx.key] = left;
  return { left };
}

function onMetaMouseMove(e: MouseEvent, m: MetaMetric) {
  const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
  const x = e.clientX - rect.left;
  const ratio = x / rect.width;
  const pos = metaDotPos(m) / 100;
  const side = ratio < pos ? "a" : "b";
  const usd = side === "a" ? m.usdA : m.usdB;
  metaHover.value = { key: m.key, side, usd, mouseX: x };
}

function metaTooltipClass(m: MetaMetric): Record<string, boolean> {
  if (!metaHover.value || metaHover.value.key !== m.key) return {};
  const side = metaHover.value.side;
  const visible = m.key === 'ctx' ? true : !!metaHover.value.usd;
  return {
    "tip-visible": visible,
    "tip-a": side === "a",
    "tip-b": side === "b",
  };
}

const metaTooltipCache: Record<string, string> = {};

function metaTooltipStyle(m: MetaMetric): Record<string, string> {
  const hasContent = m.key === 'ctx' ? true : !!metaHover.value?.usd;
  if (!metaHover.value || metaHover.value.key !== m.key || !hasContent) {
    const cached = metaTooltipCache[m.key];
    if (cached) return { left: cached };
    return {};
  }
  const left = `${metaHover.value.mouseX}px`;
  metaTooltipCache[m.key] = left;
  return { left };
}

function metaDotPos(m: MetaMetric): number {
  const a = m.valueA;
  const b = m.valueB;
  if (a === 0 && b === 0) return 50;
  return (a / (a + b)) * 100;
}

function metaDotStyle(m: MetaMetric): Record<string, string> {
  return { left: `${metaDotPos(m)}%` };
}

function metaDotClass(m: MetaMetric): string {
  if (!m.winner) return "tied";
  return `lead-${m.winner}`;
}

function metaBarA(m: MetaMetric): Record<string, string> {
  return { width: `${metaDotPos(m)}%` };
}

function metaBarB(m: MetaMetric): Record<string, string> {
  return { width: `${100 - metaDotPos(m)}%` };
}
</script>

<style scoped>
.selector-area {
  padding: 32px 0 0;
}

.section-label {
  font-size: 12px;
  color: var(--color-text-muted);
  letter-spacing: 2px;
  font-weight: 600;
  margin-bottom: 10px;
}

.split-selectors {
  display: flex;
  align-items: center;
  gap: 10px;
}

.split-card {
  background: var(--color-card-bg);
  border-radius: 12px;
  box-shadow: 0 1px 8px rgba(0, 0, 0, 0.06);
  overflow: visible;
  flex: 1;
  transition: flex 0.5s cubic-bezier(0.25, 1, 0.5, 1);
}

.shrink-spacer {
  flex: 0 0 0px;
  transition: flex 0.5s cubic-bezier(0.25, 1, 0.5, 1);
}

.split-model {
  padding: 12px 16px;
  display: flex;
  align-items: center;
}

.model-info {
  display: none;
}

.model-date {
  font-size: 10px;
  color: #bbb;
  font-family: var(--font-mono);
  letter-spacing: 0.3px;
  margin-left: 8px;
  white-space: nowrap;
  flex-shrink: 0;
}

.chip-link {
  display: inline-flex;
  align-items: center;
  color: #bbb;
  transition: color 0.2s;
  text-decoration: none;
  flex-shrink: 0;
  opacity: 0.5;
}

.chip-link:hover {
  opacity: 1;
}

.chip-a .chip-link:hover {
  color: var(--color-a);
}

.chip-b .chip-link:hover {
  color: var(--color-b);
}

.chip-link svg {
  width: 12px;
  height: 12px;
}

.split-vs {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0 4px;
  flex-shrink: 0;
  position: relative;
  --wobble-a: 0deg;
  --wobble-vs: 0deg;
  --wobble-b: 0deg;
}

.vs-label {
  font-family: Georgia, serif;
  font-size: 80px;
  font-weight: 700;
  font-style: italic;
  line-height: 0.7;
  margin-top: -36px;
  opacity: 0.72;
  text-shadow: 2px 3px 0 rgba(0, 0, 0, 0.05);
  cursor: default;
  position: relative;
  z-index: 1;
  scale: 1;
  transition: scale 0.5s cubic-bezier(0.25, 1, 0.5, 1);
}

.vs-label.a {
  color: var(--color-a);
  transform: rotate(calc(-3deg + var(--wobble-a))) translateY(-5px);
  transform-origin: 40% 60%;
  transition: scale 0.5s cubic-bezier(0.25, 1, 0.5, 1), transform 0.5s cubic-bezier(0.25, 1, 0.5, 1), transform-origin 0.5s cubic-bezier(0.25, 1, 0.5, 1);
}

.split-vs[data-hover="a"] .vs-label.a {
  z-index: 10;
  scale: 2;
  transform-origin: right bottom;
}

.vs-label.b {
  color: var(--color-b);
  transform: rotate(calc(3deg + var(--wobble-b))) translateY(3px);
  transform-origin: 60% 60%;
  transition: scale 0.5s cubic-bezier(0.25, 1, 0.5, 1), transform 0.5s cubic-bezier(0.25, 1, 0.5, 1), transform-origin 0.5s cubic-bezier(0.25, 1, 0.5, 1);
}

.split-vs[data-hover="b"] .vs-label.b {
  z-index: 10;
  scale: 2;
  transform-origin: left bottom;
}

.split-vs[data-hover="vs"] .vs-label.a {
  transform: rotate(calc(-3deg + var(--wobble-a))) translateY(-5px) translateX(-30px);
  transform-origin: right bottom;
}

.split-vs[data-hover="vs"] .vs-label.b {
  transform: rotate(calc(3deg + var(--wobble-b))) translateY(3px) translateX(30px);
  transform-origin: left bottom;
}

.vs-divider {
  font-family: Georgia, serif;
  font-size: 24px;
  font-weight: 700;
  font-style: italic;
  color: var(--color-text-muted);
  letter-spacing: 2px;
  align-self: center;
  transform: rotate(calc(1deg + var(--wobble-vs)));
  text-shadow: 1px 2px 0 rgba(0, 0, 0, 0.04);
  cursor: default;
  position: relative;
  z-index: 1;
  transform-origin: center bottom;
  scale: 1;
  transition: scale 0.5s cubic-bezier(0.25, 1, 0.5, 1);
}

.split-vs[data-hover="vs"] .vs-divider {
  z-index: 10;
  scale: 2;
}

.vs-exclaim {
  position: absolute;
  top: -70px;
  font-family: Georgia, serif;
  font-size: 48px;
  font-weight: 700;
  font-style: italic;
  opacity: 0;
  pointer-events: none;
  z-index: 5;
  color: #bbb;
  transition: opacity 0.4s cubic-bezier(0.25, 1, 0.5, 1), transform 0.5s cubic-bezier(0.25, 1, 0.5, 1);
  transform-origin: center bottom;
}

.exclaim-left {
  left: calc(50% - 22px);
  font-size: 38px;
  top: -60px;
  transform: rotate(-15deg) translateY(10px);
}

.exclaim-right {
  right: calc(50% - 22px);
  font-size: 56px;
  top: -80px;
  transform: rotate(15deg) translateY(10px);
}

.split-vs[data-hover="vs"] .exclaim-left {
  opacity: 0.6;
  transform: rotate(calc(-15deg + var(--wobble-vs))) translateY(0);
  transition-delay: 1s, 0s;
}

.split-vs[data-hover="vs"] .exclaim-right {
  opacity: 0.6;
  transform: rotate(calc(15deg + var(--wobble-vs))) translateY(0);
  transition-delay: 1s, 0s;
}

.model-chip-wrap {
  position: relative;
  flex: 1;
}

.model-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  font-family: var(--font-mono);
  width: 100%;
  transition: all 0.25s;
}

.chip-a {
  background: rgba(111, 163, 167, 0.1);
  color: #5a8e92;
}

.chip-b {
  background: rgba(232, 168, 130, 0.1);
  color: #c4885e;
}

.model-chip input {
  border: none;
  background: transparent;
  font: inherit;
  color: inherit;
  outline: none;
  flex: 1;
  min-width: 0;
}

.model-chip input::placeholder {
  color: rgba(0, 0, 0, 0.25);
  font-family: 'DM Sans', -apple-system, sans-serif;
  font-weight: 400;
}

.chip-toggle {
  background: none;
  border: none;
  cursor: pointer;
  padding: 2px;
  opacity: 0.4;
  transition: opacity 0.2s;
  flex-shrink: 0;
}

.chip-toggle:hover {
  opacity: 0.8;
}

.chip-toggle svg {
  width: 12px;
  height: 12px;
  display: block;
}

.chip-a .chip-toggle svg {
  stroke: var(--color-a);
}

.chip-b .chip-toggle svg {
  stroke: var(--color-b);
}

.select-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  background: var(--color-card-bg);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  z-index: 100;
  max-height: 260px;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: rgba(0, 0, 0, 0.12) transparent;
}

.select-dropdown::-webkit-scrollbar {
  width: 5px;
}

.select-dropdown::-webkit-scrollbar-track {
  background: transparent;
}

.select-dropdown::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.12);
  border-radius: 3px;
}

.select-dropdown::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.2);
}

.select-group-label {
  padding: 10px 12px 2px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 1px;
  color: var(--color-text-muted);
  position: sticky;
  top: 0;
  background: var(--color-card-bg);
  z-index: 1;
}

.dropdown-enter-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}

.dropdown-leave-active {
  transition: opacity 0.12s ease, transform 0.12s ease;
}

.dropdown-enter-from {
  opacity: 0;
  transform: translateY(-6px);
}

.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

.select-option {
  padding: 8px 12px;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.15s;
  color: var(--color-text);
  font-family: var(--font-mono);
}

.select-option:hover {
  background: #f0f1f5;
}

.select-option.active {
  font-weight: 600;
}

.split-a .select-option.active {
  color: var(--color-a);
  background: var(--color-a-bg);
}

.split-b .select-option.active {
  color: var(--color-b);
  background: var(--color-b-bg);
}

.meta-cards {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.meta-cards-single {
  margin-top: 0;
}

.meta-card {
  flex: 1;
  background: var(--color-card-bg);
  border-radius: 12px;
  box-shadow: 0 1px 8px rgba(0, 0, 0, 0.06);
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.mc-label {
  font-size: 10px;
  color: var(--color-text-secondary);
  text-align: center;
  letter-spacing: 0.5px;
  font-weight: 700;
}

.mc-vals {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.mc-val-wrap {
  display: flex;
  align-items: baseline;
  gap: 3px;
}

.mc-val-wrap.a {
  text-align: right;
  justify-content: flex-end;
}

.mc-val-wrap.b {
  text-align: left;
  justify-content: flex-start;
}

.mc-price-main {
  font-family: var(--font-mono);
  font-size: 13px;
  font-weight: 700;
  line-height: 1;
}

.mc-val-wrap.a .mc-price-main {
  color: var(--color-a);
}

.mc-val-wrap.b .mc-price-main {
  color: var(--color-b);
}

.mc-val-wrap.mc-wins .mc-price-main {
  font-weight: 800;
}

.mc-tooltip {
  position: absolute;
  top: -36px;
  padding: 4px 10px;
  background: #fff;
  border-radius: 8px;
  white-space: nowrap;
  pointer-events: none;
  z-index: 10;
  transform: translateX(-50%);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08), 0 0 0 1px rgba(0, 0, 0, 0.04);
  opacity: 0;
  transition: opacity 0.12s ease, left 0.15s ease-out;
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.mc-tooltip.tip-visible {
  opacity: 1;
}

.mc-tooltip.tip-a {
  box-shadow: 0 2px 12px rgba(111, 163, 167, 0.12), 0 0 0 1px rgba(111, 163, 167, 0.15);
}

.mc-tooltip.tip-b {
  box-shadow: 0 2px 12px rgba(232, 168, 130, 0.12), 0 0 0 1px rgba(232, 168, 130, 0.15);
}

.mc-tip-currency {
  font-size: 9px;
  color: #aaa;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.mc-tip-label {
  font-size: 9px;
  color: #aaa;
  font-weight: 600;
  letter-spacing: 0.5px;
  margin-right: 4px;
}

.mc-tip-value {
  font-family: var(--font-mono);
  font-size: 13px;
  font-weight: 700;
  color: #444;
}

.mc-tip-unit {
  font-size: 11px;
  color: #999;
  font-weight: 500;
}

.mc-per-unit {
  font-size: 8px;
  color: #ccc;
  margin-left: 1px;
}

.mc-tooltip.tip-a .mc-tip-value {
  color: var(--color-a);
}

.mc-tooltip.tip-b .mc-tip-value {
  color: var(--color-b);
}

.mc-tooltip::after {
  content: "";
  position: absolute;
  bottom: -4px;
  left: 50%;
  transform: translateX(-50%);
  border-left: 5px solid transparent;
  border-right: 5px solid transparent;
  border-top: 5px solid #fff;
}

.mc-tooltip.tip-a::after {
  border-top-color: #fff;
}

.mc-tooltip.tip-b::after {
  border-top-color: #fff;
}

.mc-chart {
  flex: 1;
  position: relative;
  height: 28px;
  display: flex;
  align-items: center;
}

.mc-center-line {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 1px;
  height: 10px;
  background: #e0e0e8;
}

.mc-bar-a,
.mc-bar-b {
  position: absolute;
  top: 50%;
  height: 6px;
  transform: translateY(-50%);
  transition: height 0.25s cubic-bezier(0.34, 1.56, 0.64, 1), top 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.mc-bar-a {
  left: 0;
  background: rgba(111, 163, 167, 0.3);
  border-radius: 3px 0 0 3px;
}

.mc-bar-b {
  right: 0;
  background: rgba(232, 168, 130, 0.3);
  border-radius: 0 3px 3px 0;
}

.mc-dot {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%) scale(1);
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--color-card-bg);
  z-index: 1;
  transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
  border: 2px solid #bbb;
}

.mc-dot.lead-a {
  border-color: var(--color-a);
}

.mc-dot.lead-b {
  border-color: var(--color-b);
}

.mc-dot.tied {
  border-color: #ccc;
}

.mc-dot-hover {
  transform: translate(-50%, -50%) scale(1.6);
}

.mc-chart[data-side="a"] .mc-bar-a {
  height: 10px;
  top: calc(50% - 2px);
}

.mc-chart[data-side="b"] .mc-bar-b {
  height: 10px;
  top: calc(50% - 2px);
}

.index-cards {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.index-card {
  flex: 1;
  background: var(--color-card-bg);
  border-radius: 12px;
  box-shadow: 0 1px 8px rgba(0, 0, 0, 0.06);
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.ic-label {
  font-size: 10px;
  color: var(--color-text-secondary);
  text-align: center;
  letter-spacing: 0.5px;
  font-weight: 700;
}

.ic-vals {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.ic-val {
  font-family: var(--font-mono);
  font-size: 13px;
  font-weight: 700;
  line-height: 1;
}

.ic-val.a {
  color: var(--color-a);
  text-align: right;
}

.ic-val.b {
  color: var(--color-b);
  text-align: left;
}

.ic-chart {
  flex: 1;
  position: relative;
  height: 28px;
  display: flex;
  align-items: center;
}

.ic-center-line {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 1px;
  height: 10px;
  background: #e0e0e8;
}

.ic-bar-a,
.ic-bar-b {
  position: absolute;
  top: 50%;
  height: 6px;
  transform: translateY(-50%);
  transition: height 0.25s cubic-bezier(0.34, 1.56, 0.64, 1), top 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.ic-bar-a {
  left: 0;
  background: rgba(111, 163, 167, 0.3);
  border-radius: 3px 0 0 3px;
}

.ic-bar-b {
  right: 0;
  background: rgba(232, 168, 130, 0.3);
  border-radius: 0 3px 3px 0;
}

.ic-dot {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%) scale(1);
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--color-card-bg);
  z-index: 1;
  border: 2px solid #bbb;
  transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.ic-dot.lead-a {
  border-color: var(--color-a);
}

.ic-dot.lead-b {
  border-color: var(--color-b);
}

.ic-dot.tied {
  border-color: #ccc;
}

.ic-dot-hover {
  transform: translate(-50%, -50%) scale(1.6);
}

.ic-chart[data-side="a"] .ic-bar-a {
  height: 10px;
  top: calc(50% - 2px);
}

.ic-chart[data-side="b"] .ic-bar-b {
  height: 10px;
  top: calc(50% - 2px);
}

.ic-tooltip {
  position: absolute;
  top: -36px;
  padding: 4px 10px;
  background: #fff;
  border-radius: 8px;
  white-space: nowrap;
  pointer-events: none;
  z-index: 10;
  transform: translateX(-50%);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08), 0 0 0 1px rgba(0, 0, 0, 0.04);
  opacity: 0;
  transition: opacity 0.12s ease, left 0.15s ease-out;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ic-tooltip.tip-visible {
  opacity: 1;
}

.ic-tooltip.tip-a {
  box-shadow: 0 2px 12px rgba(111, 163, 167, 0.12), 0 0 0 1px rgba(111, 163, 167, 0.15);
}

.ic-tooltip.tip-b {
  box-shadow: 0 2px 12px rgba(232, 168, 130, 0.12), 0 0 0 1px rgba(232, 168, 130, 0.15);
}

.ic-tip-text {
  font-size: 11px;
  font-weight: 600;
  color: #666;
}

.ic-tooltip.tip-a .ic-tip-text {
  color: var(--color-a);
}

.ic-tooltip.tip-b .ic-tip-text {
  color: var(--color-b);
}

.ic-tooltip::after {
  content: "";
  position: absolute;
  bottom: -4px;
  left: 50%;
  transform: translateX(-50%);
  border-left: 5px solid transparent;
  border-right: 5px solid transparent;
  border-top: 5px solid #fff;
}

.selector-skeleton {
  padding: 20px 0 0;
  display: flex;
  gap: 20px;
  align-items: center;
}

.skeleton-card {
  flex: 1;
  height: 80px;
  background: linear-gradient(90deg, #eee 25%, #f5f5f5 50%, #eee 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 12px;
}

.skeleton-vs {
  width: 44px;
  text-align: center;
  color: var(--color-text-muted);
  font-family: Georgia, serif;
  font-weight: 700;
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

.price-unit {
  font-size: 0.7em;
  color: #ccc;
}
</style>
