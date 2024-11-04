export interface NetworkInterface {
  description: string
  errors_on_received: number
  errors_on_transmitted: number
  ips: string[]
  is_loopback: boolean
  is_up: boolean
  mac: string
  name: string
  packets_received: number
  packets_transmitted: number
  received_B: number
  total_errors_on_received: number
  total_errors_on_transmitted: number
  total_packets_received: number
  total_packets_transmitted: number
  total_received_B: number
  total_transmitted_B: number
  transmitted_B: number
}
