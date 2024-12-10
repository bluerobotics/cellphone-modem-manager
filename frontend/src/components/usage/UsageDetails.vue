<template>
  <v-card class="pa-4">
    <v-card-text>
      <apexchart
        :options="chartOptions"
        :series="chartData"
        type="line"
      />
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { computed, defineProps } from 'vue';
import dayjs from 'dayjs';

import { DataUsageSettings, ModemDevice } from '@/types/ModemManager';
import { bytesToLevel, getBaseApexChartOptions } from '@/utils';

/** Props / Emits */
const props = defineProps<{
  modem: ModemDevice;
  dataUsage: DataUsageSettings | null;
}>();

/** Computed */
const chartPoints = computed(() => {
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


  const data = [];
  let lastUsage = 0;
  for (let date = startDate; date.isBefore(endDate); date = date.add(1, 'day')) {
    const usage = props.dataUsage.data_points[date.format('YYYY-MM-DD')]

    if (usage) {
      lastUsage = usage[0] + usage[1];
    }


    data.push({
      x: date.format('YYYY-MM-DD'),
      y: lastUsage,
    });
  }

  return [
    {
      name: 'Usage',
      data,
    },
  ];
});

const chartData = computed(() => {
  const max = Math.max(...chartPoints.value[0].data.map((d: any) => d.y));
  const [_, unit] = bytesToLevel(max);

  console.log("Unit", unit);

  return [
    {
      name: 'Usage',
      data: chartPoints.value[0].data.map((d: any) => ({
        x: d.x,
        y: bytesToLevel(d.y, unit)[0].toFixed(1),
      })),
    },
  ];
});

const chartOptions = computed(() => {
  const max = Math.max(...chartPoints.value[0].data.map((d: any) => d.y));
  const [_, unit] = bytesToLevel(max);

  const data = chartPoints.value[0].data;
  const firstDate = data[0]?.x;
  const lastDate = data[data.length - 1]?.x;

  const baseOptions = getBaseApexChartOptions(undefined, "Data usage since last reset", unit);

  return {
    ...baseOptions,
    xaxis: {
      ...baseOptions.xaxis,
      labels: {
        formatter: (value: string) => {
          if (value === firstDate || value === lastDate) {
            return value;
          }
          return "";
        },
        style: {
          colors: 'white',
        },
      },
    },
  }
})

</script>
