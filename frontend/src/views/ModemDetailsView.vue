<template>
  <v-card rounded="0">
    <v-card-title>Selected Modem</v-card-title>
    <v-card-text>
      <p>Device: {{ modem.device }}</p>
      <p>Manufacturer: {{ modem.manufacturer }}</p>
      <p>Product: {{ modem.product }}</p>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { defineProps } from 'vue';

import { ModemDevice } from '@/types/ModemManager';

defineProps<{
  modem: ModemDevice;
}>();
</script>

<style scoped>

</style>
