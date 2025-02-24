<template>
  <v-row v-if="deviceDetails" class="device-details-container">
    <v-col cols="12" md="5" class="details-column">
      <p class="fixed-text"><strong>IMEI:</strong> {{ deviceDetails?.imei ?? 'N/A' }}</p>
      <p class="fixed-text"><strong>SN:</strong> {{ deviceDetails?.serial_number ?? 'N/A' }}</p>
      <p class="fixed-text"><strong>IMSI:</strong> {{ deviceDetails?.imsi ?? 'N/A' }}</p>
    </v-col>
    <v-col cols="12" md="5" class="details-column">
      <p class="fixed-text"><strong>FIRM:</strong> {{ deviceDetails?.firmware_revision.firmware_revision ?? 'N/A'}}</p>
      <p class="fixed-text"><strong>-</strong> {{ deviceDetails?.firmware_revision.timestamp ?? 'N/A'}}</p>
      <p class="fixed-text"><strong>-</strong> {{ deviceDetails?.firmware_revision.authors ?? 'N/A'}}</p>
    </v-col>
    <v-col cols="12" md="2" class="details-column reset-column">
      <v-btn
        v-if="isDevMode"
        color="primary"
        @click="onConsole"
      >
        Console
      </v-btn>
      <v-btn color="primary" @click="onReboot">Reboot</v-btn>
      <v-btn color="warning" @click="onReset">Reset</v-btn>
    </v-col>
  </v-row>
  <SpinningLogo
    v-else
    subtitle="Fetching device details..."
  />
  <v-dialog v-model="showResetDialog" max-width="400px">
    <v-card class="pa-2">
      <v-card-title>Confirm Factory Reset</v-card-title>
      <v-card-text>Are you sure you want to reset the modem?</v-card-text>
      <v-card-actions class="justify-center pa-2">
        <v-spacer></v-spacer>
        <v-btn color="primary" @click="showResetDialog = false">Cancel</v-btn>
        <v-btn color="red" @click="onConfirmReset">Confirm</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
  <v-dialog
    v-model="showConsoleDialog"
    width="85%"
  >
    <v-card>
      <v-app-bar dense>
        <v-text-field
          v-model="commandInput"
          class="pl-3"
          label="AT Command"
          hide-details
          clearable
          variant="solo-filled"
        />
        <v-text-field
          v-model="commandDelay"
          class="px-3"
          style="max-width: 150px;"
          label="Delay (s)"
          type="number"
          hide-details
          variant="solo-filled"
        />
        <v-btn
          class="px-3"
          color="primary"
          :disabled="!commandInput || sendingCommand"
          :icon="sendingCommand ? 'mdi-loading mdi-spin' : 'mdi-send'"
          @click="sendCommand"
        />
        <v-spacer style="max-width: 30px;" />
      </v-app-bar>
      <v-sheet>
        <v-card-text ref="logContainer" class="scrollable-content">
          <!-- eslint-disable -->
          <pre class="logs" v-html="htmlConsoleOutput" />
          <!-- eslint-enable -->
        </v-card-text>
      </v-sheet>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { AnsiUp } from 'ansi_up'
import { ref, defineProps, computed } from 'vue';

import { OneMoreTime } from '@/one-more-time';

import ModemManager from '@/services/ModemManager';
import { ModemDevice, ModemDeviceDetails } from '@/types/ModemManager';

import SpinningLogo from '@/components/common/SpinningLogo.vue';
import { isDevMode } from '@/storage';

const props = defineProps<{
  modem: ModemDevice;
}>();
const emit = defineEmits<(event: 'reset' | 'reboot') => void>();

const ansi = new AnsiUp();

/** States */
const deviceDetails = ref<ModemDeviceDetails | null>(null);
const logContainer = ref(null);
const sendingCommand = ref(false);
const commandInput = ref('');
const commandDelay = ref(0.3);
const consoleText = ref('');
const showResetDialog = ref(false);
const showConsoleDialog = ref(false);

/** Computed */
const htmlConsoleOutput = computed((): string => {
  return ansi.ansi_to_html(consoleText.value)
});

/** Utils */
const fetchDeviceDetails = async () => {
  try {
    deviceDetails.value = await ModemManager.fetchById(props.modem.id);
  } catch (error) {
    console.error("Failed to fetch modem details", error);
  }
};

/** Callbacks */
const onReset = () => {
  showResetDialog.value = true;
};

const onReboot = () => {
  emit('reboot');
};

const onConsole = () => {
  showConsoleDialog.value = true;
};

const onConfirmReset = () => {
  emit('reset');
  showResetDialog.value = false;
};

const sendCommand = async () => {
  try {
    sendingCommand.value = true;
    const response = await ModemManager.commandById(props.modem.id, commandInput.value);
    consoleText.value += response;
  } catch (error) {
    console.error("Failed to send command", error);
  } finally {
    sendingCommand.value = false;
  }
};

/** Tasks */
new OneMoreTime({ delay: 30000, disposeWith: this }, fetchDeviceDetails);
</script>

<style scoped>
.device-col {
  display: flex;
  flex-grow: 1;
  flex-direction: column;
  max-width: 100%;
}

.device-details-container {
  display: flex;
  width: 100%;
  padding: 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
}

.details {
  display: flex;
  width: 100%;
  justify-content: space-between;
}

.details-column {
  display: flex;
  flex-direction: column;
  gap: 10px;
  font-size: 18px;
}

.reset-column {
  width: 100%;
  display: flex;
  justify-content: center;
}

.fixed-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 400px;
}

.jv-code {
  padding: 0px !important;
}

pre.logs {
  margin-top: 50px;
  color:white;
  background: black;
  padding: 10px;
  overflow-x: scroll;
  height: 60vh;
}

.scrollable-content {
  max-height: 71vh;
  overflow-y: auto;
}
</style>
