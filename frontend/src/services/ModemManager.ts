import axios from 'axios'
import {
  CellLocation,
  DataUsageControls,
  DataUsageSettings,
  ModemCellInfo,
  ModemClockDetails,
  ModemDevice,
  ModemDeviceDetails,
  ModemPosition,
  ModemSIMStatus,
  ModemSignalQuality,
  NearbyCellTower,
  OperatorInfo,
  PDPContext,
  USBNetMode,
} from '@/types/ModemManager'

const MODEM_MANAGER_V1_API = `/v1.0`

const api = axios.create({
  baseURL: MODEM_MANAGER_V1_API,
  timeout: 15000,
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
 * Execute an AT command in a modem by modem id.
 * @param {string} modemId - Modem ID
 * @param {string} command - AT command to be executed
 * @param {number} delay - Delay in seconds between sending the command and reading the response
 * @returns {Promise<string>}
 */
export async function commandById(modemId: string, command: string, delay: number = 0.3): Promise<string> {
  command = encodeURIComponent(command)
  const response = await api.post(`/modem/${modemId}/commander?command=${command}&delay=${delay}`)
  return response.data as string
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
 * Return the current position of a modem by modem id.
 * @param {string} modemId - Modem ID
 * @returns {Promise<ModemPosition>}
 */
export async function fetchPositionById(modemId: string): Promise<ModemPosition> {
  const response = await api.get(`/modem/${modemId}/position`)
  return response.data as ModemPosition
}

/**
 * Get SIM status of a modem by id.
 * @param {string} modemId - Modem ID
 * @returns {Promise<ModemSIMStatus>}
 */
export async function fetchSIMStatusById(modemId: string): Promise<ModemSIMStatus> {
  const response = await api.get(`/modem/${modemId}/sim_status`)
  return response.data as ModemSIMStatus
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
  await api.put(`/modem/${modemId}/pdp/${profile}/apn/${apn}`)
}

/**
 * Get data usage details of a modem by modem id.
 * @param {string} modemId - Modem ID
 * @returns {Promise<DataUsageSettings>}
 */
export async function fetchDataUsageById(modemId: string): Promise<DataUsageSettings> {
  const response = await api.get(`/modem/${modemId}/usage/details`)
  return response.data as DataUsageSettings
}

/**
 * Set data usage control settings of a modem by modem id.
 * @param {string} modemId - Modem ID
 * @param {DataUsageControls} control - Data usage control settings
 * @returns {Promise<DataUsageSettings>}
 */
export async function setDataUsageControlById(modemId: string, control: DataUsageControls): Promise<DataUsageSettings> {
  const response = await api.put(`/modem/${modemId}/usage/control`, control)
  return response.data as DataUsageSettings
}

export async function fetchCellCoordinates(
  mcc: number,
  mnc: number,
  lac: number,
  cellId: number
): Promise<CellLocation> {
  const response = await api.get(`/cells/coordinate?mcc=${mcc}&mnc=${mnc}&lac=${lac}&cell_id=${cellId}`)
  return response.data as CellLocation
}

export async function fetchNearbyCellsCoordinates(
  lat: number,
  lon: number,
): Promise<NearbyCellTower[]> {
  const response = await api.get(`/cells/nearby?lat=${lat}&lon=${lon}`)
  return response.data as NearbyCellTower[]
}

export default {
  commandById,
  fetch,
  fetchById,
  fetchCellCoordinates,
  fetchCellInfoById,
  fetchClockById,
  fetchDataUsageById,
  fetchNearbyCellsCoordinates,
  fetchOperatorInfoById,
  fetchPDPInfoById,
  fetchPositionById,
  fetchSIMStatusById,
  fetchSignalStrengthById,
  fetchUSBModeById,
  rebootById,
  resetById,
  setAPNByProfileById,
  setDataUsageControlById,
  setUSBModeById,
}
