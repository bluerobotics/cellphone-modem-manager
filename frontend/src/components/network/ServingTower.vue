<template>
  <v-col cols="12" md="6" class="serving-cell-col">
    <apexchart :options="chartOptions" :series="signalQualityChartData" type="line"></apexchart>
  </v-col>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, defineProps } from 'vue';
import ModemManager from '@/services/ModemManager';
import { ModemDevice, ModemCellInfo } from '@/types/ModemManager';
import { OneMoreTime } from '@/one-more-time';

const props = defineProps<{
  modem: ModemDevice;
  cellInfo: ModemCellInfo | null;
}>();

/** States */
const signalQualityData = ref<number[]>([]);

/** Computed */
const signalQualityChartData = computed(() => {
  return [{
    name: 'Signal',
    data: signalQualityData.value,
  }];
});

const chartOptions = {
  chart: { toolbar: { show: false } },
  tooltip: { enabled: false },
  dataLabels: { enabled: false },
  yaxis: {
    title: {
      text: 'dBm',
      style: {
        fontSize: '14px',
        color: 'white'
      }
    },
    min: -100,
    max: 0,
  },
  xaxis: {
    title: {
      text: 'Serving Cell Signal Quality',
      style: {
        fontSize: '14px',
        color: 'white'
      }
    },
    labels: {
      show: false
    }
  }
};

/** Utils */

const fetchSignalStrength = async () => {
  try {
    const quality = await ModemManager.fetchSignalStrengthById(props.modem.id);

    if (signalQualityData.value.length >= 200) {
      signalQualityData.value.shift();
    }
    signalQualityData.value.push(quality.signal_strength_dbm);
  } catch (error) {
    console.error('Failed to fetch signal strength', (error as any)?.message);
  }
};

/** Tasks */
new OneMoreTime({ delay: 10000, disposeWith: this }, fetchSignalStrength);

/** Hooks */
onMounted(async () => {
  fetchSignalStrength();
});
</script>

<style scoped>
.serving-cell-col {
  flex: 1;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  min-width: 500px;
  max-width: 100%;
}
</style>
