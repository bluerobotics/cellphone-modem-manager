<template>
  <div class="sim-status">
    <v-icon
      :icon="simIcon"
      size="100"
    />
    <div class="operator-info">
      <div v-if="simStatus === ModemSIMStatus.CONNECTED">
        <p><strong>OPERATOR: {{ operatorInfo?.operator || 'Unknown' }}</strong></p>
        <p><strong>TECH: {{ operatorTech }}</strong></p>
      </div>
      <p v-else-if="simStatus === ModemSIMStatus.DISCONNECTED">
        <strong>DISCONNECTED</strong>
      </p>
      <p v-else>
        <strong>UNKNOWN</strong>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed, defineProps } from 'vue';
import ModemManager from '@/services/ModemManager';
import { ModemDevice, OperatorAct, ModemSIMStatus, OperatorInfo } from '@/types/ModemManager';
import { OneMoreTime } from '@/one-more-time';

const props = defineProps<{
  modem: ModemDevice;
}>();

/** States */
const simStatus = ref<ModemSIMStatus>(ModemSIMStatus.UNKNOWN);
const operatorInfo = ref<OperatorInfo | null>();

/** Utils */
const getOperatorActName = (value: OperatorAct | undefined): string | undefined => {
  return Object.keys(OperatorAct).find(key => OperatorAct[key as keyof typeof OperatorAct] === value);
};

const fetchSIMStatus = async () => {
  try {
    simStatus.value = await ModemManager.fetchSIMStatusById(props.modem.id);
  } catch (error) {
    console.error("Failed to fetch SIM status from modem device", error);
  }
};

const fetchOperatorInfo = async () => {
  try {
    operatorInfo.value = await ModemManager.fetchOperatorInfoById(props.modem.id);
  } catch (error) {
    operatorInfo.value = null;
    console.error("Failed to fetch operator info from modem device", error);
  }
};

/** Computed */
const simIcon = computed(() => {
  switch (simStatus.value) {
    case ModemSIMStatus.CONNECTED:
      return 'mdi-sim';
    case ModemSIMStatus.DISCONNECTED:
      return 'mdi-sim-off';
    default:
      return 'mdi-sim-alert';
  }
});

const operatorTech = computed<string>(() => {
  return getOperatorActName(operatorInfo.value?.act) ?? 'N/A';
});

/** Tasks */
new OneMoreTime({ delay: 10000, disposeWith: this }, fetchSIMStatus);
const fetch_operator_task = new OneMoreTime({ delay: 30000, disposeWith: this }, fetchOperatorInfo);

/** Watcher */
watch(simStatus, (newVal) => {
  if (newVal === ModemSIMStatus.CONNECTED) {
    fetch_operator_task.resume();
  } else {
    fetch_operator_task.stop();
  }
});
</script>

<style scoped>
.sim-status {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.operator-info {
  margin-top: 10px;
}
</style>
