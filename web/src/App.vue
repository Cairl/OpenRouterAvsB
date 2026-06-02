<template>
  <div class="app">
    <div class="openrouter-watermark"><span class="wm-letter" style="--i:0">O</span><span class="wm-letter" style="--i:1">p</span><span class="wm-letter" style="--i:2">e</span><span class="wm-letter" style="--i:3">n</span><span class="wm-letter" style="--i:4">R</span><span class="wm-letter" style="--i:5">o</span><span class="wm-letter" style="--i:6">u</span><span class="wm-letter" style="--i:7">t</span><span class="wm-letter" style="--i:8">e</span><span class="wm-letter" style="--i:9">r</span></div>
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
  left: 18vw;
  top: 60px;
  transform: perspective(1200px) rotateY(5deg) rotate(2deg);
  font-family: "Consolas", "Courier New", monospace;
  font-size: 72px;
  font-weight: 300;
  white-space: nowrap;
  color: rgba(170, 175, 185, 0.18);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.03), 0 4px 8px rgba(0, 0, 0, 0.02);
  pointer-events: none;
  user-select: none;
  z-index: -1;
  overflow: visible;
  padding: 40px 60px;
  mask-image: linear-gradient(to right, rgba(0,0,0,1) 0%, rgba(0,0,0,1) 65%, rgba(0,0,0,0.5) 85%, rgba(0,0,0,0.25) 100%);
  -webkit-mask-image: linear-gradient(to right, rgba(0,0,0,1) 0%, rgba(0,0,0,1) 65%, rgba(0,0,0,0.5) 85%, rgba(0,0,0,0.25) 100%);
}

.wm-letter {
  display: inline-block;
  margin: 0 4px;
  will-change: transform, rotate;
  animation: wm-rotate 18s cubic-bezier(0.37, 0, 0.63, 1) infinite,
             wm-drift 13s cubic-bezier(0.37, 0, 0.63, 1) infinite,
             wm-bob 21s cubic-bezier(0.45, 0, 0.55, 1) infinite;
  animation-delay: calc(var(--i) * -1.7s), calc(var(--i) * -2.1s), calc(var(--i) * -2.7s);
}

@keyframes wm-rotate {
  0%, 100% { rotate: -20deg; }
  50% { rotate: 20deg; }
}

@keyframes wm-drift {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(18px); }
  50% { transform: translateX(0); }
  75% { transform: translateX(-18px); }
}

@keyframes wm-bob {
  0%, 100% { transform: translateY(0); }
  33% { transform: translateY(-6px); }
  66% { transform: translateY(6px); }
}
</style>
