/**
 * General modem
 */

export interface ModemDevice {
  device: string
  id: string
  manufacturer: string
  product: string
}

export interface ModemFirmwareRevision {
  firmware_revision: string
  timestamp?: string
  authors?: string
}

export interface ModemDeviceDetails extends ModemDevice {
  imei: string
  serial_number: string
  imsi?: string
  firmware_revision: ModemFirmwareRevision
}

export interface ModemClockDetails {
  date: string
  time: string
  gmt_offset: number
}

export interface ModemPosition {
  latitude: number
  longitude: number
  // If the position was estimated by other sources like mavlink it will be considered as external
  external_source: boolean
}

export enum ModemSIMStatus {
  DISCONNECTED = "0",
  CONNECTED = "1",
  UNKNOWN = "2",
}

export interface DataUsageControls {
  data_control_enabled: boolean
  // Data limit in bytes, default is 2GB
  data_limit: number
  // The day of the month when the data usage resets
  data_reset_day: number
  // The date when the data usage was last reset
  last_reset_date: string
}

export interface DataUsageSettings extends DataUsageControls {
  // RX and TX data used in bytes
  data_used: [number, number]
  // List of data points from last data_reset_day to now, key is the month day and value is RX and TX data used
  data_points: Record<string, [number, number]>
}

/**
 * Configurations related
 */

export enum USBNetMode {
  QMI = "0",
  ECM = "1",
  MBIM = "2",
}

/**
 * Cell Towers related
 */

export enum ServingCellState {
  SEARCH = "SEARCH",
  LIMSRV = "LIMSRV",
  NOCONN = "NOCONN",
  CONNECT = "CONNECT",
}

export enum AccessTechnology {
  GSM = "GSM",
  WCDMA = "WCDMA",
  LTE = "LTE",
  CDMA = "CDMA",
  HDR = "HDR",
  TDSCDMA = "TDSCDMA",
}

export interface ServingCellInfo {
  state: ServingCellState
  rat: AccessTechnology
  mobile_country_code: number
  mobile_network_code: number
  area_id: number
  cell_id: number

  signal_quality_dbm?: number
  signal_inr_db?: number
  up_bandwidth_mhz?: number
  dl_bandwidth_mhz?: number
}

export enum NeighborCellType {
  NEIGHBOUR_CELL = "neighbourcell",
  NEIGHBOUR_CELL_INTRA = "neighbourcell intra",
  NEIGHBOUR_CELL_INTER = "neighbourcell inter",
}

export interface NeighborCellInfo {
  cell_type: NeighborCellType
  rat: AccessTechnology

  /* Sadly only GSM gives us location parameters */
  mobile_country_code?: number
  mobile_network_code?: number
  area_id?: number
  cell_id?: number

  signal_quality_dbm?: number
  signal_inr_db?: number
}

export interface ModemCellInfo {
  serving_cell: ServingCellInfo
  neighbor_cells: NeighborCellInfo[]
}

/**
 * PDP context related
 */

export enum PDPType {
  IP = "IP",
  PPP = "PPP",
  IPV6 = "IPV6",
  IPV4V6 = "IPV4V6",
}
export enum PDPDataCompression {
  OFF = "0",
  ON = "1",
  V42BIS = "2",
}

export enum PDPHeaderCompression {
  OFF = "0",
  ON = "1",
  RFC1144 = "2",
  RFC2507 = "3",
  RFC3095 = "4",
}

export enum PDPAddressAllocation {
  NAS = "0",
  DHCP = "1",
}

export enum PDPRequestType {
  NORMAL = "0",
  EMERGENCY = "1",
}

export interface PDPContext {
  context_id: number
  protocol: PDPType
  access_point_name: string
  ip_address: string
  data_compression: PDPDataCompression
  header_compression: PDPHeaderCompression
  ipv6_address: PDPAddressAllocation
  status: PDPRequestType
}

/** Signal quality related */

export interface ModemSignalQuality {
  signal_strength_dbm: number
  bit_error_rate: number
}

/** Network related */

export enum OperatorSelectionMode {
  AUTOMATIC = "0",
  MANUAL = "1",
  DEREGISTER = "2",
  FORMAT_ONLY = "3",
  MANUAL_AUTOMATIC = "4",
}

export enum OperatorFormat {
  LONG = "0",
  SHORT = "1",
  NUMERIC = "2",
}

export enum OperatorAct {
  GSM = "0",
  UTRAN = "2",
  GSM_EGPRS = "3",
  UTRAN_HSDPA = "4",
  UTRAN_HSUPA = "5",
  UTRAN_HSDPA_HSUPA = "6",
  E_UTRAN = "7",
  CDMA = "100",
}

export interface OperatorInfo {
  mode: OperatorSelectionMode
  format: OperatorFormat
  operator: string
  act: OperatorAct
}

/** Cells Location */

export interface CellLocation {
  latitude: number
  longitude: number
  range: number
}

export interface NearbyCellRadio {
  type: string
}

export interface NearbyCellTower {
  latitude: number
  longitude: number
  range: number
  radio: NearbyCellRadio
}
