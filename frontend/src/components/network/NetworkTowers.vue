<template>
  <v-row class="device-details-container">
    <v-col cols="12" class="base-column title-column">
      <v-card-title>Neighbor Cells and Positioning </v-card-title>
    </v-col>
    <v-divider />
    <v-col cols="12" class="base-column details-column">
      <v-tabs v-model="selectedTab" grow>
        <v-tab value="cells">Nearby Cells</v-tab>
        <v-tab value="map">Map</v-tab>
      </v-tabs>
    </v-col>
    <v-col cols="12">
      <v-tabs-window v-model="selectedTab">
        <v-tabs-window-item value="cells">
          <NeighborCellsTable :cell-info="props.cellInfo" />
        </v-tabs-window-item>

        <v-tabs-window-item value="map">
          <NetworkMap
            :modem="props.modem"
            :cell-info="props.cellInfo"
          />
        </v-tabs-window-item>
      </v-tabs-window>
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import { defineProps, ref } from 'vue';

import { ModemCellInfo, ModemDevice } from '@/types/ModemManager';

import NetworkMap from './NetworkMap.vue';
import NeighborCellsTable from './NeighborCellsTable.vue';

/** Props / Emits */
const props = defineProps<{
  modem: ModemDevice;
  cellInfo: ModemCellInfo | null;
}>();

/** States */
const selectedTab = ref<string>('cells');
</script>

<style scoped>
.device-details-container {
  display: flex;
}

.base-column {
  display: flex;
  flex-direction: row;
  gap: 15px;
  font-size: 18px;
  justify-content: center;
}

.title-column {
  justify-content: center;
}
</style>
