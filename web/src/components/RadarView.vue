<template>
  <div class="chart-container" ref="containerRef">
    <v-chart
      ref="chartRef"
      :option="chartOption"
      :init-options="{ renderer: 'svg' }"
      autoresize
      @init="onChartInit"
    />
    <div
      class="radar-tooltip"
      v-if="tooltipData"
      :style="{ left: tooltipX + 'px', top: tooltipY + 'px' }"
    >
      <div class="tooltip-label">{{ tooltipData.label }}</div>
      <div class="tooltip-desc" v-if="tooltipData.desc">{{ tooltipData.desc }}</div>
      <div class="tooltip-row">{{ nameA }}: <b>{{ tooltipData.va }}</b></div>
      <div class="tooltip-row">{{ nameB }}: <b>{{ tooltipData.vb }}</b></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import VChart from "vue-echarts";
import { useAppState } from "../composables/useState";
import { BENCHMARK_DESCRIPTIONS, BENCHMARK_LABELS } from "../types";
import "echarts";

const state = useAppState();

const chartRef = ref();
const containerRef = ref<HTMLElement | null>(null);
const tooltipData = ref<{ label: string; desc: string; va: string; vb: string } | null>(null);
const tooltipX = ref(0);
const tooltipY = ref(0);

let chartInstance: any = null;

function modelDisplayName(m: { name: string } | null | undefined): string {
  if (!m) return "A";
  const idx = m.name.indexOf(": ");
  return idx !== -1 ? m.name.slice(idx + 2) : m.name;
}

function onChartInit(instance: any) {
  chartInstance = instance;
  instance.getZr().on("mousemove", onZrMouseMove);
  instance.getZr().on("mouseout", () => {
    tooltipData.value = null;
  });
}

function onZrMouseMove(e: any) {
  if (!chartInstance || !containerRef.value) return;
  const x = e.offsetX ?? e.event?.offsetX ?? 0;
  const y = e.offsetY ?? e.event?.offsetY ?? 0;

  const globalPt = chartInstance.convertFromPixel({ seriesIndex: 0 }, [x, y]);
  if (!globalPt) {
    tooltipData.value = null;
    return;
  }

  const [gx, gy] = globalPt as number[];
  const cx = chartInstance.getWidth() * 0.5;
  const cy = chartInstance.getHeight() * 0.54;
  const radius = Math.min(chartInstance.getWidth(), chartInstance.getHeight()) * 0.6;

  const dx = gx - cx;
  const dy = gy - cy;
  const dist = Math.sqrt(dx * dx + dy * dy);

  if (dist < radius * 0.15) {
    tooltipData.value = null;
    return;
  }

  const angle = Math.atan2(dy, dx);
  const normalizedAngle = ((angle + Math.PI * 2) % (Math.PI * 2));
  const sectorAngle = (Math.PI * 2) / BENCHMARK_INDICATORS.length;
  const startOffset = -Math.PI / 2;
  let adjustedAngle = normalizedAngle - startOffset;
  if (adjustedAngle < 0) adjustedAngle += Math.PI * 2;

  const idx = Math.floor(adjustedAngle / sectorAngle) % BENCHMARK_INDICATORS.length;

  const a = state.modelA?.benchmarks ?? {};
  const b = state.modelB?.benchmarks ?? {};
  const key = BENCHMARK_INDICATORS[idx].key;
  const label = BENCHMARK_LABELS[key] ?? key;
  const desc = BENCHMARK_DESCRIPTIONS[key] ?? "";
  const va = key ? (a[key] ?? 0) : 0;
  const vb = key ? (b[key] ?? 0) : 0;

  tooltipData.value = {
    label,
    desc,
    va: `${va.toFixed(1)}%`,
    vb: `${vb.toFixed(1)}%`,
  };
  tooltipX.value = x + 12;
  tooltipY.value = y - 10;
}

const BENCHMARK_INDICATORS = [
  { key: "GPQA Diamond", max: 100 },
  { key: "HLE", max: 50 },
  { key: "SciCode", max: 60 },
  { key: "Terminal-Bench Hard", max: 70 },
  { key: "AA-LCR", max: 100 },
  { key: "IFBench", max: 100 },
  { key: "GDPval-AA", max: 70 },
  { key: "τ²-Bench Telecom", max: 100 },
];

const N = BENCHMARK_INDICATORS.length;
const AREA_FACTOR = 0.5 * Math.sin((2 * Math.PI) / N);

