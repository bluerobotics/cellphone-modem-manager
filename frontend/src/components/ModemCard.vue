<template>
  <v-card class="modem-card" outlined>
    <div class="avatar-container">
      <img
        class="modem-thumbnail"
        :src="getThumbnailFromProduct(modem.product)"
        @error="(e: Event) => {(e.target as HTMLImageElement).src = defaultThumbnail;}"
        alt="Modem logo"
      />
    </div>
    <v-divider></v-divider>
    <v-card-title>{{ modem.manufacturer }} / {{ modem.product }}</v-card-title>
    <v-card-text>{{ getUSBFromDevice(modem.device) }}</v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { defineProps } from 'vue';

import { ModemDevice } from '@/types/ModemManager';
import defaultThumbnail from '@/assets/thumbs/unknown.svg';
import { getUSBFromDevice, getThumbnailFromProduct } from '@/utils';

defineProps<{
  modem: ModemDevice;
}>();
</script>

<style scoped>
.modem-card {
  width: 250px;
  max-width: 250px;
  border-radius: 5px;
  transition: transform 0.3s;
  box-sizing: border-box;
  -moz-box-sizing: border-box;
  -webkit-box-sizing: border-box;
  cursor: pointer;
}

.modem-card:hover {
  transform: translateY(-5px);
}

.avatar-container {
  display: flex;
  justify-content: center;
  padding-top: 10px;
}

.modem-thumbnail {
  width: 80%;
  min-height: 240px;
  object-fit: contain;
}

.v-divider {
  margin: 10px 0;
}
</style>
