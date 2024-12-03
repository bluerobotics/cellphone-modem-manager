export interface SpeedtestServer {
  url: string
  lat: string
  lon: string
  name: string
  country: string
  cc: string
  sponsor: string
  id: string
  host: string
  d: number
  latency: number
}

export interface SpeedtestClient {
  ip: string
  lat: string
  lon: string
  isp: string
  isprating: string
  rating: string
  ispdlavg: string
  ispulavg: string
  loggedin: string
  country: string
}

export interface SpeedTestResult {
  download: number
  upload: number
  ping: number
  server: SpeedtestServer
  timestamp: Date
  bytes_sent: number
  bytes_received: number
  share: string | null
  client: SpeedtestClient
}

export interface Website {
  hostname: string
  path: string
  port: number
}

export interface WebsiteStatus {
  site: Website
  online: boolean
  error?: string
}
