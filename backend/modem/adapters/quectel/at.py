# NOTE: Store only Quectel-specific AT commands here; reuse global ones from modem.at

from enum import Enum

class QuectelATCommand(Enum):
    CONFIGURATION = "AT+QCFG"
    ENGINEER_MODE = "AT+QENG"
    PING = "AT+QPING"
    SIM_STATUS = "AT+QSIMSTAT"
    PACKET_DATA_COUNTER = "AT+QGDCNT"
    AUTO_PACKET_DATA_COUNTER = "AT+QAUGDCNT"
    AUTO_TIME_SYNC = "AT+CTZU"
    CONFIGURE_PDP_AUTH = "AT+QICSGP"
    SIGNAL_QUALITY = "AT+QCSQ"
    NETWORK_INFO = "AT+QNWINFO"
    TCP_PDP_CONTEXT = "AT+QIACT"
    DNS_RESOLVE = "AT+QIDNSGIP"
