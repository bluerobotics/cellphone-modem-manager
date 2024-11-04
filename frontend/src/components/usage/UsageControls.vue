<template>
  <v-card class="pa-4" height="100%">
    <v-card-title>Data Usage Controls</v-card-title>
    <v-card-text>
      <v-row>
        <v-col cols="12">
          <v-switch
            v-model="controlEnabled"
            label="Enable Data Alert"
            :color="controlEnabled ? 'primary' : 'grey'"
            @change="onDataAlertToggle"
          />
        </v-col>

        <v-col cols="12" md="8">
          <v-text-field
            v-model="controlUsage"
            type="number"
            label="Value"
            :disabled="!controlEnabled"
          />
        </v-col>
        <v-col cols="12" md="4">
          <v-select
            v-model="controlUnit"
            :items="validDataAlertUnits"
            label="Unit"
            :disabled="!controlEnabled"
          />
        </v-col>

        <v-col cols="12">
          <v-text-field
            v-model="controlResetDay"
            label="Cycle Reset month day"
            type="number"
            :rules="resetDayRules"
            :disabled="!controlEnabled"
          />
        </v-col>
      </v-row>
    </v-card-text>
    <v-card-actions class="justify-center px-4">
      <v-spacer />
      <v-btn
        color="primary"
        :variant="controlEnabled ? 'flat' : 'tonal'"
        :disabled="!controlEnabled"
        @click="onSave"
      >
        Save
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { defineProps } from 'vue';

import { ModemDevice, DataUsageSettings, DataUsageControls } from '@/types/ModemManager';

const props = defineProps<{
  modem: ModemDevice;
  dataUsage: DataUsageSettings | null;
}>();

const emit = defineEmits<(e: 'on-update', control: DataUsageControls) => void>()

/** State */
const controlEnabled = ref(false);
const controlUsage = ref(0);
const controlUnit = ref("B");
const controlResetDay = ref(1);

const validDataAlertUnits = ["B", "KB", "MB", "GB"];
const resetDayRules = [
  (v: number) => v >= 1 && v <= 31 || "Day must be between 1 and 31",
];

/** Utils */
const bytesToLevel = (bytes: number): [number, string] => {
  if (bytes < 2 ** 10) {
    return [bytes, "B"];
  } else if (bytes < 2 ** 20) {
    return [bytes / (2 ** 10), "KB"];
  } else if (bytes < 2 ** 30) {
    return [bytes / (2 ** 20), "MB"];
  } else {
    return [bytes / (2 ** 30), "GB"];
  }
};

const levelToBytes = (level: number, unit: string): number => {
  switch (unit) {
    case "B":
      return level;
    case "KB":
      return level * (2 ** 10);
    case "MB":
      return level * (2 ** 20);
    case "GB":
      return level * (2 ** 30);
    default:
      return 0;
  }
};

/** Watchers */
watch(() => props.dataUsage, (dataUsage) => {
  if (!dataUsage) {
    return;
  }

  controlEnabled.value = dataUsage.data_control_enabled;
  [controlUsage.value, controlUnit.value] = bytesToLevel(dataUsage.data_limit);
  controlResetDay.value = dataUsage.data_reset_day;
});

/** Callbacks */
const onDataAlertToggle = () => {
  if (!props.dataUsage) {
    return;
  }

  const newControl = { ...props.dataUsage };
  newControl.data_control_enabled = controlEnabled.value;

  emit('on-update', newControl);
};

const onSave = () => {
  if (!controlEnabled.value || !props.dataUsage) {
    return;
  }

  emit('on-update', {
    data_control_enabled: controlEnabled.value,
    data_limit: levelToBytes(controlUsage.value, controlUnit.value),
    data_reset_day: controlResetDay.value,
    last_reset_date: props.dataUsage.last_reset_date,
  });
};
</script>

<style scoped>
.v-card {
  border: 1px solid #ccc;
  border-radius: 8px;
}
</style>
