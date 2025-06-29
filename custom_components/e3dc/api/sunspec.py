import dataclasses
import enum
import struct
from typing import Any, Self, override

from pymodbus.client import AsyncModbusTcpClient


class _Model:
    def __init_subclass__(cls, struct: struct.Struct) -> None:
        super().__init_subclass__()
        cls.STRUCT = struct

    @classmethod
    def unpack(cls, data: bytes) -> Self:
        return cls(*cls.STRUCT.unpack(data))

    @classmethod
    def unpack_registers(cls, registers: list[int]) -> Self:
        return cls.unpack(b"".join(reg.to_bytes(2, "big") for reg in registers))

    @classmethod
    async def read(cls, client: AsyncModbusTcpClient, address: int) -> Self:
        # Address calc: -1 because of 1-index and then +2 to skip the sunspec header.
        resp = await client.read_holding_registers(
            address + 1,
            count=cls.STRUCT.size // 2,
        )
        return cls.unpack_registers(resp.registers)

    @classmethod
    async def read_many(
        cls, client: AsyncModbusTcpClient, address: int, count: int
    ) -> list[Self]:
        # Address calc: -1 because of 1-index and then +2 to skip the sunspec header.
        resp = await client.read_holding_registers(
            address + 1,
            count=count * (cls.STRUCT.size // 2),
        )
        size_regs = cls.STRUCT.size // 2
        return [
            cls.unpack_registers(resp.registers[start : start + size_regs])
            for start in range(0, len(resp.registers), size_regs)
        ]


# 1
@dataclasses.dataclass(frozen=True)
class Common(_Model, struct=struct.Struct(">16s16s8s8s16sH")):
    manufacturer: str
    model: str  # not set
    options: str
    version: str  # not set
    serial_number: str  # not set
    device_address: int

    @classmethod
    @override
    def unpack(cls, data: bytes) -> Self:
        def handle_str(v: Any) -> Any:  # noqa: ANN401
            if isinstance(v, bytes):
                return v.decode("utf-8", errors="replace").strip("\0")
            return v

        values = cls.STRUCT.unpack(data)
        return cls(*map(handle_str, values))


# 801
@dataclasses.dataclass(frozen=True)
class EnergyStorageBase(_Model, struct=struct.Struct(">H11HL3H4h")):
    class DerTyp(enum.IntEnum):
        STORAGE = 90
        BATTERY = 91
        LITHIUM_ION_BATTERY = 92
        REDOX_FLOW_BATTERY = 93

    class ChaSt(enum.IntEnum):
        OFF = 1
        EMPTY = 2
        DISCHARGING = 3
        CHARGING = 4
        FULL = 5
        HOLDING = 6
        TESTING = 7

    class LocRemCtl(enum.IntEnum):
        REMOTE = 1
        LOCAL = 2

    class Evt(enum.IntFlag):
        UNDER_SOC_MIN_WARNING = 1 << 0
        UNDER_SOC_MIN_ALARM = 1 << 1
        OVER_SOC_MAX_WARNING = 1 << 2
        OVER_SOC_MAX_ALARM = 1 << 3

    der_typ: DerTyp
    wh_rtg: int
    w_max_cha_rte: int
    w_max_dis_cha_rte: int
    dis_cha_rte: int  # not set
    soc_np_max_pct: int
    soc_np_min_pct: int
    max_rsv_pct: int  # not set
    min_rsv_pct: int  # not set
    soc: int
    cha_st: ChaSt
    loc_rem_ctl: LocRemCtl
    evt: Evt  # not set
    der_hb: int  # not set
    controller_hb: int  # not set
    der_alarm_reset: int  # not set
    wh_rtg_sf: int
    w_max_cha_dis_cha_sf: int
    dis_cha_rte_sf: int  # not set
    soc_sf: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "der_typ", self.DerTyp(self.der_typ))
        object.__setattr__(self, "cha_st", self.ChaSt(self.cha_st))
        object.__setattr__(self, "loc_rem_ctl", self.LocRemCtl(self.loc_rem_ctl))
        object.__setattr__(self, "evt", self.Evt(self.evt))


