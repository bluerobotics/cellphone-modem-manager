import asyncio
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import AsyncGenerator, Callable, Dict, List, Optional, Union
from urllib.parse import quote

import aiohttp

from config import BLUE_OS_HOST
from modem.at import ATCommand, ATDivider
from modem.adapters.quectel.at import QuectelATCommand
from modem.modem import Modem

COMMANDER_API = f"http://{BLUE_OS_HOST}:9100/v1.0/command/host"

ATCommandType = Union[ATCommand, QuectelATCommand]


class StepType(Enum):
    AT = "at"
    SHELL = "shell"
    INTERNAL = "internal"


# --- Output sanitizers ---

def sanitize_iccid(output: str) -> str:
    """Mask ICCID digits in AT+CCID output, keeping first 6 and last 4 visible."""
    return re.sub(r'\b(\d{6})\d{9,14}(\d{4})\b', r'\1*****\2', output)


# --- Step definition ---

@dataclass
class ReportStep:
    name: str
    step_type: StepType
    section: str
    at_command: Optional[ATCommandType] = None
    divider: ATDivider = ATDivider.UNDEFINED
    data: str = ""
    shell_command: Optional[str] = None
    internal_handler: Optional[Callable[..., str]] = field(default=None, repr=False)
    delay: float = 1.0
    sanitizer: Optional[Callable[[str], str]] = field(default=None, repr=False)

    @property
    def command_str(self) -> str:
        if self.step_type == StepType.AT and self.at_command:
            return f"{self.at_command.value}{self.divider.value}{self.data}"
        if self.step_type == StepType.SHELL:
            return self.shell_command or ""
        return "(internal)"


# --- Internal step handlers ---

def read_manager_settings(modem: Modem) -> str:
    try:
        return modem._manager.settings.model_dump_json(indent=2)
    except Exception:
        try:
            return json.dumps(modem._manager.settings.dict(), indent=2)
        except Exception as e:
            return f"ERROR reading settings: {e}"


# --- Diagnostic procedure steps ---

S_STATE = "Extension State"
S_MODEM = "Modem Connectivity Diagnostic"
S_BLUEOS = "BlueOS Connectivity Diagnostic"

DIAGNOSTIC_STEPS: List[ReportStep] = [
    # Extension State
    ReportStep("Modem manager settings",            StepType.INTERNAL, S_STATE, internal_handler=read_manager_settings),
    # Modem Connectivity Diagnostic
    ReportStep("Enable verbose errors",             StepType.AT, S_MODEM, at_command=ATCommand.REPORT_MOBILE_EQUIPMENT_ERROR, divider=ATDivider.EQ, data="2"),
    ReportStep("Modem identification & firmware",   StepType.AT, S_MODEM, at_command=ATCommand.ATI),
    ReportStep("SIM status - PIN check",            StepType.AT, S_MODEM, at_command=ATCommand.SIM_PIN_STATUS, divider=ATDivider.QUESTION),
    ReportStep("SIM status - CCID",                 StepType.AT, S_MODEM, at_command=ATCommand.SIM_CARD_IDENTIFICATION, sanitizer=sanitize_iccid),
    ReportStep("RF signal quality (CSQ)",           StepType.AT, S_MODEM, at_command=ATCommand.CHECK_SIGNAL_QUALITY),
    ReportStep("RF signal quality (QCSQ)",          StepType.AT, S_MODEM, at_command=QuectelATCommand.SIGNAL_QUALITY),
    ReportStep("Serving cell info",                 StepType.AT, S_MODEM, at_command=QuectelATCommand.ENGINEER_MODE, divider=ATDivider.EQ, data='"servingcell"', delay=2.0),
    ReportStep("Network registration (COPS)",       StepType.AT, S_MODEM, at_command=ATCommand.CONFIGURE_OPERATOR, divider=ATDivider.QUESTION, delay=2.0),
    ReportStep("Network registration (CREG)",       StepType.AT, S_MODEM, at_command=ATCommand.NETWORK_REGISTRATION, divider=ATDivider.QUESTION),
    ReportStep("Network registration (CGREG)",      StepType.AT, S_MODEM, at_command=ATCommand.GPRS_NETWORK_REGISTRATION, divider=ATDivider.QUESTION),
    ReportStep("Network registration (CEREG)",      StepType.AT, S_MODEM, at_command=ATCommand.EPS_NETWORK_REGISTRATION, divider=ATDivider.QUESTION),
    ReportStep("Network info (QNWINFO)",            StepType.AT, S_MODEM, at_command=QuectelATCommand.NETWORK_INFO),
    ReportStep("PDP context configuration",         StepType.AT, S_MODEM, at_command=ATCommand.CONFIGURE_PDP_CONTEXT, divider=ATDivider.QUESTION),
    ReportStep("PDP attachment state",              StepType.AT, S_MODEM, at_command=ATCommand.PS_ATTACH, divider=ATDivider.QUESTION),
    ReportStep("PDP activation state",              StepType.AT, S_MODEM, at_command=ATCommand.PDP_CONTEXT_ACTIVATE, divider=ATDivider.QUESTION),
    ReportStep("PDP context read dynamic params",   StepType.AT, S_MODEM, at_command=ATCommand.PDP_CONTEXT_READ_DYNAMIC, delay=2.0),
    ReportStep("Quectel data stack state",          StepType.AT, S_MODEM, at_command=QuectelATCommand.TCP_PDP_CONTEXT, divider=ATDivider.QUESTION),
    ReportStep("USB networking mode",               StepType.AT, S_MODEM, at_command=QuectelATCommand.CONFIGURATION, divider=ATDivider.EQ, data='"usbnet"'),
    ReportStep("Roaming configuration",             StepType.AT, S_MODEM, at_command=QuectelATCommand.CONFIGURATION, divider=ATDivider.EQ, data='"roamservice"'),
    ReportStep("Ping 8.8.8.8",                     StepType.AT, S_MODEM, at_command=QuectelATCommand.PING, divider=ATDivider.EQ, data='1,"8.8.8.8"', delay=12.0),
    ReportStep("Ping google.com",                   StepType.AT, S_MODEM, at_command=QuectelATCommand.PING, divider=ATDivider.EQ, data='1,"google.com",10,1,1', delay=12.0),
    ReportStep("DNS resolution test",               StepType.AT, S_MODEM, at_command=QuectelATCommand.DNS_RESOLVE, divider=ATDivider.EQ, data='1,"google.com"', delay=8.0),
    # BlueOS Connectivity Diagnostic
    ReportStep("Network interfaces (link)",         StepType.SHELL, S_BLUEOS, shell_command="ip link"),
    ReportStep("Network interfaces (addr)",         StepType.SHELL, S_BLUEOS, shell_command="ip addr"),
    ReportStep("Network routes",                    StepType.SHELL, S_BLUEOS, shell_command="ip route"),
    ReportStep("DNS configuration",                 StepType.SHELL, S_BLUEOS, shell_command="cat /etc/resolv.conf"),
]


