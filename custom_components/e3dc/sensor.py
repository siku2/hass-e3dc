import dataclasses
from collections.abc import Callable

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfEnergy, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .api import sunspec
from .coordinator import E3dcCoordinator, E3dcEntity


@dataclasses.dataclass(kw_only=True, frozen=True)
class E3dcSensorEntityDescription(SensorEntityDescription):
    value_fn: Callable[[E3dcCoordinator], str | int | float | None]


_STORAGE_SENSORS = [
    E3dcSensorEntityDescription(
        key="storage_wh_rtg",
        value_fn=lambda e3dc: e3dc.storage.wh_rtg * (10**e3dc.storage.wh_rtg_sf),
        device_class=SensorDeviceClass.ENERGY_STORAGE,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    E3dcSensorEntityDescription(
        key="storage_w_max_cha_rte",
        value_fn=lambda e3dc: e3dc.storage.w_max_cha_rte
        * (10**e3dc.storage.w_max_cha_dis_cha_sf),
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    E3dcSensorEntityDescription(
        key="storage_w_max_dis_cha_rte",
        value_fn=lambda e3dc: e3dc.storage.w_max_dis_cha_rte
        * (10**e3dc.storage.w_max_cha_dis_cha_sf),
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    E3dcSensorEntityDescription(
        key="storage_soc",
        value_fn=lambda e3dc: e3dc.storage.soc * (10**e3dc.storage.soc_sf),
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    E3dcSensorEntityDescription(
        key="storage_cha_st",
        value_fn=lambda e3dc: e3dc.storage.cha_st.name,
        device_class=SensorDeviceClass.ENUM,
        options=sunspec.EnergyStorageBase.ChaSt._member_names_,
    ),
    E3dcSensorEntityDescription(
        key="storage_loc_rem_ctl",
        value_fn=lambda e3dc: e3dc.storage.loc_rem_ctl.name,
        device_class=SensorDeviceClass.ENUM,
        options=sunspec.EnergyStorageBase.LocRemCtl._member_names_,
    ),
]


async def async_setup_entry(
    _hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities(
        [E3dcSensor(config_entry.runtime_data, desc) for desc in _STORAGE_SENSORS]
    )


class E3dcSensor(E3dcEntity[E3dcSensorEntityDescription], SensorEntity):
    @property
    def native_value(self) -> str | int | float | None:
        return self.entity_description.value_fn(self.coordinator)
