<template>
  <nav class="navbar">
    <div class="nav-inner">
      <a class="github-link" href="https://github.com/Cairl/OpenRouterAvsB" target="_blank" rel="noopener">
        <svg viewBox="0 0 16 16" fill="currentColor" width="20" height="20"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>
      </a>
    </div>
  </nav>
</template>

<script setup lang="ts">
</script>

<style scoped>
.navbar {
  padding: 14px 0;
}

.nav-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  align-items: center;
}

.brand {
  position: relative;
  display: inline-block;
  cursor: default;
  user-select: none;
  color: var(--color-text);
  font-family: "Consolas", "Courier New", monospace;
  font-size: 20px;
  letter-spacing: 3px;
}

.brand::before {
  content: "";
  position: absolute;
  left: -3px;
  bottom: -1px;
  width: calc(100% + 6px);
  height: 13px;
  background: linear-gradient(
    180deg,
    rgba(255, 220, 100, 0.0) 0%,
    rgba(255, 210, 80, 0.32) 35%,
    rgba(255, 180, 40, 0.22) 70%,
    rgba(255, 150, 20, 0.08) 100%
  );
  transform: scaleX(0) rotate(-1.2deg);
  transform-origin: left center;
  transition: transform 0.48s cubic-bezier(0.22, 0.61, 0.36, 1);
  z-index: -1;
  border-radius: 30% 70% 60% 40% / 35% 55% 50% 60%;
  filter: blur(1.5px);
}

.brand::after {
  content: "";
  position: absolute;
  left: 0;
  bottom: 1px;
  width: 100%;
  height: 4px;
  background: linear-gradient(
    90deg,
    rgba(255, 130, 10, 0.6) 0%,
    rgba(255, 160, 30, 0.52) 12%,
    rgba(255, 185, 45, 0.45) 35%,
    rgba(255, 195, 55, 0.4) 60%,
    rgba(255, 175, 35, 0.28) 85%,
    rgba(255, 140, 20, 0.1) 100%
  );
  transform: scaleX(0) rotate(-0.9deg);
  transform-origin: left center;
  transition: transform 0.4s 0.07s cubic-bezier(0.22, 0.61, 0.36, 1);
  z-index: -1;
  border-radius: 35% 65% 55% 45% / 55% 45% 50% 50%;
}

.brand:hover::before {
  transform: scaleX(1) rotate(-1.2deg);
}

.brand:hover::after {
  transform: scaleX(1) rotate(-0.9deg);
}

.github-link {
  color: #aaa;
  position: fixed;
  top: 16px;
  right: 24px;
  z-index: 100;
  display: inline-flex;
  align-items: center;
  transition: color 0.2s;
}

.github-link:hover {
  color: #666;
}

.github-link svg {
  width: 20px;
  height: 20px;
}
</style>
