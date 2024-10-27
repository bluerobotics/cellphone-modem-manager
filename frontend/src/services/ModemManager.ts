import axios from 'axios'
import { ModemDevice } from '@/types/ModemManager'

const MODEM_MANAGER_V1_API = `/v1.0`

const api = axios.create({
  baseURL: MODEM_MANAGER_V1_API,
})

/**
 * List device descriptor of all connected modems.
 * @returns {Promise<string[]>}
 */
export async function fetchModems(): Promise<ModemDevice[]> {
  const response = await api.get('/modem', { timeout: 5000 })

  return response.data as ModemDevice[]

  // return [
  //   {
  //     device: '/sys/devices/platform/scb/fd500000.pcie/pci0000:00/0000:00:00.0/0000:01:00.0/usb1/1-1/1-1.1',
  //     manufacturer: 'Quectel',
  //     product: 'EC25-E',
  //   },
  //   {
  //     device: '/sys/devices/platform/scb/fd500000.pcie/pci0000:00/0000:00:00.0/0000:01:00.0/usb2/1-1/1-1.1',
  //     manufacturer: 'Quectel',
  //     product: 'EC25-E',
  //   },
  // ] as ModemDevice[]
}

/**
 * Get details of a modem by identifier.
 * @returns {Promise<ModemDevice[]>}
 */
export async function fetchModemByDevice(device: string): Promise<ModemDevice> {
  const response = await api.get(`/modem/${device}`, { timeout: 5000 })

  return response.data as ModemDevice
}

export default {
  fetchModems,
  fetchModemByDevice,
}