function computeRadarArea(values: number[]): number {
  let sum = 0;
  for (let i = 0; i < N; i++) {
    const a = Math.min(values[i] / BENCHMARK_INDICATORS[i].max, 1);
    const b = Math.min(values[(i + 1) % N] / BENCHMARK_INDICATORS[(i + 1) % N].max, 1);
    sum += a * b;
  }
  return AREA_FACTOR * sum;
}

const chartOption = computed(() => {
  const a = state.modelA?.benchmarks ?? {};
  const b = state.modelB?.benchmarks ?? {};

  const nameA = modelDisplayName(state.modelA);
  const nameB = modelDisplayName(state.modelB);

  const valsA = BENCHMARK_INDICATORS.map((ind) => a[ind.key] ?? 0);
  const valsB = BENCHMARK_INDICATORS.map((ind) => b[ind.key] ?? 0);
  const areaA = computeRadarArea(valsA);
  const areaB = computeRadarArea(valsB);
  const aLeads = areaA >= areaB;
  const lead = aLeads ? areaA - areaB : areaB - areaA;
  const leadName = aLeads ? nameA : nameB;

  return {
    tooltip: { show: false },
    title: {
      text: `{swatch| } ${leadName} 多维能力覆盖面积领先 ${(lead * 100).toFixed(1)}%`,
      right: 10,
      top: 6,
      textStyle: {
        fontSize: 12,
        color: "#555",
        fontWeight: "normal",
        fontFamily: "'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        rich: {
          swatch: {
            width: 14,
            height: 14,
            backgroundColor: aLeads ? '#6fa3a7' : '#e8a882',
            borderRadius: 3,
            padding: [0, 0, 0, 0],
            verticalAlign: "middle",
          },
        },
      },
    },
    legend: {
      data: [nameA, nameB],
      left: 0,
      bottom: 0,
      itemWidth: 14,
      itemHeight: 14,
      icon: "roundRect",
      textStyle: { fontSize: 11, fontFamily: "'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" },
    },
    radar: {
      indicator: BENCHMARK_INDICATORS.map((ind) => ({
        name: BENCHMARK_LABELS[ind.key] ?? ind.key,
        max: ind.max,
      })),
      shape: "polygon",
      splitNumber: 5,
      center: ["50%", "54%"],
      radius: "60%",
      axisName: { fontSize: 10, color: "#666", fontFamily: "'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" },
    },
    series: [
      {
        type: "radar",
        emphasis: {
          focus: "self",
          itemStyle: { borderWidth: 3 },
          lineStyle: { width: 3 },
        },
        data: [
          {
            value: valsA,
            name: nameA,
            areaStyle: { color: "rgba(111, 163, 167, 0.15)" },
            lineStyle: { color: "#6fa3a7", width: 1.5 },
            itemStyle: { color: "#6fa3a7" },
            emphasis: {
              areaStyle: { color: "rgba(111, 163, 167, 0.25)" },
              scale: true,
              scaleSize: 6,
            },
          },
          {
            value: valsB,
            name: nameB,
            areaStyle: { color: "rgba(232, 168, 130, 0.15)" },
            lineStyle: { color: "#e8a882", width: 1.5 },
            itemStyle: { color: "#e8a882" },
            emphasis: {
              areaStyle: { color: "rgba(232, 168, 130, 0.25)" },
              scale: true,
              scaleSize: 6,
            },
          },
        ],
      },
    ],
  };
});

const nameA = computed(() => modelDisplayName(state.modelA));
const nameB = computed(() => modelDisplayName(state.modelB));
</script>

<style scoped>
.chart-container {
  background: var(--color-card-bg);
  border-radius: 10px;
  border: 1px solid var(--color-border);
  padding: 16px;
  position: relative;
}

.chart-container :deep(.echarts) {
  width: 100%;
  height: 100%;
  min-height: 280px;
}

.radar-tooltip {
  position: absolute;
  z-index: 20;
  pointer-events: none;
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 8px 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
  font-size: 12px;
  max-width: 240px;
  transform: translate(-50%, -100%);
}

.tooltip-label {
  font-weight: 700;
  font-size: 13px;
  margin-bottom: 2px;
  color: #1a1a2e;
}

.tooltip-desc {
  font-size: 11px;
  color: #888;
  margin-bottom: 8px;
}

.tooltip-row {
  font-size: 12px;
  line-height: 1.6;
  font-family: var(--font-mono);
}
</style>