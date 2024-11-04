<template>
  <div>
    <v-row class="selector-container">
      <OperationError
        v-if="modems.length === 0"
        class="magnify-animation"
        icon="mdi-magnify-remove-outline"
        color="white"
        title="No modems found"
        subtitle="Scanning for new modems"
      />
      <h1 v-else>
        Available modems
      </h1>
    </v-row>
    <v-row class="align-center justify-center">
      <v-col
        v-for="modem in modems"
        :key="modem.device"
        cols="auto"
        @click="onSelectModem(modem)"
      >
        <ModemCard :modem="modem" />
      </v-col>
    </v-row>
  </div>
</template>

<script setup lang="ts">
import { defineProps, ref } from 'vue';

import { ModemDevice } from '@/types/ModemManager';
import ModemCard from '@/components/ModemCard.vue';
import OperationError from '@/components/common/OperationError.vue';

defineProps<{
  modems: ModemDevice[];
}>();
const emit = defineEmits<(event: 'modemSelected', modem: ModemDevice) => void>();

/** States */
const selectedModem = ref<ModemDevice | null>(null);

/** Callbacks */
const onSelectModem = (modem: ModemDevice) => {
  selectedModem.value = modem;
  emit("modemSelected", modem);
};
</script>

<style scoped>
.selector-container {
  margin-top: 5%;
  justify-content: center;
}

.custom-rounded-select {
  width: 100%;
  max-width: 400px;
  border-bottom-right-radius: 25px !important;
}

.v-select .v-list-item {
  align-items: center;
}
</style>

<style>
.magnify-animation .op-error-icon {
  animation: float 3s ease-in-out infinite !important;
}

@keyframes float {
  0% {
    transform: translate(0px, 0px) rotate(0deg);
  }
  25% {
    transform: translate(10px, -10px) rotate(15deg);
  }
  50% {
    transform: translate(0px, -20px) rotate(0deg);
  }
  75% {
    transform: translate(-10px, -10px) rotate(-15deg);
  }
  100% {
    transform: translate(0px, 0px) rotate(0deg);
  }
}
</style>
