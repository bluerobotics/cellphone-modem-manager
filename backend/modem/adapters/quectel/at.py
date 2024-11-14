# NOTE: Store only Quectel-specific AT commands here; reuse global ones from modem.at

from enum import Enum

class QuectelATCommand(Enum):
    CONFIGURATION = "AT+QCFG"
    ENGINEER_MODE = "AT+QENG"
    PING= "AT+QPING"
    SIM_STATUS = "AT+QSIMSTAT"
