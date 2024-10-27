<template>
  <div>
    <v-row class="justify-center">
      <div v-if="modems.length == 0">
        <h1>No modems found</h1>
        <h4 class="mt-3">Scanning for new modems...</h4>
      </div>
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
import { defineEmits, defineProps, ref } from 'vue';

import { ModemDevice } from '@/types/ModemManager';
import ModemCard from '@/components/ModemCard.vue';

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
.custom-rounded-select {
  width: 100%;
  max-width: 400px;
  border-bottom-right-radius: 25px !important;
}

.v-select .v-list-item {
  align-items: center;
}
</style>
