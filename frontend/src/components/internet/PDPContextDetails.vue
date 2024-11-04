<template>
  <v-card class="align-center text-center" elevation="0">
    <v-card-title class="ma-0 pa-0 text-center">
      Modem PDP Contexts
    </v-card-title>
    <v-card-text class="pt-2" style="margin: 0; padding: 0;">
      <v-row class="virtual-table-row">
        <v-col class="virtual-table-cell virtual-table-small">
          <strong>PROFILE</strong>
        </v-col>
        <v-col class="virtual-table-cell">
          <strong>PROTOCOL</strong>
        </v-col>
        <v-col class="virtual-table-cell">
          <strong>APN</strong>
        </v-col>
        <v-col class="virtual-table-cell virtual-table-small">
          <strong>EDIT</strong>
        </v-col>
      </v-row>
    </v-card-text>
    <v-virtual-scroll
      :items="pdpContext"
      height="300"
      item-height="50"
      class="virtual-table"
    >
      <template #default="{ item }">
        <v-row class="virtual-table-row">
          <v-col class="virtual-table-cell virtual-table-small">
            {{ item.context_id }}
          </v-col>
          <v-col class="virtual-table-cell">
            {{ getPDPProtocolName(item.protocol) ?? '-' }}
          </v-col>
          <v-col class="virtual-table-cell">
            {{ item.access_point_name }}
          </v-col>
          <v-col class="virtual-table-cell virtual-table-small">
            <v-btn
              color="primary"
              size="small"
              style="margin: 0; padding: 0;"
              @click="onOpenEditPDPModal(item)"
              icon="mdi-pencil"
            />
          </v-col>
        </v-row>
      </template>
    </v-virtual-scroll>
  </v-card>
  <v-dialog v-model="showEditPDPDialog" max-width="400px">
    <v-card class="pa-2">
      <v-card-title>Editing PDP {{ editingPDP?.context_id ?? '-' }}</v-card-title>
      <div v-if="!savingAPN">
        <v-card-text>New APN for this profile</v-card-text>
        <v-text-field
          v-model="pdpAPN"
          class="mx-3"
          label="APN"
          outlined
          dense
          variant="solo-filled"
          style="padding: 8px;"
        />
      </div>
      <SpinningLogo
        v-else
        subtitle="Saving new APN"
      />

      <v-card-actions class="justify-center pa-2">
        <v-spacer></v-spacer>
        <v-btn
          color="primary"
          :disabled="savingAPN"
          @click="onCloseEditPDPModal"
        >
          Cancel
        </v-btn>
        <v-btn
          :disabled="savingAPN"
          color="red" @click="onEditPDP"
        >
          Confirm
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, defineProps } from 'vue';
import ModemManager from '@/services/ModemManager';
import { ModemDevice, PDPContext, PDPType } from '@/types/ModemManager';
import { OneMoreTime } from '@/one-more-time';
import SpinningLogo from '@/components/common/SpinningLogo.vue';

const props = defineProps<{
  modem: ModemDevice;
}>();

/** States */
const pdpContext = ref<PDPContext[]>([]);
const editingPDP = ref<PDPContext | null>(null);
const pdpAPN = ref<string>('');
const showEditPDPDialog = ref(false);
const savingAPN = ref(false);

/** Utils */
const fetchPDPContext = async () => {
  try {
    pdpContext.value = await ModemManager.fetchPDPInfoById(props.modem.id);
  } catch (error) {
    console.error("Failed to fetch PDP info", error);
  }
};

const getPDPProtocolName = (value: PDPType): string | undefined => {
  return Object.keys(PDPType).find(key => PDPType[key as keyof typeof PDPType] === value);
}

/** Callbacks */
const onOpenEditPDPModal = (pdp: PDPContext) => {
  editingPDP.value = pdp;
  showEditPDPDialog.value = true;
}

const onCloseEditPDPModal = () => {
  editingPDP.value = null;
  showEditPDPDialog.value = false;
}

const onEditPDP = async () => {
  try {
    if (!editingPDP.value) {
      throw new Error('No PDP context selected for editing');
    }
    savingAPN.value = true;

    await ModemManager.setAPNByProfileById(props.modem.id, editingPDP.value.context_id, pdpAPN.value);
    await fetchPDPContext();
    onCloseEditPDPModal();
  } catch (error) {
    console.error('Failed to edit PDP', error);
  } finally {
    savingAPN.value = false;
  }
}

/** Tasks */
new OneMoreTime({ delay: 30000, disposeWith: this }, fetchPDPContext);
</script>

<style scoped>
.no-info-available {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 350px;
}

.virtual-table-row {
  display: flex;
  margin: 0;
  padding-bottom: 5px;
  margin-bottom: 5px;
  border-bottom: 1px solid #eee;
  flex-wrap: nowrap;
  justify-content: center;
  align-items: center;
}

.virtual-table-cell {
  flex: 2;
  padding: 5px;
  min-width: 60px;
  text-wrap: nowrap;
}

.virtual-table-small {
  flex: 1;
  min-width: 60px;
  text-wrap: nowrap;
}

.virtual-table {
  overflow-x: hidden;
}
</style>
