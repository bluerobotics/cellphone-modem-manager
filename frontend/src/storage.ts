import { ref, Ref } from "vue";

/** Simple shared storage */

/** - Dev mode */
const isDevMode: Ref<boolean> = ref(false);

/** Utils */
const initStorage = () => {
  isDevMode.value = localStorage.getItem("isDevMode") === "true";
}

export {
  isDevMode,
  initStorage
}
