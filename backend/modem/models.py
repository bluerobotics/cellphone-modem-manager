from enum import Enum
from typing import List, Optional

from pydantic import BaseModel

# General modem related

class ModemDevice(BaseModel):
    device: str
    id: str
    manufacturer: str
    product: str


class ModemDeviceDetails(ModemDevice):
    firmware_revision: str

# Configurations related

class USBNetMode(Enum):
    QMI = "0"
    ECM = "1"
    MBIM = "2"

# Cell Towers related

class ServingCellState(Enum):
    SEARCH = "SEARCH"
    LIMSRV = "LIMSRV"
    NOCONN = "NOCONN"
    CONNECT = "CONNECT"


class AccessTechnology(Enum):
    GSM = "GSM"
    WCDMA = "WCDMA"
    LTE = "LTE"
    CDMA = "CDMA"
    HDR = "HDR"
    TDSCDMA = "TDSCDMA"


class ServingCellInfo(BaseModel):
    """
    Common model for serving cell info. Fields vary by manufacturer and are sent to the frontend. Add any needed fields
    here, typically as optional, since not all modems provide the same data.
    """
    state: ServingCellState
    rat: AccessTechnology
    mobile_country_code: int
    mobile_network_code: int
    area_id: int
    cell_id: int

    signal_quality_dbm: Optional[int] = None
    signal_inr_db: Optional[int] = None
    up_bandwidth_mhz: Optional[int] = None
    dl_bandwidth_mhz: Optional[int] = None


class NeighborCellType(Enum):
    NEIGHBOUR_CELL = "neighbourcell"
    NEIGHBOUR_CELL_INTRA = "neighbourcell intra"
    NEIGHBOUR_CELL_INTER = "neighbourcell inter"


class NeighborCellInfo(BaseModel):
    cell_type: NeighborCellType
    rat: AccessTechnology

    # Sadly only GSM gives us location parameters
    mobile_country_code: Optional[int] = None
    mobile_network_code: Optional[int] = None
    area_id: Optional[int] = None
    cell_id: Optional[int] = None

    signal_quality_dbm: Optional[int] = None
    signal_inr_db: Optional[int] = None


class ModemCellInfo(BaseModel):
    serving_cell: ServingCellInfo
    neighbor_cells: List[NeighborCellInfo]

# PDP context related

class PDPType(Enum):
    IP = "IP"
    PPP = "PPP"
    IPV6 = "IPV6"
    IPV4V6 = "IPV4V6"

class PDPDataCompression(Enum):
    OFF = "0"
    ON = "1"
    V42BIS = "2"

class PDPHeaderCompression(Enum):
    OFF = "0"
    ON = "1"
    RFC1144 = "2"
    RFC2507 = "3"
    RFC3095 = "4"

class PDPAddressAllocation(Enum):
    NAS = "0"
    DHCP = "1"

class PDPRequestType(Enum):
    NORMAL = "0"
    EMERGENCY = "1"

class PDPContext(BaseModel):
    context_id: int
    protocol: PDPType
    access_point_name: str
    ip_address: str
    data_compression: PDPDataCompression
    header_compression: PDPHeaderCompression
    ipv6_address: PDPAddressAllocation
    status: PDPRequestType

# Signal quality related

class ModemSignalQuality(BaseModel):
    signal_strength: int
    bit_error_rate: int
