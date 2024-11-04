<template>
  <v-container fluid class="d-flex flex-wrap">
    <ServingTower
      :modem="props.modem"
      :cell-info="cellInfo"
    />
    <NetworkTowers
      :modem="props.modem"
      :cell-info="cellInfo"
    />
  </v-container>
</template>

<script setup lang="ts">
import { defineProps, ref } from 'vue';

import { OneMoreTime } from '@/one-more-time';
import ModemManager from '@/services/ModemManager';
import { ModemCellInfo, ModemDevice } from '@/types/ModemManager';

import NetworkTowers from './NetworkTowers.vue';
import ServingTower from './ServingTower.vue';

const props = defineProps<{
  modem: ModemDevice;
}>();

/** States */
const cellInfo = ref<ModemCellInfo | null>(null);

/** Utils */
const fetchCellInfo = async () => {
  try {
    cellInfo.value = await ModemManager.fetchCellInfoById(props.modem.id);
  } catch (error) {
    cellInfo.value = null;
    console.error('Unable to fetch cellInfo', (error as any)?.message);
  }
};

/** Tasks */
new OneMoreTime({ delay: 10000, disposeWith: this }, fetchCellInfo);
</script>
