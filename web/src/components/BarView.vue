<template>
  <div class="chart-container">
    <v-chart :option="chartOption" :init-options="{ renderer: 'svg' }" autoresize />
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import VChart from "vue-echarts";
import { useAppState } from "../composables/useState";
import { BENCHMARK_DESCRIPTIONS, BENCHMARK_LABELS } from "../types";
import "echarts";

const state = useAppState();

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

const CATEGORY_ORDER = ["推理", "知识", "编程"];

function modelDisplayName(m: { name: string } | null | undefined): string {
  if (!m) return "A";
  const idx = m.name.indexOf(": ");
  return idx !== -1 ? m.name.slice(idx + 2) : m.name;
}

const chartOption = computed(() => {
  const a = state.modelA?.benchmarks ?? {};
  const b = state.modelB?.benchmarks ?? {};
  const rawKeys = Object.keys(a).length >= Object.keys(b).length ? Object.keys(a) : Object.keys(b);
  const allKeys: string[] = [];
  let firstCat = true;
  for (const cat of CATEGORY_ORDER) {
    const catKeys = rawKeys.filter(k => (BENCHMARK_CATEGORIES[k] ?? "其他") === cat);
    if (catKeys.length === 0) continue;
    if (!firstCat) allKeys.push("");
    for (const k of catKeys) allKeys.push(k);
    firstCat = false;
  }
  const otherKeys = rawKeys.filter(k => !BENCHMARK_CATEGORIES[k]);
  if (otherKeys.length > 0) {
    if (!firstCat) allKeys.push("");
    for (const k of otherKeys) allKeys.push(k);
  }

  const nameA = modelDisplayName(state.modelA);
  const nameB = modelDisplayName(state.modelB);

  return {
    tooltip: {
      trigger: "axis",
      axisPointer: { type: "shadow" },
      extraCssText: "max-width:280px;white-space:normal;word-break:break-all;",
      formatter: (params: any[]) => {
        const idx = params[0]?.dataIndex ?? 0;
        const key = allKeys[idx];
        if (!key) return "";
        const label = BENCHMARK_LABELS[key] ?? key;
        const desc = BENCHMARK_DESCRIPTIONS[key];
        let html = `<div style="font-weight:600;font-size:10px;color:#333;line-height:1.4;white-space:nowrap">${key}</div><div style="font-weight:400;font-size:9px;color:#bbb;line-height:1.4;white-space:nowrap">${label}</div>`;
        if (desc) html += `<div style="font-size:12px;color:#888;line-height:1.7;margin-top:4px">${desc}</div>`;
        for (const p of params) {
          html += `<div style="font-size:12px;line-height:1.6">${p.marker} ${p.seriesName}: <b>${p.value.toFixed(1)}%</b></div>`;
        }
        return html;
      },
    },
    legend: { data: [nameA, nameB], left: 0, top: 0, textStyle: { fontSize: 11 } },
    grid: { left: 180, right: 40, top: 30, bottom: 40 },
    xAxis: { type: "value", axisLabel: { fontSize: 10 } },
    yAxis: {
      type: "category",
      data: allKeys.map((k) => k),
      axisLabel: {
        fontSize: 10,
        rich: {
          en: { fontSize: 9, color: "#333", fontWeight: 600, lineHeight: 16 },
          zh: { fontSize: 8, color: "#bbb", lineHeight: 14 },
        },
        formatter: (val: string) => {
          if (!val) return " ";
          return `{en|${val}}\n{zh|${BENCHMARK_LABELS[val] ?? val}}`;
        },
      },
    },
    series: [
      {
        name: nameA,
        type: "bar",
        data: allKeys.map((k) => k ? (a[k] ?? 0) : null),
        itemStyle: {
          color: "rgba(111, 163, 167, 0.6)",
          borderRadius: [0, 4, 4, 0],
        },
        barWidth: 18,
        barGap: "-100%",
      },
      {
        name: nameB,
        type: "bar",
        data: allKeys.map((k) => k ? (b[k] ?? 0) : null),
        itemStyle: {
          color: "rgba(232, 168, 130, 0.6)",
          borderRadius: [0, 4, 4, 0],
        },
        barWidth: 18,
      },
    ],
  };
});
</script>

<style scoped>
.chart-container {
  background: var(--color-card-bg);
  border-radius: 10px;
  border: 1px solid var(--color-border);
  padding: 16px;
  margin-top: 16px;
}

.chart-container :deep(.echarts) {
  width: 100%;
  height: 500px;
}
</style>
