from typing import List, Optional

from pydantic import BaseModel


class ModemDevice(BaseModel):
    device: str
    id: str
    manufacturer: str
    product: str


class ServingCellInfo(BaseModel):
    network_status: str
    access_technology: str
    duplex_mode: str
    mobile_country_code: int
    mobile_network_code: int
    cell_identity: str
    physical_cell_id: int
    earfcn: int
    frequency_band: int
    tracking_area_code: int
    reference_signal_power: int
    timing_advance: Optional[int]
    reference_signal_received_power: int
    reference_signal_received_quality: Optional[int]
    snr: Optional[int]
    uplink_bandwidth: Optional[int]
    downlink_bandwidth: Optional[int]


class NeighborCellInfo(BaseModel):
    cell_type: str
    access_technology: str
    earfcn: int
    physical_cell_id: Optional[int]
    signal_quality: Optional[int]
    reference_signal_received_power: Optional[int]
    snr: Optional[int]
    timing_advance: Optional[int]
    downlink_bandwidth: Optional[int]
    uplink_bandwidth: Optional[int]
    qrxlevmin: Optional[int]
    signal_quality_threshold: Optional[int]
    signal_strength_threshold: Optional[int]


class ModemCellInfo(BaseModel):
    serving_cell: ServingCellInfo
    neighbor_cells: List[NeighborCellInfo]


class PDPInfo(BaseModel):
    profile_id: str
    protocol: str
    apn: str
    ip_address: str
    primary_dns: Optional[str] = None
    secondary_dns: Optional[str] = None
    ipv6_address: Optional[str] = None
    status: str


class ModemSignalQuality(BaseModel):
    signal_strength: int
    bit_error_rate: int