# 802
@dataclasses.dataclass(frozen=True)
class BatteryBase(_Model, struct=struct.Struct(">2HLH2L3HHh2H4h")):
    class BatTyp(enum.IntEnum):
        NOT_APPLICABLE_UNKNOWN = 0
        LEAD_ACID = 1
        NICKEL_METAL_HYDRATE = 2
        NICKEL_CADMIUM = 3
        LITHIUM_ION = 4
        CARBON_ZINC = 5
        ZINC_CHLORIDE = 6
        ALKALINE = 7
        RECHARGEABLE_ALKALINE = 8
        SODIUM_SULFUR = 9
        FLOW = 10
        OTHER = 99

    class BatSt(enum.IntEnum):
        DISCONNECTED = 1
        INITIALIZING = 2
        CONNECTED = 3
        STANDBY = 4
        SOC_PROTECTION = 5

    class Evt1(enum.IntFlag):
        COMMUNICATION_ERROR = 1 << 0
        OVER_TEMP_ALARM = 1 << 1
        UNDER_TEMP_ALARM = 1 << 2
        OVER_TEMP_WARNING = 1 << 3
        UNDER_TEMP_WARNING = 1 << 4
        OVER_CHARGE_CURRENT_ALARM = 1 << 5
        OVER_DISCHARGE_CURRENT_ALARM = 1 << 6
        OVER_CHARGE_CURRENT_WARNING = 1 << 7
        OVER_DISCHARGE_CURRENT_WARNING = 1 << 8
        VOLTAGE_IMBALANCE_WARNING = 1 << 9
        CURRENT_IMBALANCE_WARNING = 1 << 10
        OVER_VOLT_ALARM = 1 << 11
        UNDER_VOLT_ALARM = 1 << 12
        OVER_VOLT_WARNING = 1 << 13
        UNDER_VOLT_WARNING = 1 << 14
        CONTACTOR_ERROR = 1 << 15
        FAN_ERROR = 1 << 16
        CONTACTOR_STATUS = 1 << 17
        GROUND_FAULT = 1 << 18
        OPEN_DOOR_ERROR = 1 << 19
        OTHER_ALARM = 1 << 20
        OTHER_WARNING = 1 << 21

    class ReqPcsSt(enum.IntEnum):
        NO_REQUEST = 0
        START = 1
        STOP = 2
        UNSUPPORTED = 0xFFFF

    class SetOperation(enum.IntEnum):
        CONNECT = 1
        DISCONNECT = 2
        UNSUPPORTED = 0xFFFF

    class SetPcsState(enum.IntEnum):
        STOPPED = 1
        STANDBY = 2
        STARTED = 3
        UNSUPPORTED = 0xFFFF

    bat_typ: BatTyp
    bat_st: BatSt
    cycle_ct: int  # not set
    soh: int  # not set
    evt1: Evt1  # not set
    evt2: int  # not set
    vol: int  # not set
    max_bat_a_cha: int
    max_bat_a_discha: int
    bat_req_pcs_st: ReqPcsSt  # not set
    bat_req_w: int  # not set
    b_set_operation: SetOperation  # not set
    b_set_pcs_state: SetPcsState  # not set
    soh_sf: int  # not set
    vol_sf: int  # not set
    max_bat_a_sf: int
    bat_req_w_sf: int  # not set

    def __post_init__(self) -> None:
        object.__setattr__(self, "bat_typ", self.BatTyp(self.bat_typ))
        object.__setattr__(self, "bat_st", self.BatSt(self.bat_st))
        object.__setattr__(self, "evt1", self.Evt1(self.evt1))
        object.__setattr__(self, "bat_req_pcs_st", self.ReqPcsSt(self.bat_req_pcs_st))
        object.__setattr__(
            self, "b_set_operation", self.SetOperation(self.b_set_operation)
        )
        object.__setattr__(
            self, "b_set_pcs_state", self.SetPcsState(self.b_set_pcs_state)
        )


