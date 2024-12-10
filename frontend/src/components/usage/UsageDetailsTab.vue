<template>
  <v-container v-if="modemDataUsage !== null" fluid class="d-flex flex-wrap">
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
  <SpinningLogo
    v-else
    size="50"
    subtitle="Loading modem data usage..."
  />
</template>

<script setup lang="ts">
import { defineProps, onMounted, ref, watch } from 'vue';

import SpinningLogo from '@/components/common/SpinningLogo.vue';
import ModemManager from '@/services/ModemManager';
import { DataUsageControls, DataUsageSettings, ModemDevice } from '@/types/ModemManager';

/** Props / Emits */
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
    console.error('Failed to fetch Data Usage info, error:', (error as any)?.message);
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
    console.error('Failed to update Data Usage control, error:', (error as any)?.message);
  }
}

/** Hooks */
onMounted(fetchDataUsage);
</script>
