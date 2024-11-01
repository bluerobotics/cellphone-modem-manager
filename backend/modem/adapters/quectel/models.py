# NOTE: This file should define parsing models specific to this modem, reuse models from modem.models where possible.
# NOTE: Recommended keep fields in order since we expand directly from AT command array response
#
# Protocol Manual: https://forums.quectel.com/uploads/short-url/cBnrTmjnCg7OGnqRsk8dIpbHuVX.pdf

import abc
import math
from enum import Enum
from typing import Optional, Type

from pydantic import BaseModel, Field, field_validator

from modem.models import (
    AccessTechnology,
    ServingCellInfo,
    ServingCellState,
    NeighborCellInfo,
    NeighborCellType,
)

# Utils

def rxlev_to_dbm(rxlev: Optional[int]) -> Optional[int]:
    return rxlev - 111 if rxlev else None

def cpich_rscp_rxpwr_to_dbm(rscp_rxpwr: Optional[int]) -> Optional[int]:
    return rscp_rxpwr / 10.0 if rscp_rxpwr else None

def cpich_ecno_to_db(cpich_ecno: Optional[int]) -> Optional[int]:
    return cpich_ecno / 10.0 if cpich_ecno else None

# Related to AT+QENG="servingcell"
# Page: 103

class CellVoiceCodec(Enum):
    HR = "HR"
    FR = "FR"
    EFR = "EFR"
    AMR = "AMR"
    AMRHR = "AMRHR"
    AMRFR = "AMRFR"
    AMRWB = "AMRWB"


class CellSpreadingFactor(Enum):
    SF_4 = "0"
    SF_8 = "1"
    SF_16 = "2"
    SF_32 = "3"
    SF_64 = "4"
    SF_128 = "5"
    SF_256 = "6"
    SF_512 = "7"
    UNKNOWN = "8"


class ULDLBandwidth(Enum):
    MHz_1_4 = "0"
    MHz_3 = "1"
    MHz_5 = "2"
    MHz_10 = "3"
    MHz_15 = "4"
    MHz_20 = "5"

    def as_mhz(self) -> float:
        mhz_value = self.name.split("_", 1)[1].replace("_", ".")
        return float(mhz_value)


class BaseServingCell(BaseModel):
    @abc.abstractmethod
    def info(self) -> ServingCellInfo:
        raise NotImplementedError

    @classmethod
    def get_model(cls, rat: AccessTechnology) -> Optional[Type]:
        target_name = f"ServingCell{rat.value}"
        for subcls in cls.__subclasses__():
            if subcls.__name__ == target_name:
                return subcls
            found = subcls.get_model(rat)
            if found:
                return found
        return None


class BaseServingCellData(BaseServingCell):
    state: ServingCellState
    rat: AccessTechnology
    mcc: Optional[int] = None
    mnc: Optional[int] = None
    lac: Optional[int] = Field(None, ge=0, le=0xFFFFFFF)
    cell_id: Optional[int] = Field(None, ge=0, le=0xFFFFFFF)

    @field_validator("lac", "cell_id", mode="before")
    @classmethod
    def hex_to_int(cls, value):
        return int(value, 16) if isinstance(value, str) else value

    def _base_info(self) -> ServingCellInfo:
        return ServingCellInfo(
            state=self.state,
            rat=self.rat,
            mobile_country_code=self.mcc,
            mobile_network_code=self.mnc,
            area_id=self.lac,
            cell_id=self.cell_id,
        )


class ServingCellGSM(BaseServingCellData):
    bsic: Optional[int] = Field(None, ge=0, le=63)
    arfcn: Optional[int] = Field(None, ge=0, le=1023)
    band: Optional[int] = Field(None, ge=0, le=1)
    rxlev: Optional[int] = Field(None, ge=0, le=63)
    txp: Optional[int] = None
    rla: Optional[int] = None
    drx: Optional[int] = None
    c1: Optional[int] = None
    c2: Optional[int] = None
    gprs: Optional[bool] = None
    tch: Optional[int | str] = None
    ts: Optional[int] = None
    ta: Optional[int] = Field(None, ge=0, le=63)
    maio: Optional[int] = None
    hsn: Optional[int] = None
    rxlevsub: Optional[int] = Field(None, ge=0, le=63)
    rxlevfull: Optional[int] = Field(None, ge=0, le=63)
    rxqualsub: Optional[int] = Field(None, ge=0, le=7)
    rxqualfull: Optional[int] = Field(None, ge=0, le=7)
    voicecodec: Optional[CellVoiceCodec] = None

    def info(self) -> ServingCellInfo:
        base = self._base_info()
        base.signal_quality_dbm = rxlev_to_dbm(self.rxlev)
        return base


