<template>
  <div
    v-if="neighborCells.length === 0"
    class="no-info-available"
  >
    <strong>No nearby cells info available.</strong>
  </div>
  <v-card v-else>
    <v-row class="pt-3 virtual-table-row">
      <v-col
        v-for="column in tableColumns"
        class="virtual-table-cell title-table-cell"
      >
        <strong>{{ column }}</strong>
      </v-col>
    </v-row>
    <v-virtual-scroll
      :items="tableData"
      height="300"
      item-height="30"
      class="virtual-table"
    >
      <template #default="{ item }">
        <v-row class="virtual-table-row">
          <v-col
            v-for="column in item"
            class="virtual-table-cell"
          >
            {{ column }}
          </v-col>
        </v-row>
      </template>
    </v-virtual-scroll>
  </v-card>
</template>

<script setup lang="ts">
import { computed, defineProps } from 'vue';

import { ModemCellInfo, NeighborCellInfo } from '@/types/ModemManager';

/** Props / Emits */
const props = defineProps<{
  cellInfo: ModemCellInfo | null;
}>();

/** Computed */
const neighborCells = computed<NeighborCellInfo[]>(() => {
  if (!props.cellInfo) return [];
  return props.cellInfo.neighbor_cells;
});

const columnsMapping: Record<string, string> = {
  rat: 'TECH',
  mobile_country_code: 'MCC',
  mobile_network_code: 'MNC',
  area_id: 'LAC',
  cell_id: 'Cell ID',
  signal_quality_dbm: 'POWER',
}

const tableKeys = computed<string[]>(() => {
  return Object.keys(columnsMapping).filter((key) => {
    return neighborCells.value.some(
      (cell) => cell[key as keyof NeighborCellInfo] !== null && cell[key as keyof NeighborCellInfo] !== undefined
    );
  });
});

const tableColumns = computed<string[]>(() => {
  return tableKeys.value.map((key) => {
    return columnsMapping[key];
  });
});

const tableData = computed<string[][]>(() => {
  return neighborCells.value.map((cell) => {
    return tableKeys.value.map((key) => {
      return (cell[key as keyof NeighborCellInfo] ?? '-') as string;
    });
  });
});
</script>

<style scoped>
.no-info-available {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 350px;
}

.virtual-table-row {
  display: flex;
  margin: 0;
  margin-bottom: 15px;
  border-bottom: 1px solid #eee;
  flex-wrap: nowrap;
}

.virtual-table-cell {
  flex: 1;
  padding: 5px;
  height: 30px;
  min-width: 60px;
  text-wrap: nowrap;
}

.title-table-cell {
  font-weight: bold;
  text-wrap: nowrap;
}

.virtual-table {
  overflow-x: hidden;
}
</style>
