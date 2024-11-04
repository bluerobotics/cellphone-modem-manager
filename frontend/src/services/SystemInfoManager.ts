import axios from 'axios'
import { NetworkInterface } from '@/types/SystemInfoManager'

const SYSTEM_INFO_API = `http://blueos.internal/system`

const api = axios.create({
  baseURL: SYSTEM_INFO_API,
  timeout: 15000,
})

/**
 * Gte information about network interfaces in the system.
 * @returns {Promise<NetworkInterface[]>}
 */
export async function fetchNetworkInfo(): Promise<NetworkInterface[]> {
  const response = await api.get('/network')
  return response.data as NetworkInterface[]
}

export default {
  fetchNetworkInfo,
}
