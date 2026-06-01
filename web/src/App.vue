<template>
  <div class="app">
    <div class="openrouter-watermark">OpenRouter</div>
    <NavBar />
    <main class="main">
      <ModelSelector />
      <BenchmarkContent />
      <FooterBar />
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import NavBar from "./components/NavBar.vue";
import ModelSelector from "./components/ModelSelector.vue";
import BenchmarkContent from "./components/BenchmarkContent.vue";
import FooterBar from "./components/FooterBar.vue";
import { useBenchmarks } from "./composables/useBenchmarks";

const { fetchModelList, restorePersistedModels } = useBenchmarks();

onMounted(() => {
  fetchModelList().then(() => {
    restorePersistedModels();
  });
});
</script>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main {
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 80px 24px 0;
}

.openrouter-watermark {
  position: fixed;
  left: 24vw;
  top: 100px;
  transform: perspective(1200px) rotateY(5deg) rotate(2deg);
  font-family: Arial, 'Helvetica Neue', sans-serif;
  font-size: 72px;
  font-weight: 300;
  letter-spacing: 6px;
  white-space: nowrap;
  color: rgba(170, 175, 185, 0.18);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.03), 0 4px 8px rgba(0, 0, 0, 0.02);
  pointer-events: none;
  user-select: none;
  z-index: -1;
  mask-image: linear-gradient(to right, rgba(0,0,0,1) 0%, rgba(0,0,0,1) 45%, rgba(0,0,0,0.4) 75%, rgba(0,0,0,0.15) 100%);
  -webkit-mask-image: linear-gradient(to right, rgba(0,0,0,1) 0%, rgba(0,0,0,1) 45%, rgba(0,0,0,0.4) 75%, rgba(0,0,0,0.15) 100%);
}
</style>
