<template>
  <v-list-item
    v-bind="listProps"
    :title="`${ modem.manufacturer } / ${ modem.product }`"
    :subtitle="getUSBFromDevice(modem.device)"
  >
    <template v-slot:prepend>
      <div class="prepend-image-container">
        <img
          :height="height"
          :src="getThumbnailFromProduct(modem.product)"
          @error="(e: Event) => {(e.target as HTMLImageElement).src = defaultThumbnail;}"
          alt="Logo"
        />
      </div>
    </template>
  </v-list-item>
</template>

<script setup lang="ts">
import { defineProps } from 'vue';

import { ModemDevice } from '@/types/ModemManager';
import defaultThumbnail from '@/assets/thumbs/unknown.svg';
import { getUSBFromDevice, getThumbnailFromProduct } from '@/utils';

withDefaults(defineProps<{
  modem: ModemDevice;
  height?: string;
  listProps?: Record<string, unknown>;
}>(), {
  height: '30px',
});
</script>

<style scoped>
.prepend-image-container {
  width: 100%;
  height: 100%;
  min-width: 35px;
  display: flex;
  align-items: center;
  margin-right: 27px;
}

.v-list-item {
  align-items: center;
}
</style>
