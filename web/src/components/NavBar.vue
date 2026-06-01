<template>
  <nav class="navbar">
    <div class="nav-inner"></div>
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
  font-family: Georgia, serif;
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
</style>
