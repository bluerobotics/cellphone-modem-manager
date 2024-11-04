<template>
  <v-card class="align-center text-center" elevation="0">
    <v-card-title class="ma-0 pa-0 text-center">
      Internet Controller Mode
    </v-card-title>
    <v-card-text
      v-if="selected_internet_mode !== null"
      class="pt-2 d-flex flex-column align-center"
    >
      <v-radio-group
        v-model="selected_internet_mode"
        inline
        @change="onInternetModeChange"
        class="justify-center"
      >
        <v-radio key="qmi" label="QMI" :value="USBNetMode.QMI" />
        <v-radio key="ecm" label="ECM" :value="USBNetMode.ECM" />
        <v-radio key="mbim" label="MBIM" :value="USBNetMode.MBIM" />
      </v-radio-group>
    </v-card-text>
    <SpinningLogo
      v-else
      size="50"
      subtitle="Loading internet controller mode..."
    />
  </v-card>
</template>

<script setup lang="ts">
import { ref, onMounted, defineProps } from 'vue';
import ModemManager from '@/services/ModemManager';
import { ModemDevice, USBNetMode } from '@/types/ModemManager';
import SpinningLogo from '@/components/common/SpinningLogo.vue';

const props = defineProps<{
  modem: ModemDevice;
}>();

/** States */
const selected_internet_mode = ref<USBNetMode | null>(null);

/** Utils */

const fetchCurrentInternetControllerMode = async () => {
  try {
    selected_internet_mode.value = await ModemManager.fetchUSBModeById(props.modem.id);
  } catch (error) {
    console.error("Failed to get current internet controller mode", error);
  }
};

const setInternetControllerMode = async (mode: USBNetMode) => {
  try {
    console.log("Setting internet controller mode to", mode);
    await ModemManager.setUSBModeById(props.modem.id, mode);
  } catch (error) {
    console.error("Failed to set internet controller mode", error);
  }
};

/** Callbacks */
const onInternetModeChange = async () => {
  if (!selected_internet_mode.value) {
    return;
  }

  await setInternetControllerMode(selected_internet_mode.value);
  await fetchCurrentInternetControllerMode();
};

/** Hooks */
onMounted(async () => {
  fetchCurrentInternetControllerMode();
});
</script>