# 803
@dataclasses.dataclass(frozen=True)
class LithiumIonBattery(_Model, struct=struct.Struct(">5HhHhH3h4h")):
    @dataclasses.dataclass(frozen=True)
    class String(_Model, struct=struct.Struct(">3Hh3H2hHLLHH")):
        class Evt1(enum.IntFlag):
            COMMUNICATION_ERROR = 1 << 0
            OVER_TEMP_ALARM = 1 << 1
            UNDER_TEMP_ALARM = 1 << 2
            OVER_TEMP_WARNING = 1 << 3
            UNDER_TEMP_WARNING = 1 << 4
            OVER_CHARGE_CURRENT_ALARM = 1 << 5
            OVER_DISCHARGE_CURRENT_ALARM = 1 << 6
            OVER_CHARGE_CURRENT_WARNING = 1 << 7
            OVER_DISCHARGE_CURRENT_WARNING = 1 << 8
            OVER_VOLT_ALARM = 1 << 9
            UNDER_VOLT_ALARM = 1 << 10
            OVER_VOLT_WARNING = 1 << 11
            UNDER_VOLT_WARNING = 1 << 12
            CONTACTOR_ERROR = 1 << 13
            FAN_ERROR = 1 << 14
            CONTACTOR_STATUS = 1 << 15
            GROUND_FAULT = 1 << 16
            OPEN_DOOR_ERROR = 1 << 17
            OTHER_ALARM = 1 << 18
            OTHER_WARNING = 1 << 19
            STRING_ENABLED = 1 << 20

        class ConFail(enum.IntEnum):
            NO_FAILURE = 0
            BUTTON_PUSHED = 1
            STR_GROUND_FAULT = 2
            OUTSIDE_VOLTAGE_RANGE = 3
            UNSUPPORTED = 0xFFFF

        class SetEna(enum.IntEnum):
            ENABLE = 1
            DISABLE = 2
            UNSUPPORTED = 0xFFFF

        mod_ct: int  # not set
        soc: int  # not set
        soh: int  # not set
        cur: int
        max_cell_vol: int
        min_cell_vol: int
        cell_vol_loc: int  # not set
        max_mod_tmp: int  # not set
        min_mod_tmp: int  # not set
        mod_tmp_loc: int  # not set
        evt1: Evt1  # not set
        evt2: int  # not set
        con_fail: ConFail  # not set
        set_ena: SetEna  # not set

        def __post_init__(self) -> None:
            object.__setattr__(self, "evt1", self.Evt1(self.evt1))
            object.__setattr__(self, "con_fail", self.ConFail(self.con_fail))
            object.__setattr__(self, "set_ena", self.SetEna(self.set_ena))

    b_con_str_ct: int
    b_max_cell_vol: int  # not set
    b_max_cell_vol_loc: int  # not set
    b_min_cell_vol: int  # not set
    b_min_cell_vol_loc: int  # not set
    b_max_mod_tmp: int
    b_max_mod_tmp_loc: int  # not set
    b_min_mod_tmp: int
    b_min_mod_tmp_loc: int  # not set
    b_tot_dc_cur: int
    b_max_str_cur: int
    b_min_str_cur: int
    b_cell_vol_sf: int
    b_mod_tmp_sf: int
    b_current_sf: int
    str_so_h_sf: int  # not set

    strings: list[String] = dataclasses.field(default_factory=list)

    @classmethod
    @override
    async def read(cls, client: AsyncModbusTcpClient, address: int) -> Self:
        resp = await client.read_holding_registers(
            address,
            count=1 + cls.STRUCT.size // 2,
        )

        length = resp.registers[0]
        this = cls.unpack_registers(resp.registers[1:])

        string_count = (2 * length - cls.STRUCT.size) // cls.String.STRUCT.size
        strings = await cls.String.read_many(
            client,
            address + (this.STRUCT.size // 2),
            string_count,
        )
        object.__setattr__(this, "strings", strings)

        return this


# 203


@dataclasses.dataclass(frozen=True)
class AbcnMeter(_Model, struct=struct.Struct(">4hh8hhhh4hh4hh4hh4hh8Lh8Lh16LhL")):
    class Evt(enum.IntFlag):
        POWER_FAILURE = 1 << 2
        UNDER_VOLTAGE = 1 << 3
        LOW_PF = 1 << 4
        OVER_CURRENT = 1 << 5
        OVER_VOLTAGE = 1 << 6
        MISSING_SENSOR = 1 << 7
        RESERVED1 = 1 << 8
        RESERVED2 = 1 << 9
        RESERVED3 = 1 << 10
        RESERVED4 = 1 << 11
        RESERVED5 = 1 << 12
        RESERVED6 = 1 << 13
        RESERVED7 = 1 << 14
        RESERVED8 = 1 << 15
        OEM01 = 1 << 16
        OEM02 = 1 << 17
        OEM03 = 1 << 18
        OEM04 = 1 << 19
        OEM05 = 1 << 20
        OEM06 = 1 << 21
        OEM07 = 1 << 22
        OEM08 = 1 << 23
        OEM09 = 1 << 24
        OEM10 = 1 << 25
        OEM11 = 1 << 26
        OEM12 = 1 << 27
        OEM13 = 1 << 28
        OEM14 = 1 << 29
        OEM15 = 1 << 30

    a: int  # not set
    aph_a: int  # not set
    aph_b: int  # not set
    aph_c: int  # not set
    a_sf: int  # not set
    ph_v: int  # not set
    ph_vph_a: int
    ph_vph_b: int
    ph_vph_c: int
    ppv: int  # not set
    ph_vph_ab: int  # not set
    ph_vph_bc: int  # not set
    ph_vph_ca: int  # not set
    v_sf: int  # not set
    hz: int  # not set
    hz_sf: int  # not set
    w: int
    wph_a: int
    wph_b: int
    wph_c: int
    w_sf: int
    va: int  # not set
    v_aph_a: int  # not set
    v_aph_b: int  # not set
    v_aph_c: int  # not set
    va_sf: int  # not set
    var: int  # not set
    va_rph_a: int  # not set
    va_rph_b: int  # not set
    va_rph_c: int  # not set
    var_sf: int  # not set
    pf: int  # not set
    p_fph_a: int  # not set
    p_fph_b: int  # not set
    p_fph_c: int  # not set
    pf_sf: int  # not set
    tot_wh_exp: int
    tot_wh_exp_ph_a: int
    tot_wh_exp_ph_b: int
    tot_wh_exp_ph_c: int
    tot_wh_imp: int
    tot_wh_imp_ph_a: int
    tot_wh_imp_ph_b: int
    tot_wh_imp_ph_c: int
    tot_wh_sf: int
    tot_v_ah_exp: int
    tot_v_ah_exp_ph_a: int
    tot_v_ah_exp_ph_b: int
    tot_v_ah_exp_ph_c: int
    tot_v_ah_imp: int
    tot_v_ah_imp_ph_a: int
    tot_v_ah_imp_ph_b: int
    tot_v_ah_imp_ph_c: int
    tot_v_ah_sf: int
    tot_v_arh_imp_q1: int
    tot_v_arh_imp_q1_ph_a: int
    tot_v_arh_imp_q1_ph_b: int
    tot_v_arh_imp_q1_ph_c: int
    tot_v_arh_imp_q2: int
    tot_v_arh_imp_q2_ph_a: int
    tot_v_arh_imp_q2_ph_b: int
    tot_v_arh_imp_q2_ph_c: int
    tot_v_arh_exp_q3: int
    tot_v_arh_exp_q3_ph_a: int
    tot_v_arh_exp_q3_ph_b: int
    tot_v_arh_exp_q3_ph_c: int
    tot_v_arh_exp_q4: int
    tot_v_arh_exp_q4_ph_a: int
    tot_v_arh_exp_q4_ph_b: int
    tot_v_arh_exp_q4_ph_c: int
    tot_v_arh_sf: int  # not set
    evt: Evt  # not set

    def __post_init__(self) -> None:
        object.__setattr__(self, "evt", self.Evt(self.evt))


# 103
@dataclasses.dataclass(frozen=True)
class Inverter(_Model, struct=struct.Struct(">4Hh6HhhhhhhhhhhhLhHhHhhh4hh2H6L")):
    class St(enum.IntEnum):
        OFF = 1
        SLEEPING = 2
        STARTING = 3
        MPPT = 4
        THROTTLED = 5
        SHUTTING_DOWN = 6
        FAULT = 7
        STANDBY = 8

    class Evt1(enum.IntFlag):
        GROUND_FAULT = 1 << 0
        DC_OVER_VOLT = 1 << 1
        AC_DISCONNECT = 1 << 2
        DC_DISCONNECT = 1 << 3
        GRID_DISCONNECT = 1 << 4
        CABINET_OPEN = 1 << 5
        MANUAL_SHUTDOWN = 1 << 6
        OVER_TEMP = 1 << 7
        OVER_FREQUENCY = 1 << 8
        UNDER_FREQUENCY = 1 << 9
        AC_OVER_VOLT = 1 << 10
        AC_UNDER_VOLT = 1 << 11
        BLOWN_STRING_FUSE = 1 << 12
        UNDER_TEMP = 1 << 13
        MEMORY_LOSS = 1 << 14
        HW_TEST_FAILURE = 1 << 15

    a: int
    aph_a: int
    aph_b: int
    aph_c: int
    a_sf: int
    pp_vph_ab: int  # not set
    pp_vph_bc: int  # not set
    pp_vph_ca: int  # not set
    ph_vph_a: int
    ph_vph_b: int
    ph_vph_c: int
    v_sf: int
    w: int
    w_sf: int
    hz: int  # not set
    hz_sf: int  # not set
    va: int  # not set
    va_sf: int  # not set
    v_ar: int  # not set
    v_ar_sf: int  # not set
    pf: int  # not set
    pf_sf: int  # not set
    wh: int
    wh_sf: int
    dca: int
    dca_sf: int
    dcv: int
    dcv_sf: int
    dcw: int
    dcw_sf: int
    tmp_cab: int
    tmp_snk: int
    tmp_trns: int
    tmp_ot: int
    tmp_sf: int
    st: St
    st_vnd: int  # not set
    evt1: Evt1
    evt2: int  # not set
    evt_vnd1: int  # not set
    evt_vnd2: int  # not set
    evt_vnd3: int  # not set
    evt_vnd4: int  # not set

    def __post_init__(self) -> None:
        object.__setattr__(self, "st", self.St(self.st))
        object.__setattr__(self, "evt1", self.Evt1(self.evt1))


class E3dc:
    def __init__(self, client: AsyncModbusTcpClient) -> None:
        self._client = client

    @classmethod
    async def connect(cls, host: str) -> Self:
        client = AsyncModbusTcpClient(host, name="e3dc")
        await client.connect()
        return cls(client)

    async def read_common(self) -> Common:
        return await Common.read(self._client, 40003)

    async def read_storage(self) -> EnergyStorageBase:
        return await EnergyStorageBase.read(self._client, 40071)
