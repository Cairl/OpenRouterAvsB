<template>
  <div class="content-section" v-if="!state.loading && state.modelA && state.modelB">
    <div class="section-label"><span class="sl-zh">基准测试</span><span class="sl-en">BENCHMARKS</span></div>
    <div class="compare-row">
      <div class="compare-left">
        <TableView category="推理" />
        <TableView category="知识" />
      </div>
      <div class="compare-right">
        <TableView category="编程" />
        <RadarView />
      </div>
    </div>
    <BarView />
  </div>
  <div class="content-section content-section-empty" v-else-if="state.loading">
    <div class="section-label"><span class="sl-zh">基准测试</span><span class="sl-en">BENCHMARKS</span></div>
    <div class="compare-row">
      <div class="compare-left">
        <div class="empty-card"></div>
        <div class="empty-card"></div>
      </div>
      <div class="compare-right">
        <div class="empty-card"></div>
        <div class="empty-card empty-card-radar"></div>
      </div>
    </div>
    <div class="empty-card empty-card-bar"></div>
  </div>
</template>

<script setup lang="ts">
import { useAppState } from "../composables/useState";
import TableView from "./TableView.vue";
import RadarView from "./RadarView.vue";
import BarView from "./BarView.vue";

const state = useAppState();
</script>

<style scoped>
.content-section,
.content-section-empty {
  padding: 0 0 20px;
}

.compare-row {
  display: flex;
  gap: 16px;
  align-items: stretch;
}

.compare-left,
.compare-right {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.compare-right :deep(.chart-container) {
  flex: 1;
  min-height: 0;
}

.section-label {
  font-size: 20px;
  letter-spacing: 2px;
  font-weight: 700;
  margin-top: 48px;
  margin-bottom: 20px;
  display: inline-flex;
  align-items: baseline;
  gap: 8px;
}

.sl-zh {
  color: #777;
  font-weight: 700;
}

.sl-en {
  color: var(--color-text-muted);
  font-weight: 700;
  font-size: 16px;
  letter-spacing: 3px;
}

.content-section-empty {
  opacity: 0.45;
  pointer-events: none;
}

.empty-card {
  background: var(--color-card-bg);
  border-radius: 10px;
  border: 1px solid var(--color-border);
  min-height: 120px;
}

.empty-card-radar {
  flex: 1;
  min-height: 280px;
}

.empty-card-bar {
  margin-top: 16px;
  min-height: 300px;
}
</style>