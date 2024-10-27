<template>
  <v-app>
    <v-main>
      <v-container>
        <SpinningLogo
          v-if="opLoading"
          subtitle="Fetching available modems"
        />
        <OperationError
          v-else-if="opError"
          title="Failed to load available modems"
          :subtitle="opError"
        />
        <div v-else>
          <modem-selector-view
            :modems="availableModems"
            @modemSelected="onModemSelected"
          />
          <modem-details-view v-if="selectedModem" :modem="selectedModem" />
        </div>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';

import ModemSelectorView from './views/ModemSelectorView.vue';
import ModemDetailsView from './views/ModemDetailsView.vue';
import SpinningLogo from './components/common/SpinningLogo.vue';
import OperationError from './components/common/OperationError.vue';

import { ModemDevice } from '@/types/ModemManager';
import ModemManager from '@/services/ModemManager';

import { sleep } from './utils';
import { OneMoreTime } from './one-more-time';


/** States */
const availableModems = ref<ModemDevice[]>([]);
const selectedModem = ref<ModemDevice | null>(null);

const opLoading = ref<boolean>(true);
const opError = ref<string | null>(null);

/** Utils */
const fetchAvailableModems = async () => {
  try {
    const modems = await ModemManager.fetchModems();

    /** Only update if have changes */
    if (JSON.stringify(availableModems.value) !== JSON.stringify(modems)) {
      availableModems.value = modems;
    }
  } catch (error) {
    opError.value = String((error as any)?.message);
  }
};

/** Callbacks */
const onModemSelected = (modem: ModemDevice) => {
  selectedModem.value = modem;
};

/** Tasks */
new OneMoreTime({ delay: 10000, disposeWith: this }, fetchAvailableModems);

/** Hooks */
onMounted(async () => {
  await fetchAvailableModems();

  /** Since this fetch is USUALLY fast we simulate a delay to avoid glitch */
  await sleep(600);
  opLoading.value = false;
});
</script>