# --- Report generator ---

class ReportGenerator:
    _instances: Dict[str, "ReportGenerator"] = {}

    def __init__(self, modem_id: str, modem: Modem):
        self.modem_id = modem_id
        self.modem = modem
        self.running = False
        self.events: List[dict] = []
        self._task: Optional[asyncio.Task] = None
        self.full_report: Optional[str] = None

    @classmethod
    def get(cls, modem_id: str) -> Optional["ReportGenerator"]:
        return cls._instances.get(modem_id)

    @classmethod
    def get_or_start(cls, modem_id: str, modem: Modem) -> "ReportGenerator":
        instance = cls._instances.get(modem_id)
        if instance and instance.running:
            return instance
        instance = cls(modem_id, modem)
        cls._instances[modem_id] = instance
        return instance

    async def start(self) -> None:
        if self.running:
            return
        self.running = True
        self.events = []
        self.full_report = None
        self._task = asyncio.create_task(self._run())

    def _emit(self, event: dict) -> None:
        self.events.append(event)

    async def _run_at_command(self, cmd, step: ReportStep) -> str:
        try:
            return await cmd.command(
                step.at_command,
                step.divider,
                step.data,
                cmd_id_response=False,
                delay=step.delay,
                raw_response=True,
            )
        except Exception as e:
            return f"ERROR: {e}"

    async def _run_shell_command(self, command: str) -> str:
        try:
            url = f"{COMMANDER_API}?command={quote(command)}&i_know_what_i_am_doing=true"
            async with aiohttp.ClientSession() as session:
                async with session.post(url) as resp:
                    resp.raise_for_status()
                    data = await resp.json()

            stdout = data.get("stdout", "").strip("'").replace("\\n", "\n")
            stderr = data.get("stderr", "").strip("'").replace("\\n", "\n")
            output = stdout
            if stderr.strip():
                output += stderr
            return output
        except Exception as e:
            return f"ERROR: {e}"

    async def _run(self) -> None:
        total = len(DIAGNOSTIC_STEPS)
        report_lines = [
            "Modem Connectivity Diagnostic Report",
            f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"Modem ID: {self.modem_id}",
            "=" * 60,
            "",
        ]

        cmd = None
        at_available = True

        try:
            cmd = await self.modem.at_commander()
        except Exception as e:
            self._emit({"type": "error", "message": f"Failed to connect to modem AT port: {e}"})
            at_available = False

        try:
            current_section = ""
            for i, step in enumerate(DIAGNOSTIC_STEPS):
                step_num = i + 1

                if step.section != current_section:
                    current_section = step.section
                    report_lines.append(f"\n{'#' * 3} {current_section}")
                    report_lines.append("-" * 40)
                    report_lines.append("")

                self._emit({
                    "type": "step_start",
                    "step": step_num,
                    "total": total,
                    "name": step.name,
                })

                if step.step_type == StepType.AT:
                    if at_available and cmd:
                        output = await self._run_at_command(cmd, step)
                    else:
                        output = "SKIPPED: AT port unavailable"
                elif step.step_type == StepType.SHELL:
                    output = await self._run_shell_command(step.command_str)
                elif step.step_type == StepType.INTERNAL and step.internal_handler:
                    output = step.internal_handler(self.modem)

                clean_output = output.strip() if output else "(no output)"

                if step.sanitizer:
                    clean_output = step.sanitizer(clean_output)

                report_lines.append(f"[{step_num}/{total}] {step.name}")
                report_lines.append(f"  Command: {step.command_str}")
                report_lines.append(f"  Response:")
                for line in clean_output.splitlines():
                    report_lines.append(f"    {line}")
                report_lines.append("")

                self._emit({
                    "type": "step_complete",
                    "step": step_num,
                    "total": total,
                    "name": step.name,
                    "command": step.command_str,
                    "output": clean_output,
                })

        except Exception as e:
            self._emit({"type": "error", "message": str(e)})
            report_lines.append(f"\nFATAL ERROR: {e}")
        finally:
            if cmd:
                cmd._close()

        self.full_report = "\n".join(report_lines)
        self._emit({"type": "report_complete", "report": self.full_report})
        self.running = False

    async def stream_events(self) -> AsyncGenerator[str, None]:
        idx = 0
        while True:
            while idx < len(self.events):
                yield json.dumps(self.events[idx]) + "\n"
                idx += 1

            if not self.running and idx >= len(self.events):
                break

            await asyncio.sleep(0.25)
