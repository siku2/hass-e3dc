import dataclasses
from collections.abc import Callable
from typing import Literal

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .api import sunspec
from .coordinator import E3dcCoordinator, E3dcEntity

type ValueType = str | int | float | None


@dataclasses.dataclass(kw_only=True, frozen=True)
class E3dcSensorEntityDescription(SensorEntityDescription):
    value_fn: Callable[[E3dcCoordinator], ValueType]


_STORAGE_SENSORS = [
    E3dcSensorEntityDescription(
        key="wh_rtg",
        value_fn=lambda e3dc: e3dc.storage.wh_rtg * (10**e3dc.storage.wh_rtg_sf),
        device_class=SensorDeviceClass.ENERGY_STORAGE,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    ),
    E3dcSensorEntityDescription(
        key="w_max_cha_rte",
        value_fn=lambda e3dc: e3dc.storage.w_max_cha_rte
        * (10**e3dc.storage.w_max_cha_dis_cha_sf),
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    E3dcSensorEntityDescription(
        key="w_max_dis_cha_rte",
        value_fn=lambda e3dc: e3dc.storage.w_max_dis_cha_rte
        * (10**e3dc.storage.w_max_cha_dis_cha_sf),
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    E3dcSensorEntityDescription(
        key="soc",
        value_fn=lambda e3dc: e3dc.storage.soc * (10**e3dc.storage.soc_sf),
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    E3dcSensorEntityDescription(
        key="cha_st",
        value_fn=lambda e3dc: e3dc.storage.cha_st.name.lower(),
        device_class=SensorDeviceClass.ENUM,
        options=sunspec.EnergyStorageBase.ChaSt._member_names_,
    ),
    E3dcSensorEntityDescription(
        key="loc_rem_ctl",
        value_fn=lambda e3dc: e3dc.storage.loc_rem_ctl.name.lower(),
        device_class=SensorDeviceClass.ENUM,
        options=sunspec.EnergyStorageBase.LocRemCtl._member_names_,
    ),
]

_INVERTER_SENSORS = [
    E3dcSensorEntityDescription(
        key="a",
        value_fn=lambda e3dc: e3dc.inverter.a * (10**e3dc.inverter.a_sf),
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    E3dcSensorEntityDescription(
        key="aph_a",
        value_fn=lambda e3dc: e3dc.inverter.aph_a * (10**e3dc.inverter.a_sf),
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    E3dcSensorEntityDescription(
        key="aph_b",
        value_fn=lambda e3dc: e3dc.inverter.aph_b * (10**e3dc.inverter.a_sf),
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    E3dcSensorEntityDescription(
        key="aph_c",
        value_fn=lambda e3dc: e3dc.inverter.aph_c * (10**e3dc.inverter.a_sf),
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    E3dcSensorEntityDescription(
        key="ph_vph_a",
        value_fn=lambda e3dc: e3dc.inverter.ph_vph_a * (10**e3dc.inverter.v_sf),
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    E3dcSensorEntityDescription(
        key="ph_vph_b",
        value_fn=lambda e3dc: e3dc.inverter.ph_vph_b * (10**e3dc.inverter.v_sf),
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    E3dcSensorEntityDescription(
        key="ph_vph_c",
        value_fn=lambda e3dc: e3dc.inverter.ph_vph_c * (10**e3dc.inverter.v_sf),
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    E3dcSensorEntityDescription(
        key="w",
        value_fn=lambda e3dc: e3dc.inverter.w * (10**e3dc.inverter.w_sf),
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    E3dcSensorEntityDescription(
        key="wh",
        value_fn=lambda e3dc: e3dc.inverter.wh * (10**e3dc.inverter.wh_sf),
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    E3dcSensorEntityDescription(
        key="dca",
        value_fn=lambda e3dc: e3dc.inverter.dca * (10**e3dc.inverter.dca_sf),
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    E3dcSensorEntityDescription(
        key="dcv",
        value_fn=lambda e3dc: e3dc.inverter.dcv * (10**e3dc.inverter.dcv_sf),
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    E3dcSensorEntityDescription(
        key="dcw",
        value_fn=lambda e3dc: e3dc.inverter.dcw * (10**e3dc.inverter.dcw_sf),
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    E3dcSensorEntityDescription(
        key="tmp_cab",
        value_fn=lambda e3dc: e3dc.inverter.tmp_cab * (10**e3dc.inverter.tmp_sf),
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    E3dcSensorEntityDescription(
        key="tmp_snk",
        value_fn=lambda e3dc: e3dc.inverter.tmp_snk * (10**e3dc.inverter.tmp_sf),
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    E3dcSensorEntityDescription(
        key="tmp_trns",
        value_fn=lambda e3dc: e3dc.inverter.tmp_trns * (10**e3dc.inverter.tmp_sf),
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    E3dcSensorEntityDescription(
        key="tmp_ot",
        value_fn=lambda e3dc: e3dc.inverter.tmp_ot * (10**e3dc.inverter.tmp_sf),
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    E3dcSensorEntityDescription(
        key="st",
        value_fn=lambda e3dc: e3dc.inverter.st.name.lower(),
        device_class=SensorDeviceClass.ENUM,
        options=sunspec.Inverter.St._member_names_,
    ),
]

_BATTERY_SENSORS = [
    E3dcSensorEntityDescription(
        key="con_str_ct",
        value_fn=lambda e3dc: e3dc.li_battery.con_str_ct,
    ),
    E3dcSensorEntityDescription(
        key="max_mod_tmp",
        value_fn=lambda e3dc: e3dc.li_battery.max_mod_tmp
        * (10**e3dc.li_battery.mod_tmp_sf),
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    E3dcSensorEntityDescription(
        key="min_mod_tmp",
        value_fn=lambda e3dc: e3dc.li_battery.min_mod_tmp
        * (10**e3dc.li_battery.mod_tmp_sf),
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    E3dcSensorEntityDescription(
        key="tot_dc_cur",
        value_fn=lambda e3dc: e3dc.li_battery.tot_dc_cur
        * (10**e3dc.li_battery.current_sf),
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    E3dcSensorEntityDescription(
        key="max_str_cur",
        value_fn=lambda e3dc: e3dc.li_battery.max_str_cur
        * (10**e3dc.li_battery.current_sf),
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    E3dcSensorEntityDescription(
        key="min_str_cur",
        value_fn=lambda e3dc: e3dc.li_battery.min_str_cur
        * (10**e3dc.li_battery.current_sf),
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
]


@dataclasses.dataclass(kw_only=True, frozen=True)
class E3dcMeterSensorEntityDescription(SensorEntityDescription):
    value_fn: Callable[[sunspec.AbcnMeter], ValueType]


_METER_SENSORS = [
    E3dcMeterSensorEntityDescription(
        key="ph_vph_a",
        value_fn=lambda meter: meter.ph_vph_a * (10**meter.v_sf),
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    E3dcMeterSensorEntityDescription(
        key="ph_vph_b",
        value_fn=lambda meter: meter.ph_vph_b * (10**meter.v_sf),
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    E3dcMeterSensorEntityDescription(
        key="ph_vph_c",
        value_fn=lambda meter: meter.ph_vph_c * (10**meter.v_sf),
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    E3dcMeterSensorEntityDescription(
        key="w",
        value_fn=lambda meter: meter.w * (10**meter.w_sf),
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    E3dcMeterSensorEntityDescription(
        key="wph_a",
        value_fn=lambda meter: meter.wph_a * (10**meter.w_sf),
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    E3dcMeterSensorEntityDescription(
        key="wph_b",
        value_fn=lambda meter: meter.wph_b * (10**meter.w_sf),
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    E3dcMeterSensorEntityDescription(
        key="wph_c",
        value_fn=lambda meter: meter.wph_c * (10**meter.w_sf),
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    E3dcMeterSensorEntityDescription(
        key="tot_wh_exp",
        value_fn=lambda meter: meter.tot_wh_exp * (10**meter.tot_wh_sf),
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    E3dcMeterSensorEntityDescription(
        key="tot_wh_exp_ph_a",
        value_fn=lambda meter: meter.tot_wh_exp_ph_a * (10**meter.tot_wh_sf),
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    E3dcMeterSensorEntityDescription(
        key="tot_wh_exp_ph_b",
        value_fn=lambda meter: meter.tot_wh_exp_ph_b * (10**meter.tot_wh_sf),
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    E3dcMeterSensorEntityDescription(
        key="tot_wh_exp_ph_c",
        value_fn=lambda meter: meter.tot_wh_exp_ph_c * (10**meter.tot_wh_sf),
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    E3dcMeterSensorEntityDescription(
        key="tot_wh_imp",
        value_fn=lambda meter: meter.tot_wh_imp * (10**meter.tot_wh_sf),
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    E3dcMeterSensorEntityDescription(
        key="tot_wh_imp_ph_a",
        value_fn=lambda meter: meter.tot_wh_imp_ph_a * (10**meter.tot_wh_sf),
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    E3dcMeterSensorEntityDescription(
        key="tot_wh_imp_ph_b",
        value_fn=lambda meter: meter.tot_wh_imp_ph_b * (10**meter.tot_wh_sf),
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    E3dcMeterSensorEntityDescription(
        key="tot_wh_imp_ph_c",
        value_fn=lambda meter: meter.tot_wh_imp_ph_c * (10**meter.tot_wh_sf),
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
]


async def async_setup_entry(
    _hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coord = config_entry.runtime_data
    async_add_entities([E3dcSensor(coord, desc) for desc in _STORAGE_SENSORS])
    async_add_entities(
        [E3dcSensor(coord, desc, device_key="inverter") for desc in _INVERTER_SENSORS]
    )
    async_add_entities(
        [E3dcSensor(coord, desc, device_key="battery") for desc in _BATTERY_SENSORS]
    )
    async_add_entities(
        [E3dcMeterSensor(coord, desc, "root_meter") for desc in _METER_SENSORS]
    )
    async_add_entities(
        [E3dcMeterSensor(coord, desc, "extra_meter") for desc in _METER_SENSORS]
    )


class E3dcSensor(E3dcEntity[E3dcSensorEntityDescription], SensorEntity):
    @property
    def native_value(self) -> ValueType:
        return self.entity_description.value_fn(self.coordinator)


class E3dcMeterSensor(E3dcEntity[E3dcMeterSensorEntityDescription], SensorEntity):
    def __init__(
        self,
        coordinator: E3dcCoordinator,
        entity_description: E3dcMeterSensorEntityDescription,
        meter: Literal["root_meter", "extra_meter"],
    ) -> None:
        super().__init__(coordinator, entity_description, device_key=meter)
        self._meter = meter

    @property
    def native_value(self) -> ValueType:
        meter = (
            self.coordinator.root_meter
            if self._meter == "root_meter"
            else self.coordinator.extra_meter
        )
        return self.entity_description.value_fn(meter)
