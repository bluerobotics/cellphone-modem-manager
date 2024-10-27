<template>
  <div v-if="selectedModem">
    <v-card rounded="0" flat>
      <v-card height="80px" class="custom-rounded-select" flat>
        <v-select
          v-model="selectedModem"
          :items="modems"
          variant="solo-filled"
          @update:model-value="onSelectModem"
        >
          <template v-slot:selection="{ item }">
            <ModemItem v-if="item" :modem="item.raw" />
          </template>
          <template v-slot:item="{ props, item }">
            <ModemItem v-if="item" :list-props="props" :modem="item.raw" />
          </template>
        </v-select>
      </v-card>
    </v-card>
  </div>
  <div v-else>
    <v-row class="justify-center">
    <h1>Available modems</h1>
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
import ModemItem from '@/components/ModemItem.vue';
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
