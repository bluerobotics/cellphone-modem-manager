<template>
  <v-card>
    <v-card-subtitle class="px-4 pt-4 pb-2 d-flex justify-space-between align-start">
      <v-avatar size="100" rounded="0">
        <img
          class="modem-thumbnail"
          :src="getThumbnailFromProduct(modem.product)"
          @error="(e: Event) => {(e.target as HTMLImageElement).src = defaultThumbnail;}"
          alt="Modem logo"
        />
      </v-avatar>
      <div class="modem-details">
        <div class="modem-details-title my-2">
          {{ modem.manufacturer }} / {{ modem.product }}
        </div>
        <div class="modem-details-device">
          {{ modem.device }}
        </div>
        <div class="modem-details-usb">
          <strong>{{ getUSBFromDevice(modem.device) }}</strong>
        </div>
      </div>
    </v-card-subtitle>
    <v-divider />
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
.modem-thumbnail {
  width: 100%;
  height: 100%;
}
.modem-details {
  flex-grow: 1;
  margin-left: 10px;
}
.modem-details-title {
  font-weight: bold;
  font-size: 30px;
}
.modem-details-device {
  color: gray;
  font-size: 14px;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
  text-overflow: ellipsis;
}
.modem-details-usb {
  color: gray;
  font-size: 15px;
  padding-top: 4px;
  text-transform: uppercase;
}
</style>
