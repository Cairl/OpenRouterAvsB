<template>
  <footer class="footer" v-if="state.modelA && state.modelB">
    <span class="footer-note">数据来源: OpenRouter</span>
  </footer>
</template>

<script setup lang="ts">
import { useAppState } from "../composables/useState";

const state = useAppState();
</script>

<style scoped>
.footer {
  padding: 10px 28px 20px;
  display: flex;
  justify-content: center;
  font-size: 10px;
  color: var(--color-text-muted);
  letter-spacing: 0.5px;
}
</style>
