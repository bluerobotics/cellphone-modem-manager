<template>
  <v-container fluid class="d-flex flex-wrap align-center">
    <v-col cols="12" md="4" class="operator-col">
      <ModemOperatorDetails :modem="modem" />
    </v-col>
    <v-col cols="12" md="8" class="device-col">
      <ModemDeviceDetails :modem="modem" @reset="onReset"/>
    </v-col>
  </v-container>
</template>

<script setup lang="ts">
import { defineProps } from 'vue';

import { ModemDevice } from '@/types/ModemManager';

import ModemOperatorDetails from './ModemOperatorDetails.vue';
import ModemDeviceDetails from './ModemDeviceDetails.vue';

defineProps<{
  modem: ModemDevice;
}>();
const emit = defineEmits<(event: 'reset') => void>();

/** Callbacks */
const onReset = () => {
  emit('reset');
};
</script>

<style>
.operator-col {
  flex: 1;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  min-width: 200px;
  max-width: 100%;
}

.device-col {
  display: flex;
  flex-grow: 1;
  flex-direction: column;
  max-width: 100%;
}
</style>
