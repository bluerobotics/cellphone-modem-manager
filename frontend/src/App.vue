<template>
  <v-app>
    <v-main>
      <modem-details-view
        v-if="selectedModem !== null"
        :modem="selectedModem"
        @back="onBack"
        @reboot="onModemReboot"
        @reset="onModemReset"
      />
      <v-container
        v-else
      >
        <SpinningLogo
          v-if="opLoading"
          :subtitle="opDescription"
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
const opDescription = ref<string>('');

/** Utils */
const fetchAvailableModems = async () => {
  try {
    const modems = await ModemManager.fetch();

    /** Only update if have changes */
    if (JSON.stringify(availableModems.value) !== JSON.stringify(modems)) {
      availableModems.value = modems;

      /** If current modem got disconnected */
      if (selectedModem.value !== null) {
        selectedModem.value = modems.find((modem) => modem.id === selectedModem.value?.id) ?? null;
      }
    }
  } catch (error) {
    opError.value = String((error as any)?.message);
  }
};

const initComponent = async (delay: number = 500, title: string = 'Fetching available modems') => {
  fetchAvailableModemTask.stop();
  opLoading.value = true;
  opDescription.value = title;
  await fetchAvailableModems();

  /** Since this fetch is USUALLY fast we simulate a delay to avoid glitch */
  await sleep(delay);
  opLoading.value = false;
  fetchAvailableModemTask.resume();
};

const initRebootComponent = async () => {
  selectedModem.value = null;
  availableModems.value = [];
  initComponent(10000, "Rebooting modem");
};

/** Callbacks */
const onModemSelected = (modem: ModemDevice) => {
  selectedModem.value = modem;
};

const onBack = () => {
  selectedModem.value = null;
  initComponent();
};

const onModemReboot = async () => {
  if (selectedModem.value === null) {
    return;
  }

  try {
    await ModemManager.rebootById(selectedModem.value?.id);

    initRebootComponent();
  } catch (error) {
    opError.value = String((error as any)?.message);
  }
};

const onModemReset = async () => {
  if (selectedModem.value === null) {
    return;
  }

  try {
    await ModemManager.resetById(selectedModem.value?.id);

    initRebootComponent();
  } catch (error) {
    opError.value = String((error as any)?.message);
  }
};

/** Tasks */
const fetchAvailableModemTask = new OneMoreTime({ delay: 10000, disposeWith: this }, fetchAvailableModems);

/** Hooks */
onMounted(async () => {
  initComponent();
});
</script>
