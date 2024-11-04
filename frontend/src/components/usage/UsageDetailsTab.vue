<template>
  <v-container fluid class="d-flex flex-wrap">
    <v-col cols="12" md="7">
      <UsageDetails
        :modem="modem"
        :data-usage="modemDataUsage"
      />
    </v-col>
    <v-col cols="12" md="5">
      <UsageControls
        :modem="modem"
        :data-usage="modemDataUsage"
        @on-update="onControlsUpdate"
      />
    </v-col>
  </v-container>
</template>

<script setup lang="ts">
import { defineProps, onMounted, ref, watch } from 'vue';

import ModemManager from '@/services/ModemManager';
import { ModemDevice, DataUsageSettings, DataUsageControls } from '@/types/ModemManager';

const props = defineProps<{
  modem: ModemDevice;
}>();

/** States */
const modemDataUsage = ref<DataUsageSettings | null>(null);

/** Utils */
const fetchDataUsage = async () => {
  try {
    const data = await ModemManager.fetchDataUsageById(props.modem.id);
    modemDataUsage.value = data;
  } catch (error) {
    console.error("Failed to fetch data usage", error);
  }
};

/** Watchers */
watch(() => props.modem, fetchDataUsage, { immediate: true });

/** Callbacks */
const onControlsUpdate = async (control: DataUsageControls) => {
  try {
    const data = await ModemManager.setDataUsageControlById(props.modem.id, control);
    modemDataUsage.value = data;
  } catch (error) {
    console.error("Failed to update data usage control", error);
  }
}

/** Hooks */
onMounted(fetchDataUsage);
</script>
