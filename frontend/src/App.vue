<template>
  <v-app>
    <v-main>
      <v-container>
        <modem-selector
          :modems="availableModems"
          @modemSelected="handleModemSelection"
        />
        <v-row v-if="selectedModem">
          <v-col>
            <v-card>
              <v-card-title>Selected Modem</v-card-title>
              <v-card-text>
                <p>Device: {{ selectedModem.device }}</p>
                <p>Manufacturer: {{ selectedModem.manufacturer }}</p>
                <p>Product: {{ selectedModem.product }}</p>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import ModemSelector from './components/ModemSelector.vue';
import ModemManager from '@/services/ModemManager';
import { ModemDevice } from '@/types/ModemManager';

const availableModems = ref<ModemDevice[]>([]);
const selectedModem = ref<ModemDevice | null>(null);

async function loadModems() {
  try {
    const modems = await ModemManager.fetchModems();
    availableModems.value = modems;
  } catch (error) {
    console.error("Failed to load modems:", error);
  }
}

function handleModemSelection(modem: ModemDevice) {
  selectedModem.value = modem;
}

onMounted(loadModems);
</script>

<script lang="ts">
export default {
  components: { ModemSelector }
};
</script>