class ServingCellWCDMA(BaseServingCellData):
    uarfcn: Optional[int] = None
    psc: Optional[int] = None
    rac: Optional[int] = Field(None, ge=0, le=255)
    rscp: Optional[int] = None
    ecio: Optional[int] = None
    phych: Optional[int] = Field(None, ge=0, le=1)
    SF: Optional[CellSpreadingFactor] = None
    slot: Optional[int] = None
    speech_code: Optional[int] = None
    com_mod: Optional[bool] = None

    def info(self) -> ServingCellInfo:
        base = self._base_info()
        base.signal_quality_dbm = self.rscp
        base.signal_inr_db = self.ecio
        return base


class ServingCellTDSCDMA(BaseServingCellData):
    pfreq: Optional[int] = None
    rssi: Optional[int] = None
    rscp: Optional[int] = None
    ecio: Optional[int] = None

    def info(self) -> ServingCellInfo:
        base = self._base_info()
        base.signal_quality_dbm = self.rscp or self.rssi
        base.signal_inr_db = self.ecio
        return base


class ServingCellCDMA(BaseServingCellData):
    bcch: Optional[int] = None
    rxpwr: Optional[int] = None
    ecio: Optional[int] = None
    txpwr: Optional[int] = None

    def info(self) -> ServingCellInfo:
        base = self._base_info()
        base.signal_quality_dbm = cpich_rscp_rxpwr_to_dbm(self.rxpwr)
        base.signal_inr_db = self.ecio
        return base


class ServingCellHDR(ServingCellCDMA):
    pass


class ServingCellLTE(BaseServingCell):
    """
    LTE is the different guy here, it have the duplex mode in header
    """
    state: ServingCellState
    rat: AccessTechnology = AccessTechnology.LTE
    is_tdd: Optional[str] = None
    mcc: Optional[int] = None
    mnc: Optional[int] = None
    cell_id: Optional[int] = Field(None, ge=0, le=0xFFFFFFF)
    pcid: Optional[int] = None
    earfcn: Optional[int] = None
    freq_band_ind: int
    ul_bandwidth: Optional[ULDLBandwidth] = None
    dl_bandwidth: Optional[ULDLBandwidth] = None
    tac: Optional[int] = Field(None, ge=0, le=0xFFFF)
    rsrp: Optional[int] = None
    rsrq: Optional[int] = None
    rssi: Optional[int] = None
    sinr: Optional[int] = Field(None, ge=-20, le=30)
    srxlev: Optional[int] = None

    @field_validator("tac", "cell_id", mode="before")
    @classmethod
    def hex_to_int(cls, value):
        return int(value, 16) if isinstance(value, str) else value

    def info(self) -> ServingCellInfo:
        return ServingCellInfo(
            state=self.state,
            rat=self.rat,
            mobile_country_code=self.mcc,
            mobile_network_code=self.mnc,
            area_id=self.tac,
            cell_id=self.cell_id,
            signal_quality_dbm=self.rsrp,
            signal_inr_db=self.sinr,
            up_bandwidth=self.ul_bandwidth.as_mhz() if self.ul_bandwidth else None,
            dl_bandwidth=self.dl_bandwidth.as_mhz() if self.dl_bandwidth else None,
        )

# Related to AT+QENG="neighbourcell"
# Page: 104

class NeighborCellSet(Enum):
    ACTIVE = "1"
    SYNC = "2"
    ASYNC = "3"

class BaseNeighborCell(BaseModel):
    @abc.abstractmethod
    def info(self) -> NeighborCellInfo:
        raise NotImplementedError

    @classmethod
    def get_model(
        cls,
        serving_rat: AccessTechnology,
        rat: AccessTechnology,
        cell_type: NeighborCellType,
    ) -> Optional[Type]:
        cell_type_str = ""
        if cell_type == NeighborCellType.NEIGHBOUR_CELL_INTRA:
            cell_type_str = "Intra"
        if cell_type == NeighborCellType.NEIGHBOUR_CELL_INTER:
            cell_type_str = "Inter"

        target_name = f"{serving_rat.value}NeighborCell{cell_type_str}{rat.value}"
        for subcls in cls.__subclasses__():
            if subcls.__name__ == target_name:
                return subcls
            found = subcls.get_model(serving_rat, rat, cell_type)
            if found:
                return found
        return None

