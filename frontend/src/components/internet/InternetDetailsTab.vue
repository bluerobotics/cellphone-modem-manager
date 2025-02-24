<template>
  <v-container fluid class="d-flex flex-wrap align-center">
    <v-col cols="12" md="8" class="pdp-col">
      <InternetControllerMode
        v-if="isDevMode"
        class="mb-2"
        :modem="modem"
      />
      <PDPContextDetails :modem="modem" />
    </v-col>
    <v-col cols="12" md="4" class="internet-details-col">
      <InternetSpeed :modem="modem" />
    </v-col>
  </v-container>
</template>

<script setup lang="ts">
import { defineProps } from 'vue';

import { ModemDevice } from '@/types/ModemManager';

import PDPContextDetails from './PDPContextDetails.vue';
import InternetControllerMode from './InternetControllerMode.vue';
import InternetSpeed from './InternetSpeed.vue';
import { isDevMode } from '@/storage';

defineProps<{
  modem: ModemDevice;
}>();

</script>

<style scoped>
.pdp-col {
  display: flex;
  flex-grow: 1;
  flex-direction: column;
  max-width: 100%;
}

.internet-details-col{
  display: flex;
  flex-grow: 1;
  flex-direction: column;
  max-width: 100%;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  justify-content: center;
  align-items: center;
}
</style>
