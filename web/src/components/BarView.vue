<template>
  <div class="chart-container">
    <v-chart
      :option="chartOption"
      :init-options="{ renderer: 'svg' }"
      autoresize
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import VChart from "vue-echarts";
import { useAppState } from "../composables/useState";
import { BENCHMARK_DESCRIPTIONS, BENCHMARK_LABELS } from "../types";
import "echarts";

const state = useAppState();

const BENCHMARK_ORDER = [
  "AA-Omniscience Non-Hallucination Rate",
  "AA-Omniscience Accuracy",
  "Terminal-Bench Hard",
  "SciCode",
  "CritPt",
  "GDPval-AA",
  "AA-LCR",
  "τ²-Bench Telecom",
  "IFBench",
  "HLE",
  "GPQA Diamond",
];

function modelDisplayName(m: { name: string } | null | undefined): string {
  if (!m) return "A";
  const idx = m.name.indexOf(": ");
  return idx !== -1 ? m.name.slice(idx + 2) : m.name;
}

const chartOption = computed(() => {
  const a = state.modelA?.benchmarks ?? {};
  const b = state.modelB?.benchmarks ?? {};
  const allKeySet = new Set([...Object.keys(a), ...Object.keys(b)]);
  const allKeys = BENCHMARK_ORDER.filter(k => allKeySet.has(k));
  const remaining = Array.from(allKeySet).filter(k => !BENCHMARK_ORDER.includes(k));
  for (const k of remaining) allKeys.push(k);

  const nameA = modelDisplayName(state.modelA);
  const nameB = modelDisplayName(state.modelB);

  return {
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#fff',
      borderColor: 'transparent',
      borderRadius: 8,
      borderWidth: 0,
      padding: [10, 14],
      extraCssText: 'box-shadow:0 4px 16px rgba(0,0,0,0.1),0 0 0 1px rgba(0,0,0,0.04);border-radius:8px',
      formatter: (params: any) => {
        if (!params || !params.length) return '';
        const p = params[0];
        const key = p.axisValue;
        const label = BENCHMARK_LABELS[key] ?? key;
        const desc = BENCHMARK_DESCRIPTIONS[key];
        const va = a[key] ?? 0;
        const vb = b[key] ?? 0;
        const rectA = '<span style="display:inline-block;width:14px;height:8px;border-radius:2px;background:rgba(111,163,167,0.6);vertical-align:middle;margin-right:6px"></span>';
        const rectB = '<span style="display:inline-block;width:14px;height:8px;border-radius:2px;background:rgba(232,168,130,0.6);vertical-align:middle;margin-right:6px"></span>';
        let html = `<div style="max-width:400px;white-space:normal;font-family:Consolas,Courier New,monospace">`;
        html += `<div style="font-weight:600;font-size:10px;color:#333;line-height:1.4;white-space:nowrap">${key}</div>`;
        if (label !== key) html += `<div style="font-weight:400;font-size:9px;color:#bbb;line-height:1.4;white-space:nowrap">${label}</div>`;
        if (desc) html += `<div style="font-size:12px;color:#888;line-height:1.7;margin-top:4px;word-break:break-word;white-space:normal">${desc}</div>`;
        html += `<div style="margin-top:6px;border-top:1px solid #f0f0f0;padding-top:6px;white-space:nowrap">`;
        html += `<div style="font-size:12px;line-height:1.7;color:#888;white-space:nowrap">${rectA}${nameA} <b style="color:#333">${va.toFixed(1)}%</b></div>`;
        html += `<div style="font-size:12px;line-height:1.7;color:#888;white-space:nowrap">${rectB}${nameB} <b style="color:#333">${vb.toFixed(1)}%</b></div>`;
        html += `</div></div>`;
        return html;
      },
    },
    legend: { data: [nameA, nameB], left: 0, bottom: 0, textStyle: { fontSize: 11, fontFamily: "Consolas" } },
    grid: { left: 250, right: 40, top: 16, bottom: 50 },
    xAxis: { type: "value", min: 0, axisLabel: { fontSize: 10, fontFamily: "Consolas" } },
    yAxis: {
      type: "category",
      data: allKeys.map((k) => k),
      axisLabel: {
        fontSize: 11,
        fontFamily: "Consolas",
        rich: {
          en: { fontSize: 11, color: "#333", fontWeight: 600, lineHeight: 16, fontFamily: "Consolas" },
          zh: { fontSize: 11, color: "#bbb", lineHeight: 14, fontFamily: "Consolas" },
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
  position: relative;
}

.chart-container :deep(.echarts) {
  width: 100%;
  height: 600px;
}
</style>
