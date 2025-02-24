<template>
  <v-card class="align-center text-center" elevation="0">
    <v-card-title class="ma-0 pa-0 text-center">
      Internet Controller Mode
      <v-icon
        @click="showInfoDialog = true"
        size="24"
        class="ml-2"
      >
        mdi-information-outline
      </v-icon>
    </v-card-title>
    <v-card-text
      v-if="selectedInternetMode !== null"
      class="pt-3 d-flex flex-column align-center"
    >
      <v-radio-group
        v-model="selectedInternetMode"
        inline
        @change="onInternetModeChangeRequest"
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

    <v-dialog v-model="showChangeDialog" max-width="400px">
      <v-card class="pa-2">
        <v-card-title>Confirm Internet Mode Change</v-card-title>
        <v-card-text v-if="!savingInternetMode">
          You are about to change from {{ currentModeLabel }} to {{ newModeLabel }}. Are you sure?
        </v-card-text>
        <SpinningLogo
          v-else
          subtitle="Saving new internet controller mode"
        />
        <v-card-actions class="justify-center pa-2">
          <v-spacer></v-spacer>
          <v-btn
            color="primary"
            :disabled="savingInternetMode"
            @click="onCancelChange"
          >
            Cancel
          </v-btn>
          <v-btn
            color="red"
            :disabled="savingInternetMode"
            @click="onConfirmChange"
          >
            Confirm
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-dialog v-model="showInfoDialog" max-width="550px">
      <v-card class="pa-2">
        <v-card-title>Internet Controller Modes</v-card-title>
        <v-card-text class="text-justify">
          Modems support different <strong>Internet Controller Modes</strong> that define how they interface with the operating system for data transmission.

          <v-divider class="my-2"></v-divider>

          <strong>Common Modes:</strong>
          <ul class="ml-4">
            <li><strong>QMI (Qualcomm MSM Interface):</strong> A proprietary high-performance protocol used in <strong>(Qualcomm/Quectel)</strong> based modems. Requires specific drivers for proper operation.</li>
            <li><strong>ECM (Ethernet Control Model):</strong> A standard USB networking mode that presents the modem as an Ethernet device.</li>
            <li><strong>MBIM (Mobile Broadband Interface Model):</strong> A modern, efficient mode designed for mobile broadband devices, commonly used in Windows and Linux.</li>
          </ul>

          <v-divider class="my-2"></v-divider>

          <strong>Warning:</strong> Changing the Internet Controller Mode can affect modem compatibility and connectivity. <strong>Do not change this setting unless you know what you're doing.</strong>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" @click="showInfoDialog = false">Got it</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script setup lang="ts">
import { ref, onMounted, defineProps, computed } from 'vue';
import ModemManager from '@/services/ModemManager';
import { ModemDevice, USBNetMode } from '@/types/ModemManager';
import SpinningLogo from '@/components/common/SpinningLogo.vue';

const props = defineProps<{
  modem: ModemDevice;
}>();

/** States */
const selectedInternetMode = ref<USBNetMode | null>(null);
const originalInternetMode = ref<USBNetMode | null>(null);
const pendingInternetMode = ref<USBNetMode | null>(null);
const showChangeDialog = ref(false);
const showInfoDialog = ref(false);
const savingInternetMode = ref(false);

/** Display helpers */
const modeLabels = {
  [USBNetMode.QMI]: 'QMI',
  [USBNetMode.ECM]: 'ECM',
  [USBNetMode.MBIM]: 'MBIM'
};

const currentModeLabel = computed(() => {
  return originalInternetMode.value ? modeLabels[originalInternetMode.value] : '';
});

const newModeLabel = computed(() => {
  return pendingInternetMode.value ? modeLabels[pendingInternetMode.value] : '';
});

/** Utils */
const fetchCurrentInternetControllerMode = async () => {
  try {
    const currentMode = await ModemManager.fetchUSBModeById(props.modem.id);
    selectedInternetMode.value = currentMode;
    originalInternetMode.value = currentMode;
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
const onInternetModeChangeRequest = () => {
  if (originalInternetMode.value && selectedInternetMode.value !== originalInternetMode.value) {
    pendingInternetMode.value = selectedInternetMode.value;
    showChangeDialog.value = true;
  }
};

const onConfirmChange = async () => {
  savingInternetMode.value = true;
  if (pendingInternetMode.value) {
    await setInternetControllerMode(pendingInternetMode.value);
    originalInternetMode.value = pendingInternetMode.value;
    selectedInternetMode.value = pendingInternetMode.value;
  }
  await fetchCurrentInternetControllerMode();
  showChangeDialog.value = false;
  pendingInternetMode.value = null;
  savingInternetMode.value = false;
};

const onCancelChange = () => {
  selectedInternetMode.value = originalInternetMode.value;
  showChangeDialog.value = false;
  pendingInternetMode.value = null;
};

/** Hooks */
onMounted(async () => {
  await fetchCurrentInternetControllerMode();
});
</script>
