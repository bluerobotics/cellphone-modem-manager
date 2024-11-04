import axios from 'axios'
import {
  ModemDevice,
  ModemDeviceDetails,
  ModemSignalQuality,
  ModemCellInfo,
  ModemClockDetails,
  USBNetMode,
  PDPContext,
  OperatorInfo,
} from '@/types/ModemManager'

const MODEM_MANAGER_V1_API = `/v1.0`

const api = axios.create({
  baseURL: MODEM_MANAGER_V1_API,
  timeout: 10000,
})

/**
 * List device descriptor of all connected modems.
 * @returns {Promise<ModemDevice[]>}
 */
export async function fetch(): Promise<ModemDevice[]> {
  const response = await api.get('/modem')
  return response.data as ModemDevice[]
}

/**
 * Get details of a modem by id.
 * @param {string} modemId - Modem ID
 * @returns {Promise<ModemDeviceDetails>}
 */
export async function fetchById(modemId: string): Promise<ModemDeviceDetails> {
  const response = await api.get(`/modem/${modemId}/details`)
  return response.data as ModemDeviceDetails
}

/**
 * Get signal strength of a modem by id.
 * @param {string} modemId - Modem ID
 * @returns {Promise<ModemSignalQuality>}
 */
export async function fetchSignalStrengthById(modemId: string): Promise<ModemSignalQuality> {
  const response = await api.get(`/modem/${modemId}/signal`)
  return response.data as ModemSignalQuality
}

/**
 * Get serving cell and neighbor cells information of a modem by id.
 * @param {string} modemId - Modem ID
 * @returns {Promise<ModemCellInfo>}
 */
export async function fetchCellInfoById(modemId: string): Promise<ModemCellInfo> {
  const response = await api.get(`/modem/${modemId}/cell`)
  return response.data as ModemCellInfo
}

/**
 * Reboot a modem by id.
 * @param {string} modemId - Modem ID
 * @returns {Promise<void>}
 */
export async function rebootById(modemId: string): Promise<void> {
  await api.post(`/modem/${modemId}/reboot`)
}

/**
 * Reset a modem to factory settings by id.
 * @param {string} modemId - Modem ID
 * @returns {Promise<void>}
 */
export async function resetById(modemId: string): Promise<void> {
  await api.post(`/modem/${modemId}/reset`)
}

/**
 * Get current clock of a modem by id.
 * @param {string} modemId - Modem ID
 * @returns {Promise<ModemClockDetails>}
 */
export async function fetchClockById(modemId: string): Promise<ModemClockDetails> {
  const response = await api.get(`/modem/${modemId}/clock`)
  return response.data as ModemClockDetails
}

/**
 * Get USB network mode of a modem by id.
 * @param {string} modemId - Modem ID
 * @returns {Promise<USBNetMode>}
 */
export async function fetchUSBModeById(modemId: string): Promise<USBNetMode> {
  const response = await api.get(`/modem/${modemId}/config/usb_net`)
  return response.data as USBNetMode
}

/**
 * Set USB network mode of a modem by id.
 * @param {string} modemId - Modem ID
 * @param {USBNetMode} mode - USB network mode
 * @returns {Promise<void>}
 */
export async function setUSBModeById(modemId: string, mode: USBNetMode): Promise<void> {
  await api.put(`/modem/${modemId}/config/usb_net/${mode}`)
}

/**
 * Get PDP context information of a modem by id.
 * @param {string} modemId - Modem ID
 * @returns {Promise<PDPContext[]>}
 */
export async function fetchPDPInfoById(modemId: string): Promise<PDPContext[]> {
  const response = await api.get(`/modem/${modemId}/pdp`)
  return response.data as PDPContext[]
}

/**
 * Get operator information of a modem by id.
 * @param {string} modemId - Modem ID
 * @returns {Promise<OperatorInfo>}
 */
export async function fetchOperatorInfoById(modemId: string): Promise<OperatorInfo> {
  const response = await api.get(`/modem/${modemId}/operator`)
  return response.data as OperatorInfo
}

/**
 * Set APN of a profile by modem id.
 * @param {string} modemId - Modem ID
 * @param {number} profile - Profile ID
 * @param {string} apn - Access Point Name
 * @returns {Promise<void>}
 */
export async function setAPNByProfileById(modemId: string, profile: number, apn: string): Promise<void> {
  await api.put(`/modem/${modemId}/pdp/${profile}apn/${apn}`)
}

export default {
  fetch,
  fetchById,
  fetchSignalStrengthById,
  fetchCellInfoById,
  rebootById,
  resetById,
  fetchClockById,
  fetchUSBModeById,
  setUSBModeById,
  fetchPDPInfoById,
  fetchOperatorInfoById,
  setAPNByProfileById,
}
