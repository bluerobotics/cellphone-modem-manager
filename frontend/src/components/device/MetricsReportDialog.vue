<template>
  <v-dialog
    :model-value="modelValue"
    @update:model-value="onDialogUpdate"
    :persistent="isRunning"
    max-width="800"
    scrollable
  >
    <v-card>
      <v-card-title class="d-flex align-center">
        <v-icon class="mr-2" :color="statusIconColor">
          {{ statusIcon }}
        </v-icon>
        {{ statusTitle }}
      </v-card-title>

      <v-divider />

      <v-card-text>
        <v-progress-linear
          v-if="isRunning"
          :model-value="progressPercent"
          color="primary"
          height="8"
          rounded
          class="mb-3"
        />

        <div v-if="isRunning && currentStepName" class="text-body-2 mb-3 font-weight-medium">
          Step {{ currentStep }} of {{ totalSteps }}: {{ currentStepName }}
        </div>

        <div v-if="errorMessage" class="text-body-2 mb-3 text-error">
          {{ errorMessage }}
        </div>

        <div ref="logContainer" class="report-log">
          <div v-for="(entry, i) in completedSteps" :key="i" class="log-entry">
            <div class="log-header">
              <v-icon size="16" color="success" class="mr-1">mdi-check-circle</v-icon>
              <span class="font-weight-medium">[{{ entry.step }}/{{ entry.total }}] {{ entry.name }}</span>
            </div>
            <pre class="log-output">{{ entry.command }}&#10;{{ entry.output }}</pre>
          </div>
          <div v-if="isRunning && currentStepName" class="log-entry current-step">
            <div class="log-header">
              <v-icon size="16" color="primary" class="mr-1 mdi-spin">mdi-loading</v-icon>
              <span class="font-weight-medium">[{{ currentStep }}/{{ totalSteps }}] {{ currentStepName }}</span>
            </div>
          </div>
        </div>
      </v-card-text>

      <v-divider />

      <v-card-actions>
        <v-spacer />
        <v-btn
          v-if="!isRunning && reportText"
          color="primary"
          variant="tonal"
          @click="downloadReport"
        >
          <v-icon class="mr-1">mdi-download</v-icon>
          Download Report
        </v-btn>
        <v-btn
          v-if="!isRunning"
          variant="text"
          @click="close"
        >
          Close
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, onUnmounted, nextTick } from 'vue'

import { streamReport } from '@/services/ModemManager'
import { ModemDevice, ReportEvent } from '@/types/ModemManager'

interface CompletedStep {
  step: number
  total: number
  name: string
  command: string
  output: string
}

const props = defineProps<{
  modelValue: boolean
  modem: ModemDevice
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
}>()

const logContainer = ref<HTMLElement | null>(null)
const isRunning = ref(false)
const errorMessage = ref('')
const completedSteps = ref<CompletedStep[]>([])
const currentStep = ref(0)
const totalSteps = ref(0)
const currentStepName = ref('')
const reportText = ref('')
let abortController: AbortController | null = null
let streaming = false

const progressPercent = computed(() => {
  if (totalSteps.value === 0) return 0
  return (completedSteps.value.length / totalSteps.value) * 100
})

const statusIcon = computed(() => {
  if (isRunning.value) return 'mdi-loading mdi-spin'
  if (errorMessage.value) return 'mdi-alert-circle'
  if (reportText.value) return 'mdi-check-circle'
  return 'mdi-file-chart'
})

const statusIconColor = computed(() => {
  if (isRunning.value) return 'primary'
  if (errorMessage.value) return 'error'
  if (reportText.value) return 'success'
  return 'grey'
})

const statusTitle = computed(() => {
  if (isRunning.value) return 'Generating Metrics Report...'
  if (errorMessage.value) return 'Report Generation Failed'
  if (reportText.value) return 'Metrics Report Complete'
  return 'Metrics Report'
})

const scrollToBottom = async () => {
  await nextTick()
  if (logContainer.value) {
    logContainer.value.scrollTop = logContainer.value.scrollHeight
  }
}

const handleEvent = (event: ReportEvent) => {
  switch (event.type) {
    case 'step_start':
      currentStep.value = event.step ?? 0
      totalSteps.value = event.total ?? 0
      currentStepName.value = event.name ?? ''
      scrollToBottom()
      break

    case 'step_complete':
      completedSteps.value.push({
        step: event.step ?? 0,
        total: event.total ?? 0,
        name: event.name ?? '',
        command: event.command ?? '',
        output: event.output ?? '',
      })
      scrollToBottom()
      break

    case 'report_complete':
      reportText.value = event.report ?? ''
      isRunning.value = false
      currentStepName.value = ''
      scrollToBottom()
      break

    case 'error':
      errorMessage.value = event.message ?? 'Unknown error occurred'
      break
  }
}

const startStreaming = async () => {
  if (streaming) return
  streaming = true
  isRunning.value = true
  errorMessage.value = ''
  completedSteps.value = []
  currentStep.value = 0
  totalSteps.value = 0
  currentStepName.value = ''
  reportText.value = ''

  abortController = new AbortController()

  try {
    await streamReport(props.modem.id, handleEvent, abortController.signal)
  } catch (error) {
    if (error instanceof Error && error.name !== 'AbortError') {
      errorMessage.value = error.message
      isRunning.value = false
    }
  } finally {
    streaming = false
    if (isRunning.value) {
      isRunning.value = false
    }
  }
}

const downloadReport = () => {
  const blob = new Blob([reportText.value], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = `modem-diagnostic-report-${new Date().toISOString().replace(/[:.]/g, '-')}.txt`
  anchor.click()
  URL.revokeObjectURL(url)
}

const close = () => {
  emit('update:modelValue', false)
}

const onDialogUpdate = (value: boolean) => {
  if (!value && isRunning.value) return
  emit('update:modelValue', value)
}

watch(() => props.modelValue, (open) => {
  if (open && !streaming) {
    startStreaming()
  }
})

onUnmounted(() => {
  abortController?.abort()
})
</script>

<style scoped>
.report-log {
  max-height: 50vh;
  overflow-y: auto;
  font-size: 13px;
  background: #1e1e1e;
  border-radius: 8px;
  padding: 12px;
}

.log-entry {
  margin-bottom: 8px;
}

.log-header {
  display: flex;
  align-items: center;
  color: #e0e0e0;
  padding: 2px 0;
}

.log-output {
  margin: 2px 0 0 24px;
  padding: 4px 8px;
  background: #2a2a2a;
  border-radius: 4px;
  color: #b0b0b0;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  white-space: pre-wrap;
  word-break: break-all;
  overflow-x: auto;
}

.current-step .log-header {
  color: #90caf9;
}
</style>