## If current serving cell is GSM

class GSMNeighborCellGSM(BaseNeighborCell):
    cell_type: NeighborCellType = NeighborCellType.NEIGHBOUR_CELL
    rat: AccessTechnology = AccessTechnology.GSM
    mcc: Optional[int] = None
    mnc: Optional[int] = None
    lac: Optional[int] = Field(None, ge=0, le=0xFFFFFFF)
    cell_id: Optional[int] = Field(None, ge=0, le=0xFFFFFFF)
    bsic: Optional[int] = Field(None, ge=0, le=63)
    arfcn: Optional[int] = Field(None, ge=0, le=1023)
    rxlev: Optional[int] = Field(None, ge=0, le=63)
    c1: Optional[int] = None
    c2: Optional[int] = None
    c31: Optional[int] = None
    c32: Optional[int] = None

    @field_validator("lac", "cell_id", mode="before")
    @classmethod
    def hex_to_int(cls, value):
        return int(value, 16) if isinstance(value, str) else value

    def info(self) -> NeighborCellInfo:
        return NeighborCellInfo(
            cell_type=self.cell_type,
            rat=self.rat,
            mobile_country_code=self.mcc,
            mobile_network_code=self.mnc,
            area_id=self.lac,
            cell_id=self.cell_id,
            signal_quality_dbm=rxlev_to_dbm(self.rxlev),
        )


class GSMNeighborCellWCDMA(BaseNeighborCell):
    cell_type: NeighborCellType = NeighborCellType.NEIGHBOUR_CELL
    rat: AccessTechnology = AccessTechnology.WCDMA
    uarfcn: Optional[int] = None
    psc: Optional[int] = None
    rscp: Optional[int] = None
    ecno: Optional[int] = None

    def info(self) -> NeighborCellInfo:
        return NeighborCellInfo(
            cell_type=self.cell_type,
            rat=self.rat,
            signal_quality_dbm=self.rscp,
            signal_inr_db=self.ecno,
        )


class GSMNeighborCellLTE(BaseNeighborCell):
    cell_type: NeighborCellType = NeighborCellType.NEIGHBOUR_CELL
    rat: AccessTechnology = AccessTechnology.LTE
    earfcn: Optional[int] = None
    pcid: Optional[int] = None
    rsrp: Optional[int] = None
    rsrq: Optional[int] = None

    def info(self) -> NeighborCellInfo:
        return NeighborCellInfo(
            cell_type=self.cell_type,
            rat=self.rat,
            signal_quality_dbm=self.rsrp,
            signal_inr_db=self.rsrq,
        )

## If current serving cell is WCDMA

class WCDMANeighborCellGSM(BaseNeighborCell):
    cell_type: NeighborCellType = NeighborCellType.NEIGHBOUR_CELL
    rat: AccessTechnology = AccessTechnology.GSM
    bsic: Optional[int] = Field(None, ge=0, le=63)
    rxlev: Optional[int] = Field(None, ge=0, le=63)
    rank: Optional[int] = None

    def info(self) -> NeighborCellInfo:
        return NeighborCellInfo(
            cell_type=self.cell_type,
            rat=self.rat,
            signal_quality_dbm=rxlev_to_dbm(self.rxlev),
        )


class WCDMANeighborCellWCDMA(BaseNeighborCell):
    cell_type: NeighborCellType = NeighborCellType.NEIGHBOUR_CELL
    rat: AccessTechnology = AccessTechnology.WCDMA
    uarfcn: Optional[int] = None
    srxqual: Optional[int] = None
    psc: Optional[int] = None
    rscp: Optional[int] = None
    ecno: Optional[int] = None
    cell_set: Optional[NeighborCellSet] = None
    rank: Optional[int] = None
    srxlev: Optional[int] = None

    def info(self) -> NeighborCellInfo:
        return NeighborCellInfo(
            cell_type=self.cell_type,
            rat=self.rat,
            signal_quality_dbm=self.rscp,
            signal_inr_db=self.ecno,
        )


