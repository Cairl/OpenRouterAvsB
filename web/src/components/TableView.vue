<template>
  <div class="table-cards">
    <div class="table-card" v-for="cat in categories" :key="cat.name">
      <table>
        <thead>
          <tr>
            <th class="cat-title">
              <span class="cat-text">{{ cat.name }} {{ CATEGORY_EN[cat.name] ?? '' }}</span>
            </th>
            <th class="color-a"><span class="th-swatch-wrap"><span class="model-swatch a"></span>A</span></th>
            <th class="color-b"><span class="th-swatch-wrap"><span class="model-swatch b"></span>B</span></th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in cat.rows" :key="row.key">
            <td>
              <div class="benchmark-name">
                <div class="benchmark-en">
                  {{ row.key }}
                  <span
                    class="info-icon"
                    @mouseenter="onInfoEnter($event, row.key)"
                    @mousemove="onInfoMove($event)"
                    @mouseleave="onInfoLeave"
                  >
                    <svg viewBox="0 0 14 14" fill="none"><circle cx="7" cy="7" r="5.5" stroke="currentColor" stroke-width="1.2"/><path d="M7 6v4M7 4.5v-.2" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>
                  </span>
                </div>
                <div class="benchmark-zh">{{ row.label }}</div>
              </div>
              <span class="inverted-tag" v-if="row.inverted">越低越好</span>
            </td>
            <td :class="['value-cell', { highlight: row.winner === 'a' }, { dim: row.winner && row.winner !== 'a' && row.winner !== 'tie' }]">
              {{ formatVal(row.valueA) }}
            </td>
            <td :class="['value-cell', { highlight: row.winner === 'b' }, { dim: row.winner && row.winner !== 'b' && row.winner !== 'tie' }]">
              {{ formatVal(row.valueB) }}
            </td>
            <td :class="['delta', row.deltaColor]">
              {{ formatDelta(row.delta) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <Teleport to="body">
      <div
        class="bench-tooltip"
        :class="{ visible: infoVisible }"
        :style="infoStyle"
      v-html="infoHtml"></div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useAppState } from "../composables/useState";
import { BENCHMARK_LABELS, BENCHMARK_DESCRIPTIONS } from "../types";

const props = defineProps<{
  category?: string;
  excludeCategory?: string;
}>();

const state = useAppState();

const INVERTED_KEYS = new Set(["AA-Omniscience Hallucination Rate"]);

const BENCHMARK_CATEGORIES: Record<string, string> = {
  "GPQA Diamond": "推理",
  "HLE": "推理",
  "IFBench": "推理",
  "τ²-Bench Telecom": "推理",
  "AA-LCR": "推理",
  "GDPval-AA": "推理",
  "CritPt": "推理",
  "SciCode": "编程",
  "Terminal-Bench Hard": "编程",
  "AA-Omniscience Accuracy": "知识",
  "AA-Omniscience Non-Hallucination Rate": "知识",
  "AA-Omniscience Hallucination Rate": "知识",
};

const CATEGORY_EN: Record<string, string> = {
  "推理": "REASONING",
  "编程": "CODING",
  "知识": "KNOWLEDGE",
  "其他": "OTHER",
};

const categoryOrder = ["编程", "推理", "知识"];

interface TableRow {
  key: string;
  label: string;
  inverted: boolean;
  valueA: number | null;
  valueB: number | null;
  delta: number | null;
  deltaColor: string;
  winner: "a" | "b" | "tie" | null;
}

interface CategoryGroup {
  name: string;
  rows: TableRow[];
}

const categories = computed<CategoryGroup[]>(() => {
  const a = state.modelA?.benchmarks ?? {};
  const b = state.modelB?.benchmarks ?? {};
  const allKeys = new Set([...Object.keys(a), ...Object.keys(b)]);

  const grouped: Record<string, TableRow[]> = {};
  for (const cat of [...categoryOrder, "其他"]) {
    grouped[cat] = [];
  }

  for (const key of allKeys) {
    const label = BENCHMARK_LABELS[key] ?? key;
    const va = a[key] ?? null;
    const vb = b[key] ?? null;
    const inverted = INVERTED_KEYS.has(key);

    let delta: number | null = null;
    let deltaColor = "";
    let winner: "a" | "b" | "tie" | null = null;

    if (va !== null && vb !== null) {
      delta = Math.abs(va - vb);
      if (delta < 0.01) {
        deltaColor = "";
        winner = "tie";
      } else if (inverted) {
        winner = va < vb ? "a" : "b";
        deltaColor = winner === "a" ? "color-a" : "color-b";
      } else {
        winner = va > vb ? "a" : "b";
        deltaColor = winner === "a" ? "color-a" : "color-b";
      }
    }

    const category = BENCHMARK_CATEGORIES[key] ?? "其他";

    grouped[category].push({
      key,
      label,
      inverted,
      valueA: va,
      valueB: vb,
      delta,
      deltaColor,
      winner,
    });
  }

  const result: CategoryGroup[] = [];
  for (const cat of [...categoryOrder, "其他"]) {
    const items = grouped[cat];
    if (items.length === 0) continue;
    if (props.category && cat !== props.category) continue;
    if (props.excludeCategory && cat === props.excludeCategory) continue;
    result.push({ name: cat, rows: items });
  }

  return result;
});

function formatVal(v: number | null): string {
  if (v === null) return "--";
  return `${v.toFixed(1)}%`;
}

function formatDelta(d: number | null): string {
  if (d === null) return "--";
  return `+${d.toFixed(1)}`;
}

const infoVisible = ref(false);
const infoText = ref("");
const infoKey = ref("");
const infoHtml = computed(() => {
  if (!infoText.value && !infoKey.value) return "";
  const key = infoKey.value;
  const colonIdx = infoText.value.indexOf("：");
  const desc = colonIdx !== -1 ? infoText.value.slice(colonIdx + 1) : "";
  const zhLabel = colonIdx !== -1 ? infoText.value.slice(0, colonIdx) : infoText.value;
  let html = `<div style="font-weight:600;font-size:10px;color:#333;line-height:1.4;white-space:nowrap">${key}</div>`;
  if (zhLabel && zhLabel !== key) {
    html += `<div style="font-weight:400;font-size:9px;color:#bbb;line-height:1.4;white-space:nowrap">${zhLabel}</div>`;
  }
  if (desc) {
    html += `<div style="font-size:12px;color:#888;line-height:1.7;margin-top:4px">${desc}</div>`;
  }
  return html;
});
const infoStyle = ref<Record<string, string>>({});
let infoLeaveTimer: ReturnType<typeof setTimeout> | null = null;

function onInfoEnter(e: MouseEvent, key: string) {
  if (infoLeaveTimer) {
    clearTimeout(infoLeaveTimer);
    infoLeaveTimer = null;
  }
  infoKey.value = key;
  const zhLabel = BENCHMARK_LABELS[key] ?? "";
  const desc = BENCHMARK_DESCRIPTIONS[key] ?? "";
  infoText.value = desc ? `${zhLabel}：${desc}` : zhLabel;
  infoVisible.value = true;
  updateInfoPos(e);
}

function onInfoMove(e: MouseEvent) {
  updateInfoPos(e);
}

function onInfoLeave() {
  infoLeaveTimer = setTimeout(() => {
    infoVisible.value = false;
  }, 150);
}

function updateInfoPos(e: MouseEvent) {
  infoStyle.value = {
    left: `${e.clientX + 14}px`,
    top: `${e.clientY - 12}px`,
  };
}
</script>

<style scoped>
.table-cards {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.table-card {
  background: var(--color-card-bg);
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid var(--color-border);
}

.cat-text {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 2px;
  color: #aaa;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
  table-layout: fixed;
}

th {
  padding: 10px 16px;
  text-align: center;
  font-weight: 600;
  letter-spacing: 0.5px;
  font-size: 10px;
  color: #999;
  border-bottom: 1px dashed #e0e0e0;
  white-space: nowrap;
}

th.cat-title {
  text-align: left;
  width: 46%;
}

th:nth-child(2),
th:nth-child(3) {
  width: 18%;
}

th:nth-child(4) {
  width: 18%;
}

th.color-a {
  color: var(--color-a);
}

th.color-b {
  color: var(--color-b);
}

.th-swatch-wrap {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.model-swatch {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 3px;
  vertical-align: middle;
}

.model-swatch.a {
  background: var(--color-a);
}

.model-swatch.b {
  background: var(--color-b);
}

td {
  padding: 9px 16px;
  border-bottom: 1px dashed #f0f0f0;
}

tr:last-child td {
  border-bottom: none;
}

td:first-child {
  font-weight: 500;
  color: var(--color-text);
  font-size: 11px;
}

.benchmark-name {
  display: inline-block;
  vertical-align: middle;
  white-space: nowrap;
}

.benchmark-en {
  font-weight: 600;
  font-size: 10px;
  color: var(--color-text);
  line-height: 1.4;
  white-space: nowrap;
}

.benchmark-zh {
  font-weight: 400;
  font-size: 9px;
  color: #bbb;
  line-height: 1.4;
  white-space: nowrap;
}

td:nth-child(2),
td:nth-child(3) {
  width: 18%;
}

td:nth-child(4) {
  width: 18%;
}

.inverted-tag {
  font-size: 9px;
  color: var(--color-negative);
  background: rgba(220, 38, 38, 0.08);
  padding: 1px 5px;
  border-radius: 3px;
  margin-left: 4px;
}

.value-cell {
  text-align: center;
  color: #bbb;
  font-family: var(--font-mono);
  font-size: 11px;
}

.value-cell.dim {
}

.value-cell.highlight {
  font-weight: 700;
  color: var(--color-a);
  background: var(--color-a-bg);
  padding: 2px 8px;
  border-radius: 4px;
  opacity: 1;
}

td:nth-child(3).highlight {
  color: var(--color-b);
  background: var(--color-b-bg);
}

.delta {
  text-align: center;
  font-weight: 600;
  font-family: var(--font-mono);
  font-size: 11px;
  color: #bbb;
}

.delta.color-a {
  color: var(--color-a);
}

.delta.color-b {
  color: var(--color-b);
}

.info-icon {
  display: inline-flex;
  align-items: center;
  vertical-align: middle;
  cursor: pointer;
  opacity: 0.3;
  transition: opacity 0.15s;
  margin-left: 2px;
}

.info-icon svg {
  width: 12px;
  height: 12px;
  color: #999;
}

.info-icon:hover {
  opacity: 0.7;
}

.bench-tooltip {
  position: fixed;
  z-index: 1000;
  max-width: 400px;
  padding: 10px 14px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1), 0 0 0 1px rgba(0, 0, 0, 0.04);
  font-size: 12px;
  line-height: 1.7;
  color: #888;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.12s ease, left 0.15s ease-out, top 0.15s ease-out;
}

.bench-tooltip.visible {
  opacity: 1;
}
</style>
