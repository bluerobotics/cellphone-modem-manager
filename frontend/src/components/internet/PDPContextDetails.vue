<template>
  <v-card class="align-center text-center" elevation="0">
    <v-card-title class="ma-0 pa-0 text-center">
      Modem PDP Contexts
      <v-icon
        @click="showInfoDialog = true"
        size="24"
        class="ml-2"
      >
        mdi-information-outline
      </v-icon>
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
        <v-card-text>Configure the APN and authentication parameters for this profile.</v-card-text>
        <v-text-field
          v-model="pdpAPN"
          class="mx-3"
          label="APN"
          outlined
          dense
          variant="solo-filled"
          style="padding: 8px;"
        />
        <v-select
          v-if="isDevMode"
          v-model="pdpProtocol"
          class="mx-3"
          :items="pdpProtocolOptions"
          label="Protocol"
          dense
          variant="solo-filled"
          style="padding: 8px;"
        />
        <v-switch
          v-model="updateAuthentication"
          class="mx-3"
          color="primary"
          inset
          label="Update authentication settings"
        />
        <v-text-field
          v-model="pdpUsername"
          class="mx-3"
          label="Username"
          outlined
          dense
          variant="solo-filled"
          style="padding: 8px;"
          :disabled="!updateAuthentication"
        />
        <v-text-field
          v-model="pdpPassword"
          class="mx-3"
          label="Password"
          :type="showPassword ? 'text' : 'password'"
          outlined
          dense
          variant="solo-filled"
          style="padding: 8px;"
          :disabled="!updateAuthentication"
          :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
          @click:append-inner="showPassword = !showPassword"
        />
        <v-select
          v-model="pdpAuthentication"
          class="mx-3"
          :items="pdpAuthenticationOptions"
          item-title="label"
          item-value="value"
          label="Authentication"
          dense
          variant="solo-filled"
          style="padding: 8px;"
          :disabled="!updateAuthentication"
        />
      </div>
      <SpinningLogo
        v-else
        subtitle="Saving PDP configuration"
      />

      <v-alert
        v-if="editPDPError"
        class="mx-3 mt-2"
        type="error"
        variant="tonal"
      >
        {{ editPDPError }}
      </v-alert>

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
  <v-dialog v-model="showInfoDialog" max-width="550px">
    <v-card class="pa-2">
      <v-card-title>PDP Context Information</v-card-title>
      <v-card-text class="text-justify">
        A <strong>PDP (Packet Data Protocol) context</strong> specifies parameters for a connection between the modem and the mobile network.

        <v-divider class="my-2"></v-divider>

        <strong>Each PDP context consists of:</strong>
        <ul class="ml-4">
          <li><strong>Profile:</strong> Identifies the context number.</li>
          <li><strong>Protocol:</strong> Defines the protocol type (e.g., IPv4, IPv6, IPv4v6).</li>
          <li><strong>APN: </strong> Acts as a gateway between a mobile network (GSM, GPRS, 3G, 4G) and another network, such as the public or private Internet</li>
        </ul>

        <v-divider class="my-2"></v-divider>

        <strong>Note:</strong> For <strong>private connections</strong>, the service provider may supply a specific <strong>APN</strong>, which users must configure to access the private network.
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="primary" @click="showInfoDialog = false">Got it</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, defineProps, watch } from 'vue';
import ModemManager from '@/services/ModemManager';
import { ModemDevice, PDPAuthenticationType, PDPContext, PDPType } from '@/types/ModemManager';
import { OneMoreTime } from '@/one-more-time';
import SpinningLogo from '@/components/common/SpinningLogo.vue';
import { isDevMode } from '@/storage';

const props = defineProps<{
  modem: ModemDevice;
}>();

/** States */
const pdpContext = ref<PDPContext[]>([]);
const editingPDP = ref<PDPContext | null>(null);
const pdpAPN = ref<string>('');
const pdpProtocol = ref<PDPType>(PDPType.IP);
const pdpUsername = ref<string>('');
const pdpPassword = ref<string>('');
const pdpAuthentication = ref<PDPAuthenticationType>(PDPAuthenticationType.NONE);
const updateAuthentication = ref(false);
const showEditPDPDialog = ref(false);
const showInfoDialog = ref(false);
const savingAPN = ref(false);
const showPassword = ref(false);
const editPDPError = ref('');
const pdpProtocolOptions = Object.values(PDPType);
const pdpAuthenticationOptions = [
  { label: 'None', value: PDPAuthenticationType.NONE },
  { label: 'PAP', value: PDPAuthenticationType.PAP },
  { label: 'CHAP', value: PDPAuthenticationType.CHAP },
  { label: 'PAP or CHAP', value: PDPAuthenticationType.PAP_OR_CHAP },
];

/** Utils */
const fetchPDPContext = async (devMode?: boolean) => {
  try {
    pdpContext.value = await ModemManager.fetchPDPInfoById(props.modem.id);

    /** In case user is not on dev mode only shows PDP profile with ID 1 */
    const mode = devMode ?? isDevMode.value;
    if (!mode) {
      pdpContext.value = pdpContext.value.filter(pdp => pdp.context_id === 1);
    }
  } catch (error) {
    console.error("Failed to fetch PDP info", error);
  }
};

const getPDPProtocolName = (value: PDPType): string | undefined => {
  return Object.keys(PDPType).find(key => PDPType[key as keyof typeof PDPType] === value);
}

/** Callbacks */
const resetPDPForm = () => {
  pdpAPN.value = '';
  pdpProtocol.value = PDPType.IP;
  pdpUsername.value = '';
  pdpPassword.value = '';
  pdpAuthentication.value = PDPAuthenticationType.NONE;
  updateAuthentication.value = false;
  showPassword.value = false;
};

const onOpenEditPDPModal = (pdp: PDPContext) => {
  editingPDP.value = pdp;
  pdpAPN.value = pdp.access_point_name ?? '';
  pdpProtocol.value = pdp.protocol ?? PDPType.IP;
  pdpUsername.value = '';
  pdpPassword.value = '';
  pdpAuthentication.value = PDPAuthenticationType.NONE;
  updateAuthentication.value = false;
  showPassword.value = false;
  editPDPError.value = '';
  showEditPDPDialog.value = true;
}

const onCloseEditPDPModal = () => {
  editingPDP.value = null;
  showEditPDPDialog.value = false;
  editPDPError.value = '';
  resetPDPForm();
}

const onEditPDP = async () => {
  editPDPError.value = '';
  try {
    if (!editingPDP.value) {
      throw new Error('No PDP context selected for editing');
    }
    savingAPN.value = true;

    await ModemManager.setPDPAuthenticationByProfileById(
      props.modem.id,
      editingPDP.value.context_id,
      {
        apn: pdpAPN.value,
        protocol: pdpProtocol.value,
        username: updateAuthentication.value ? pdpUsername.value : undefined,
        password: updateAuthentication.value ? pdpPassword.value : undefined,
        type: updateAuthentication.value ? pdpAuthentication.value : PDPAuthenticationType.NONE,
      }
    );
    await fetchPDPContext();
    onCloseEditPDPModal();
  } catch (error) {
    console.error('Failed to edit PDP', error);
    editPDPError.value = error instanceof Error ? error.message : 'Failed to edit PDP';
  } finally {
    savingAPN.value = false;
  }
}

const onDevModeChange = async (mode: boolean) => {
  await fetchPDPContext(mode);
}

/** Watchers */
watch(isDevMode, onDevModeChange, { immediate: true });

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
