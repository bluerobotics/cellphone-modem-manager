/**
 * Represents details about a given modem device
 */
export interface ModemDevice {
  device: string
  id: string
  manufacturer: string
  product: string
}

/**
 * Represents information about the serving cell for the modem
 */
export interface ServingCellInfo {
  networkStatus: string
  accessTechnology: string
  duplexMode: string
  mobileCountryCode: number
  mobileNetworkCode: number
  cellIdentity: string
  physicalCellId: number
  earfcn: number
  frequencyBand: number
  trackingAreaCode: number
  referenceSignalPower: number
  timingAdvance?: number
  referenceSignalReceivedPower: number
  referenceSignalReceivedQuality?: number
  snr?: number
  uplinkBandwidth?: number
  downlinkBandwidth?: number
}

/**
 * Represents information about a neighboring cell
 */
export interface NeighborCellInfo {
  cellType: string
  accessTechnology: string
  earfcn: number
  physicalCellId?: number
  signalQuality?: number
  referenceSignalReceivedPower?: number
  snr?: number
  timingAdvance?: number
  downlinkBandwidth?: number
  uplinkBandwidth?: number
  qrxlevmin?: number
  signalQualityThreshold?: number
  signalStrengthThreshold?: number
}

/**
 * Represents overall cell information for a modem, including serving and neighboring cells
 */
export interface ModemCellInfo {
  servingCell: ServingCellInfo
  neighborCells: NeighborCellInfo[]
}

/**
 * Represents PDP (Packet Data Protocol) configuration information
 */
export interface PDPInfo {
  profileId: string
  protocol: string
  apn: string
  ipAddress: string
  primaryDns?: string
  secondaryDns?: string
  ipv6Address?: string
  status: string
}

/**
 * Represents signal quality metrics for the modem
 */
export interface ModemSignalQuality {
  signalStrength: number
  bitErrorRate: number
}
