import { createApp } from "vue";
import { AppStateKey, createAppState } from "./composables/useState";
import App from "./App.vue";
import "./style.css";

const app = createApp(App);
app.provide(AppStateKey, createAppState());
app.mount("#app");
