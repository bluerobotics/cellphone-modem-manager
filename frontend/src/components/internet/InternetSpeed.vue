<template>
  <v-card class="pa-2" max-width="450px" elevation="0">
    <v-card-title class="ma-0 pa-0 text-center">
      Internet Speed and Latency Test
    </v-card-title>
    <v-divider class="mt-3"/>
    <v-card-text class="pt-5">
      <v-row>
        <v-col cols="12" :md="result ? 4 : 3"></v-col>
        <v-col cols="12" md="6">
          <v-row class="pt-7 align-center" :class="result ? 'justify-left' : 'justify-center'">
            <v-icon v-tooltip="'Server to test internet speed'">
              mdi-server-network
            </v-icon>
            <v-list-item-subtitle class="ml-3">
              {{ server }}
            </v-list-item-subtitle>
          </v-row>
          <v-row class="pt-7 align-center" :class="result ? 'justify-left' : 'justify-center'">
            <v-icon v-tooltip="'Client provider'">
              mdi-home-circle-outline
            </v-icon>
            <v-list-item-subtitle class="ml-3">
              {{ client }}
              <v-list
                v-if="clientRating"
                v-tooltip="'Provider ISP rating'"
                class="d-flex justify-center"
              >
                (
                <div>
                  <v-icon
                    v-for="index in 5"
                    :key="index"
                    size="small"
                  >
                    {{ getRateIcon(index, clientRating) }}
                  </v-icon>
                </div>
                )
              </v-list>
            </v-list-item-subtitle>
          </v-row>
          <v-row class="pt-7 align-center" :class="result ? 'justify-left' : 'justify-center'">
            <v-icon v-tooltip="'Download speed from internet'">
              mdi-download
            </v-icon>
            <v-list-item-subtitle class="ml-3">
              {{ downloadSpeed }}
            </v-list-item-subtitle>
          </v-row>
          <v-row class="pt-7 align-center" :class="result ? 'justify-left' : 'justify-center'">
            <v-icon v-tooltip="'Upload speed to internet'">
              mdi-upload
            </v-icon>
            <v-list-item-subtitle class="ml-3">
              {{ uploadSpeed }}
            </v-list-item-subtitle>
          </v-row>
          <v-row class="pt-7 align-center" :class="result ? 'justify-left' : 'justify-center'">
            <v-icon v-tooltip="'Latency'">
              mdi-timer-outline
            </v-icon>
            <v-list-item-subtitle class="ml-3">
              {{ latency }}
            </v-list-item-subtitle>
          </v-row>
        </v-col>
        <v-col cols="12" md="3"></v-col>
      </v-row>
    </v-card-text>

    <v-card-text class="text-center">{{ operationMessage }}</v-card-text>

    <v-card-actions class="justify-center">
      <v-icon v-if="testInProgress">
        mdi-loading mdi-spin
      </v-icon>
      <v-btn
        v-else
        color="primary"
        @click="startTest"
      >
        <v-icon left>mdi-play</v-icon> Start Test
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';

import InternetManager from '@/services/InternetManager';
import { SpeedTestResult } from '@/types/InternetManager';

/** States */
const operationMessage = ref('');
const result = ref<SpeedTestResult | null>(null);
const testInProgress = ref(false);

/** Computed */
const server = computed((): string => {
  if (!result.value || !result.value.server) return 'N/A';

  return `${result.value.server.country} - ${result.value.server.name}`
})

const client = computed((): string => {
  if (!result.value || !result.value.client) return 'N/A';

  return result.value.client.isp
})

const clientRating = computed((): number | null => {
  if (!result.value || !result.value.client || !result?.value?.client?.isprating) return null;

  return parseFloat(result?.value?.client?.isprating ?? 0)
})

const downloadSpeed = computed((): string => {
  if (!result.value || !result.value.download) return 'N/A';

  return `${Math.round(result.value.download / 2 ** 20)} Mbps`
})

const uploadSpeed = computed((): string => {
  if (!result.value || !result.value.upload) return 'N/A';

  return `${Math.round(result.value.upload / 2 ** 20)} Mbps`
})

const latency = computed((): string => {
  if (!result.value || !result.value.ping) return 'N/A';

  return `${result.value.ping} ms`
})

/** Utils */
const getRateIcon = (index: number, rate: number): string => {
  if (index <= rate) {
    return 'mdi-star'
  }

  if (index > rate && rate > index - 1) {
    return 'mdi-star-half-full'
  }

  return 'mdi-star-outline'
};

/** Callbacks */
const startTest = async () => {
  result.value = null;
  testInProgress.value = true;
  operationMessage.value = 'Starting.. Looking for best server.'
  result.value = await InternetManager.checkInternetBestServer()
  operationMessage.value= 'Checking download speed.'
  result.value = await InternetManager.checkInternetDownloadSpeed()
  operationMessage.value = 'Checking upload speed.'
  result.value = await InternetManager.checkInternetUploadSpeed()
  operationMessage.value = 'Done!'
  testInProgress.value = false;
};
</script>
