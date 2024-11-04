<template>
  <v-col cols="12" md="6" class="neighbor-cell-col">
    <v-tabs v-model="selectedTab" grow>
      <v-tab value="cells">Cells</v-tab>
      <v-tab value="map">Map</v-tab>
    </v-tabs>
    <v-card>
      <v-card-text>
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
      </v-card-text>
    </v-card>
  </v-col>
</template>

<script setup lang="ts">
import { ref, defineProps } from 'vue';
import { ModemDevice, ModemCellInfo } from '@/types/ModemManager';

import NeighborCellsTable from './NeighborCellsTable.vue';
import NetworkMap from './NetworkMap.vue';

const props = defineProps<{
  modem: ModemDevice;
  cellInfo: ModemCellInfo | null;
}>();

/** States */
const selectedTab = ref<string>('cells');
</script>

<style scoped>
.neighbor-cell-col {
  flex: 1;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  min-width: 500px;
  max-width: 100%;
  border: solid 1px rgb(123, 123, 123);
  border-radius: 8px;
}
</style>
