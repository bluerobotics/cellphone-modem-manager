<template>
    <v-card class="pa-4">
      <v-card-text>
        <apexchart
          :options="chartOptions"
          :series="usageChartData"
          type="line"
        />
      </v-card-text>
    </v-card>
</template>

<script setup lang="ts">
import { defineProps, computed } from 'vue';
import dayjs from 'dayjs';

import { ModemDevice, DataUsageSettings } from '@/types/ModemManager';

const props = defineProps<{
  modem: ModemDevice;
  dataUsage: DataUsageSettings | null;
}>();

/** Computed */
const usageChartData = computed(() => {
  if (!props.dataUsage) {
    return [
      {
        name: 'Usage',
        data: [],
      },
    ];
  }

  const now = dayjs();
  const startDate = dayjs().date(props.dataUsage.data_reset_day).isBefore(now)
    ? dayjs().date(props.dataUsage.data_reset_day)
    : dayjs().subtract(1, 'month').date(props.dataUsage.data_reset_day);
  const endDate = startDate.add(1, 'month').add(1, 'day');


  /** Create a date array from start to end date */
  const data = [];
  let lastUsage = 0;
  for (let date = startDate; date.isBefore(endDate); date = date.add(1, 'day')) {
    const usage = props.dataUsage.data_points[date.format('YYYY-MM-DD')]
    data.push({
      x: date.format('YYYY-MM-DD'),
      y: usage ?? lastUsage,
    });
  }

  return [
    {
      name: 'Usage',
      data: data,
    },
  ];
});

const chartOptions = computed(() => ({
  chart: { toolbar: { show: false } },
  tooltip: { enabled: true },
  dataLabels: { enabled: false },
  yaxis: {
    title: {
      text: 'Data (GB)',
      style: {
        fontSize: '14px',
        color: 'white'
      }
    },
  },
  xaxis: {
    type: 'category',
    categories: usageChartData.value[0]?.data.map(d => d.x), // Dynamically derive categories
    title: {
      text: 'Data Usage Since Last Reset',
      style: {
        fontSize: '14px',
        color: 'white'
      }
    },
    labels: {
      rotate: -45, // Rotate for better visibility
    }
  },
  grid: {
    borderColor: '#444',
    strokeDashArray: 5,
  },
}));

</script>

<style scoped>
.v-card {
  border: 1px solid #ccc;
  border-radius: 8px;
}
</style>
