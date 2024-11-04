<template>
  <v-container fluid class="modem-details-container">
    <v-toolbar class="toolbar-container" flat>
      <v-btn icon @click="onBack">
        <v-icon size="30">mdi-arrow-left</v-icon>
      </v-btn>
      <v-toolbar-title>{{ props.modem.manufacturer }} / {{ props.modem.product }}</v-toolbar-title>
    </v-toolbar>

    <v-row class="d-flex align-center justify-space-between">
      <div class="header-section d-flex align-center">
        <img
          :src="getThumbnailFromProduct(modem.product)"
          class="modem-thumb"
          alt="Logo"
          @error="(e: Event) => {(e.target as HTMLImageElement).src = defaultThumbnail;}"
        />
        <v-col class="modem-details">
          <div class="modem-details-usb">
            {{ getUSBFromDevice(modem.device) }}
          </div>
          <div class="modem-details-usb">
            {{ currentClock ? new Date(currentClock).toLocaleString() : '' }} / GMT: {{ currentClockGmtOffset }}
          </div>
          <div class="modem-details-device">
            {{ props.modem.device }}
          </div>
        </v-col>
      </div>

      <div class="action-buttons d-flex justify-md-end justify-xs-start">
        <v-btn
          class="ma-2"
          color="primary"
          @click="onReboot"
        >
          Reboot
        </v-btn>
      </div>
    </v-row>

    <v-row class="tabs-container">
      <v-tabs v-model="selectedTab" grow>
        <v-tab value="device">Device</v-tab>
        <v-tab value="network">Network</v-tab>
        <v-tab value="internet">Internet</v-tab>
        <v-tab value="usage">Usage</v-tab>
      </v-tabs>
    </v-row>

    <v-row class="tab-content">
      <v-col cols="12">
        <v-card>
          <v-card-text>
            <v-tabs-window v-model="selectedTab">
              <v-tabs-window-item value="device">
                <DeviceDetailsTab :modem="props.modem" @reset="onReset" />
              </v-tabs-window-item>

              <v-tabs-window-item value="network">
                <NetworkDetailsTab :modem="props.modem" />
              </v-tabs-window-item>

              <v-tabs-window-item value="internet">
                <InternetDetailsTab :modem="props.modem" />
              </v-tabs-window-item>

              <v-tabs-window-item value="usage">
                <UsageDetailsTab :modem="props.modem" />
              </v-tabs-window-item>
            </v-tabs-window>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, defineProps } from 'vue';

import defaultThumbnail from "@/assets/thumbs/unknown.svg";

import ModemManager from '@/services/ModemManager';
import { ModemDevice, ModemClockDetails } from '@/types/ModemManager';

import NetworkDetailsTab from '@/components/network/NetworkDetailsTab.vue';
import DeviceDetailsTab from '@/components/device/DeviceDetailsTab.vue';
import InternetDetailsTab from '@/components/internet/InternetDetailsTab.vue';
import UsageDetailsTab from '@/components/usage/UsageDetailsTab.vue';

import { getThumbnailFromProduct, getUSBFromDevice } from '@/utils';
import { OneMoreTime } from '@/one-more-time';

const props = defineProps<{
  modem: ModemDevice;
}>();
const emit = defineEmits<(event: 'reboot' | 'back' | 'reset') => void>();

/** States */
const selectedTab = ref<number>(0);
const currentClockGmtOffset = ref<number>(0);
const currentClock = ref<number | null>(null);

/** Utils */
const clockToUnix = (clock: ModemClockDetails) => {
  const { date, time, gmt_offset } = clock;

  const [year, month, day] = date.split('/').map(Number);
  const [hours, minutes, seconds] = time.split(':').map(Number);

  const baseYear = Math.floor(new Date().getFullYear() / 1000) * 1000;
  const fullYear = year + baseYear;

  const utcDate = new Date(Date.UTC(fullYear, month - 1, day, hours, minutes, seconds));

  // Adjust for GMT offset
  const utcTimestamp = utcDate.getTime();
  return utcTimestamp - gmt_offset * 3600 * 1000;
}

const fetchClock = async () => {
  try {
    const clock = await ModemManager.fetchClockById(props.modem.id);
    currentClockGmtOffset.value = clock.gmt_offset;
    currentClock.value = clockToUnix(clock);
  } catch (error) {
    console.error("Unable to fetch clock details from modem device", error);
  }
};

const incrementClockLocally = () => {
  if (currentClock.value) {
    currentClock.value += 1000;
  }
};

/** Tasks */
new OneMoreTime({delay: 60000, disposeWith: this}, fetchClock);
new OneMoreTime({delay: 1000, disposeWith: this}, incrementClockLocally);

/** Callbacks */
const onReboot = () => {
  emit('reboot');
};

const onBack = () => {
  emit('back');
};

const onReset = () => {
  emit('reset');
};
</script>

<style scoped>
.modem-details-container {
  width: 80%;
  min-width: 450px;
}

@media (max-width: 1024px) {
  .modem-details-container {
    width: 95%;
  }
}

.toolbar-container {
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  min-width: 400px;
  width: 30%;
  border-bottom-right-radius: 25px;
}

.back-label {
  font-size: 16px;
  margin-right: 8px;
  color: #424242;
}

.header-section {
  padding: 15px;
}

.modem-thumb {
  margin-right: 16px;
  height: 100px;
  max-height: 100px;
  object-fit: contain;
}

.modem-details {
  flex-grow: 1;
}

.modem-details-device {
  color: gray;
  font-size: 14px;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 1;
  overflow: hidden;
  text-overflow: ellipsis;
}

.modem-details-usb {
  color: gray;
  font-size: 20px;
  padding-top: 4px;
  text-transform: uppercase;
}

.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tabs-container {
  margin-top: 16px;
}

.tab-content {
  margin-top: 16px;
}
</style>
