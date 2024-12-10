<template>
  <v-row v-if="cellInfo" class="device-details-container">
    <v-col cols="12" class="base-column title-column">
      <v-card-title>Serving Cell Info</v-card-title>
    </v-col>
    <v-divider />
    <v-col cols="12" class="base-column details-column">
      <p class="fixed-text"><strong>RAT:</strong> {{ cellInfo?.serving_cell.rat ?? 'N/A' }}</p>
      <p class="fixed-text"><strong>STATE:</strong> {{ cellInfo?.serving_cell.state ?? 'N/A' }}</p>
    </v-col>
    <v-col cols="12" class="base-column details-column">
      <p class="fixed-text"><strong>MCC:</strong> {{ cellInfo?.serving_cell.mobile_country_code ?? 'N/A' }}</p>
      <p class="fixed-text"><strong>MNC:</strong> {{ cellInfo?.serving_cell.mobile_network_code ?? 'N/A' }}</p>
      <p class="fixed-text"><strong>AREA:</strong> {{ cellInfo?.serving_cell.area_id ?? 'N/A' }}</p>
      <p class="fixed-text"><strong>ID:</strong> {{ cellInfo?.serving_cell.cell_id ?? 'N/A' }}</p>
    </v-col>
    <v-divider />
    <v-col cols="12">
      <apexchart :options="chartOptions" :series="chartData" type="line" class="chart"></apexchart>
    </v-col>
  </v-row>
  <SpinningLogo
    v-else
    subtitle="Fetching Serving cell info..."
  />
</template>

<script setup lang="ts">
import { computed, defineProps, onMounted, ref } from 'vue';

import SpinningLogo from '@/components/common/SpinningLogo.vue';
import { OneMoreTime } from '@/one-more-time';
import ModemManager from '@/services/ModemManager';
import { ModemCellInfo, ModemDevice } from '@/types/ModemManager';
import { getBaseApexChartOptions } from '@/utils';

/** Props / Emits */
const props = defineProps<{
  modem: ModemDevice;
  cellInfo: ModemCellInfo | null;
}>();

/** States */
const signalStrengthData = ref<number[]>([]);

/** Computed */
const chartData = computed(() => [
  {
    name: 'Signal',
    data: signalStrengthData.value,
  }
]);

const chartOptions = getBaseApexChartOptions(undefined, "Signal Strength", "dBm", -100, 0);

/** Utils */
const fetchSignalStrength = async () => {
  try {
    const strength = await ModemManager.fetchSignalStrengthById(props.modem.id);

    if (signalStrengthData.value.length >= 200) {
      signalStrengthData.value.shift();
    }
    signalStrengthData.value.push(strength.signal_strength_dbm);
  } catch (error) {
    console.error('Failed to fetch Signal Strength point, error:', (error as any)?.message);
  }
};

/** Tasks */
new OneMoreTime({ delay: 10000, disposeWith: this }, fetchSignalStrength);

/** Hooks */
onMounted(async () => {
  await fetchSignalStrength();
});
</script>

<style scoped>
.device-details-container {
  display: flex;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
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

.chart {
  margin-top: 20px;
}
</style>
