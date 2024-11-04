import axios from 'axios'
import { SpeedTestResult, WebsiteStatus } from '@/types/InternetManager'

const HELPER_API = `http://blueos.internal/helper/latest`

const api = axios.create({
  baseURL: HELPER_API,
  timeout: 15000,
})

/**
 * Check if BlueOS has internet access.
 * @returns {Promise<SpeedTestResult | void>}
 */
export async function checkInternetAccess(): Promise<Record<string, WebsiteStatus>> {
  const response = await api.get('/check_internet_access')
  return response.data as Record<string, WebsiteStatus>
}

/**
 * Check the best server for internet speed test.
 * @returns {Promise<SpeedTestResult>}
 */
export async function checkInternetBestServer(): Promise<SpeedTestResult> {
  const response = await api.get('/internet_best_server')
  return response.data as SpeedTestResult
}

/**
 * Check the internet download speed.
 * @returns {Promise<SpeedTestResult>}
 */
export async function checkInternetDownloadSpeed(): Promise<SpeedTestResult> {
  const response = await api.get('/internet_download_speed')
  return response.data as SpeedTestResult
}

/**
 * Check the internet upload speed.
 * @returns {Promise<SpeedTestResult>}
 */
export async function checkInternetUploadSpeed(): Promise<SpeedTestResult> {
  const response = await api.get('/internet_upload_speed')
  return response.data as SpeedTestResult
}

export default {
  checkInternetAccess,
  checkInternetBestServer,
  checkInternetDownloadSpeed,
  checkInternetUploadSpeed,
}
