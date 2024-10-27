<template>
  <v-container class="d-flex flex-column align-center justify-space-between">
    <v-icon class="op-error-icon" :size="size" :color="color">{{ icon }}</v-icon>
    <span class="text-h4">{{ title }}</span>
    <span class="text-subtitle-1">{{ subtitle }}</span>
  </v-container>
</template>

<script lang="ts" setup>
import { defineProps } from 'vue';

withDefaults(defineProps<{
  icon?: string;
  size?: string;
  color?: string;
  title?: string;
  subtitle?: string;
}>(), {
  icon: 'mdi-alert-octagon',
  size: '100',
  color: 'red',
});

</script>

<style scoped>
.op-error-icon {
  display: block;
  margin-top: 5%;
  margin-bottom: 2%;
}
</style>
