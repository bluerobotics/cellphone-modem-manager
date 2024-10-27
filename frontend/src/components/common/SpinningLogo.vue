<template>
  <v-container class="d-flex flex-column align-center justify-space-between">
    <v-img
      :aspect-ratio="1 / 1"
      class="lds-dual-ring"
      :width="size"
      src="@/assets/common/blue-robotics-logo.svg"
    />
    <span class="text-subtitle-1">{{ subtitle }}</span>
  </v-container>
</template>

<script lang="ts" setup>
import { defineProps } from 'vue';

withDefaults(defineProps<{
  size?: string;
  subtitle?: string;
}>(), {
  size: '10%',
});

</script>

<style scoped>
.lds-dual-ring {
  display: block;
  margin-top: 5%;
  margin-bottom: 2%;
  animation-name: rotation360;
  animation-duration: 2s;
  animation-iteration-count: infinite;
}

@keyframes rotation360 {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
