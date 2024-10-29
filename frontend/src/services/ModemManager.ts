import axios from 'axios'
import { ModemDevice, ModemSignalQuality, ModemCellInfo, PDPInfo } from '@/types/ModemManager'

const MODEM_MANAGER_V1_API = `/v1.0`

const api = axios.create({
  baseURL: MODEM_MANAGER_V1_API,
})

/**
 * List device descriptor of all connected modems.
 * @returns {Promise<ModemDevice[]>}
 */
export async function fetchModems(): Promise<ModemDevice[]> {
  const response = await api.get('/modem', { timeout: 5000 })
  return response.data as ModemDevice[]
}

/**
 * Get details of a modem by identifier.
 * @param {string} id - Modem ID
 * @returns {Promise<ModemDevice>}
 */
export async function fetchModemByDevice(id: string): Promise<ModemDevice> {
  const response = await api.get(`/modem/${id}/details`, { timeout: 5000 })
  return response.data as ModemDevice
}

/**
 * Get signal strength of a modem by device id.
 * @param {string} id - Modem ID
 * @returns {Promise<ModemSignalQuality>}
 */
export async function fetchSignalStrength(id: string): Promise<ModemSignalQuality> {
  const response = await api.get(`/modem/${id}/signal`, { timeout: 5000 })
  return response.data as ModemSignalQuality
}

/**
 * Get serving cell and neighbors cells information of a modem by device id.
 * @param {string} id - Modem ID
 * @returns {Promise<ModemCellInfo>}
 */
export async function fetchServingCellInfo(id: string): Promise<ModemCellInfo> {
  const response = await api.get(`/modem/${id}/cell`, { timeout: 5000 })
  return response.data as ModemCellInfo
}

/**
 * Reboot a modem by device id.
 * @param {string} id - Modem ID
 * @returns {Promise<void>}
 */
export async function rebootModem(id: string): Promise<void> {
  await api.post(`/modem/${id}/reboot`, null, { timeout: 5000 })
}

/**
 * Get USB mode of a modem by device.
 * @param {string} id - Modem ID
 * @returns {Promise<number>}
 */
export async function fetchUSBMode(id: string): Promise<number> {
  const response = await api.get(`/modem/${id}/config/usb_net`, { timeout: 5000 })
  return response.data as number
}

/**
 * Set USB mode of a modem by device.
 * @param {string} id - Modem ID
 * @param {string} mode - New USB mode
 * @returns {Promise<void>}
 */
export async function setUSBMode(id: string, mode: string): Promise<void> {
  await api.put(`/modem/${id}/config/usb_net/${mode}`, null, { timeout: 5000 })
}

/**
 * Get PDP information of a modem by device.
 * @param {string} id - Modem ID
 * @returns {Promise<PDPInfo[]>}
 */
export async function fetchPDPInfo(id: string): Promise<PDPInfo[]> {
  const response = await api.get(`/modem/${id}/pdp`, { timeout: 5000 })
  return response.data as PDPInfo[]
}

/**
 * Set APN of a profile of a modem by device.
 * @param {string} id - Modem ID
 * @param {number} profile - Profile ID
 * @param {string} apn - APN to set
 * @returns {Promise<void>}
 */
export async function setAPNByProfile(id: string, profile: number, apn: string): Promise<void> {
  await api.put(`/modem/${id}/pdp/${profile}apn/${apn}`, null, { timeout: 5000 })
}

/**
 * Ping a server by modem device ID, be careful that this can take a long time, and serial is blocked. So, other
 * requests will be blocked until this request is finished.
 * @param {string} device - Modem device ID
 * @param {string} server - Server address to ping
 * @returns {Promise<number>}
 */
export async function pingServerByDevice(device: string, server: string): Promise<number> {
  const response = await api.get(`/modem/${device}/ping/${server}`, { timeout: 5000 })
  return response.data as number
}

export default {
  fetchModems,
  fetchModemByDevice,
  fetchSignalStrength,
  fetchServingCellInfo,
  rebootModem,
  fetchUSBMode,
  setUSBMode,
  fetchPDPInfo,
  setAPNByProfile,
  pingServerByDevice,
}
