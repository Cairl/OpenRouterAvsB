<template>
  <div class="content-section" v-if="!state.loading && state.modelA && state.modelB">
    <div class="section-label">基准测试</div>
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
  <div class="content-skeleton" v-else-if="state.loading">
    <div class="section-label">基准测试</div>
    <div class="skeleton-table">
      <div class="skeleton-row" v-for="i in 6" :key="i"></div>
    </div>
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
.content-skeleton {
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
  font-size: 12px;
  color: var(--color-text-muted);
  letter-spacing: 2px;
  font-weight: 600;
  margin-top: 16px;
  margin-bottom: 10px;
}

.skeleton-table {
  background: var(--color-card-bg);
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid var(--color-border);
  padding: 12px;
}

.skeleton-row {
  height: 32px;
  background: linear-gradient(90deg, #eee 25%, #f5f5f5 50%, #eee 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
  margin-bottom: 8px;
}

.skeleton-row:last-child {
  margin-bottom: 0;
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
</style>
