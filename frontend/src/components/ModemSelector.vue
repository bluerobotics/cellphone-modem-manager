<template>
  <v-row class="justify-center">
    <v-col
      v-for="modem in modems"
      :key="modem.device"
      cols="auto"
      class="modem-card"
      @click="selectModem(modem)"
    >
      <v-card :class="{ 'selected-card': modem.device === selectedModem }" outlined>
        <v-card-avatar class="avatar-container">
          <img class="thumbnail" :src="getThumbnail(modem.product)" alt="Modem logo" />
        </v-card-avatar>
        <v-divider></v-divider>
        <v-card-title>{{ modem.manufacturer }} / {{ modem.product }}</v-card-title>
        <v-card-text>{{ getUsbId(modem.device) }}</v-card-text>
      </v-card>
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import { ref, defineProps, defineEmits } from 'vue';
import { ModemDevice } from '@/types/ModemManager';

defineProps<{
  modems: ModemDevice[];
}>();

const emit = defineEmits<(event: 'modemSelected', modem: ModemDevice) => void>();

const selectedModem = ref<string | null>(null);

const getThumbnail = (product: string): string => `/static/thumbs/${product.toLowerCase()}.png`;

const getUsbId = (device: string): string => {
  const usbIdentifierRegex = /\/(usb\d+)/;
  const match = device.match(usbIdentifierRegex);

  return match ? match[1].toUpperCase() : "UNKNOWN";
};

function selectModem(modem: ModemDevice): void {
  selectedModem.value = modem.device;
  emit("modemSelected", modem);
}
</script>

<style scoped>
.selected-card {
  border-color: #007bff;
  border-width: 2px;
  transform: scale(1.05);
}

.modem-card {
  width: 300px;
  border-radius: 5px;
  transition: transform 0.3s;
  box-sizing: border-box;
  -moz-box-sizing: border-box;
  -webkit-box-sizing: border-box;
}

.modem-card:hover {
  transform: translateY(-5px);
}

.avatar-container {
  display: flex;
  justify-content: center;
  padding-top: 10px;
}

.thumbnail {
  width: 80%;
  object-fit: contain;
}

.v-divider {
  margin: 10px 0; /* Spacing for the divider */
}
</style>
