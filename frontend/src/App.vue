<template>
  <v-app>
    <v-main>
      <modem-details-view
        v-if="selectedModem !== null"
        :modem="selectedModem"
        @back="onBack"
        @reboot="onModemReboot"
        @reset="onModemReset"
        @disable="onModemDisable"
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

const initLoad = (title: string = 'Fetching available modems') => {
  fetchAvailableModemTask.stop();
  selectedModem.value = null;
  availableModems.value = [];
  opLoading.value = true;
  opDescription.value = title;
}

const finishLoad = () => {
  opLoading.value = false;
  fetchAvailableModemTask.resume();
}

const initComponent = async () => {
  await initLoad();
  await fetchAvailableModems();

  /** Since this fetch is USUALLY fast we simulate a delay to avoid glitch */
  await sleep(500);
  await finishLoad();
}

const rebootModem = async (action: Promise<void>, title: string = 'Rebooting modem') => {
  await initLoad(title);
  await action;

  await sleep(15000);
  await fetchAvailableModems();
  await finishLoad();
}

/** Callbacks */
const onModemSelected = (modem: ModemDevice) => {
  selectedModem.value = modem;
};

const onBack = async () => {
  await initComponent();
};

const onModemReboot = async () => {
  if (selectedModem.value === null) {
    return;
  }

  try {
    rebootModem(ModemManager.rebootById(selectedModem.value?.id));
  } catch (error) {
    opError.value = String((error as any)?.message);
  }
};

const onModemReset = async () => {
  if (selectedModem.value === null) {
    return;
  }

  try {
    rebootModem(ModemManager.resetById(selectedModem.value?.id), 'Resetting modem');
  } catch (error) {
    opError.value = String((error as any)?.message);
  }
};

const onModemDisable = async () => {
  if (selectedModem.value === null) {
    return;
  }

  try {
    rebootModem(ModemManager.disableById(selectedModem.value?.id), 'Disabling modem');
  } catch (error) {
    opError.value = String((error as any)?.message);
  }
};

/** Tasks */
const fetchAvailableModemTask = new OneMoreTime({ delay: 10000, disposeWith: this }, fetchAvailableModems);

/** Hooks */
onMounted(async () => {
  await initComponent();
});
</script>
