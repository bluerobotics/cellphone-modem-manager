<template>
  <v-container fluid class="ga-3 d-flex flex-wrap align-center">
    <v-col cols="12" md="6" class="tab-col right-col">
      <NetworkTowers
        :modem="props.modem"
        :cell-info="cellInfo"
      />
    </v-col>
    <v-col cols="12" md="6" class="tab-col left-col">
      <ServingTower
        :modem="props.modem"
        :cell-info="cellInfo"
      />
    </v-col>
  </v-container>
</template>

<script setup lang="ts">
import { defineProps, ref } from 'vue';

import { OneMoreTime } from '@/one-more-time';
import ModemManager from '@/services/ModemManager';
import { ModemCellInfo, ModemDevice } from '@/types/ModemManager';

import NetworkTowers from './NetworkTowers.vue';
import ServingTower from './ServingTower.vue';

/** Props / Emits */
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
    console.error('Failed to fetch Cell Info, error:', (error as any)?.message);
  }
};

/** Tasks */
new OneMoreTime({ delay: 25000, disposeWith: this }, fetchCellInfo);
</script>

<style scoped>
.tab-col {
  flex: 1;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  max-width: 100%;
}

.left-col {
  min-width: 400px;
}

.right-col {
  min-width: 400px;
  height: 100%;
}
</style>