class WCDMANeighborCellLTE(BaseNeighborCell):
    cell_type: NeighborCellType = NeighborCellType.NEIGHBOUR_CELL
    rat: AccessTechnology = AccessTechnology.LTE
    earfcn: Optional[int] = None
    pcid: Optional[int] = None
    rsrp: Optional[int] = None
    rsrq: Optional[int] = None
    srxlev: Optional[int] = None

    def info(self) -> NeighborCellInfo:
        return NeighborCellInfo(
            cell_type=self.cell_type,
            rat=self.rat,
            signal_quality_dbm=self.rsrp,
            signal_inr_db=self.rsrq,
        )

## If current serving cell is LTE

class LTENeighborCellGSM(BaseNeighborCell):
    cell_type: NeighborCellType = NeighborCellType.NEIGHBOUR_CELL
    rat: AccessTechnology = AccessTechnology.GSM
    arfcn: Optional[int] = Field(None, ge=0, le=1023)
    cell_resel_priority: Optional[int] = Field(None, ge=0, le=7)
    thresh_gsm_high: Optional[int] = None
    thresh_gsm_low: Optional[int] = None
    ncc_permitted: Optional[int] = None
    band: Optional[int] = Field(None, ge=0, le=1)
    bsic_id: Optional[int] = None
    rssi: Optional[int] = None
    srxlev: Optional[int] = None

    def info(self) -> NeighborCellInfo:
        return NeighborCellInfo(
            cell_type=self.cell_type,
            rat=self.rat,
            signal_quality_dbm=self.rssi,
        )


class LTENeighborCellWCDMA(BaseNeighborCell):
    cell_type: NeighborCellType = NeighborCellType.NEIGHBOUR_CELL
    rat: AccessTechnology = AccessTechnology.WCDMA
    uarfcn: Optional[int] = None
    cell_resel_priority: Optional[int] = Field(None, ge=0, le=7)
    thresh_Xhigh: Optional[int] = None
    thresh_Xlow: Optional[int] = None
    psc: Optional[int] = None
    cpich_rscp: Optional[int] = None
    cpich_ecno: Optional[int] = None
    srxlev: Optional[int] = None

    def info(self) -> NeighborCellInfo:
        return NeighborCellInfo(
            cell_type=self.cell_type,
            rat=self.rat,
            signal_quality_dbm=cpich_rscp_rxpwr_to_dbm(self.cpich_rscp),
            signal_inr_db=cpich_ecno_to_db(self.cpich_ecno),
        )


class LTENeighborCellIntraLTE(BaseNeighborCell):
    cell_type: NeighborCellType = NeighborCellType.NEIGHBOUR_CELL_INTRA
    rat: AccessTechnology = AccessTechnology.LTE
    earfcn: Optional[int] = None
    pcid: Optional[int] = None
    rsrq: Optional[int] = None
    rsrp: Optional[int] = None
    rssi: Optional[int] = None
    sinr: Optional[int] = Field(None, ge=-20, le=30)
    srxlev: Optional[int] = None
    cell_resel_priority: Optional[int] = Field(None, ge=0, le=7)
    s_non_intra_search: Optional[int] = None
    thresh_serving_low: Optional[int] = None
    s_intra_search: Optional[int] = None

    def info(self) -> NeighborCellInfo:
        return NeighborCellInfo(
            cell_type=self.cell_type,
            rat=self.rat,
            signal_quality_dbm=self.rsrp,
            signal_inr_db=self.sinr,
        )

class LTENeighborCellInterLTE(BaseNeighborCell):
    cell_type: NeighborCellType = NeighborCellType.NEIGHBOUR_CELL_INTER
    rat: AccessTechnology = AccessTechnology.LTE
    earfcn: Optional[int] = None
    pcid: Optional[int] = None
    rsrq: Optional[int] = None
    rsrp: Optional[int] = None
    rssi: Optional[int] = None
    sinr: Optional[int] = Field(None, ge=-20, le=30)
    srxlev: Optional[int] = None
    threshX_low: Optional[int] = None
    threshX_high: Optional[int] = None
    cell_resel_priority: Optional[int] = Field(None, ge=0, le=7)

    def info(self) -> NeighborCellInfo:
        return NeighborCellInfo(
            cell_type=self.cell_type,
            rat=self.rat,
            signal_quality_dbm=self.rsrp,
            signal_inr_db=self.sinr,
        )
