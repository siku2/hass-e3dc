import logging
from datetime import timedelta
from typing import override

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import CONNECTION_UPNP, DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .api import sunspec
from .const import CONF_SSDP_UDN, DOMAIN

_LOGGER = logging.getLogger(__name__)

type E3dcConfigEntry = ConfigEntry[E3dcCoordinator]


class E3dcCoordinator(DataUpdateCoordinator[None]):
    config_entry: E3dcConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: E3dcConfigEntry,
    ) -> None:
        super().__init__(
            hass,
            logger=_LOGGER,
            config_entry=config_entry,
            name="e3dc coordinator",
            update_interval=timedelta(seconds=10),
        )

        self._client: sunspec.E3dc | None = None
        self._common: sunspec.Common | None = None
        self._storage: sunspec.EnergyStorageBase | None = None

    @property
    def client(self) -> sunspec.E3dc:
        assert self._client is not None  # noqa: S101
        return self._client

    @property
    def common(self) -> sunspec.Common:
        assert self._common is not None  # noqa: S101
        return self._common

    @property
    def storage(self) -> sunspec.EnergyStorageBase:
        assert self._storage is not None  # noqa: S101
        return self._storage

    @override
    async def _async_update_data(self) -> None:
        if self._client is None:
            self._client = await sunspec.E3dc.connect(self.config_entry.data[CONF_HOST])

        if self._common is None:
            self._common = await self._client.read_common()

        self._storage = await self._client.read_storage()


class E3dcEntity[DescT: EntityDescription](CoordinatorEntity[E3dcCoordinator]):
    _attr_has_entity_name = True

    entity_description: DescT

    def __init__(
        self,
        coordinator: E3dcCoordinator,
        entity_description: DescT,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_{entity_description.key}"
        )
        self._attr_translation_key = entity_description.key

        connections: set[tuple[str, str]] = set()
        if udn := coordinator.config_entry.data.get(CONF_SSDP_UDN):
            connections.add((CONNECTION_UPNP, str(udn)))

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            manufacturer=coordinator.common.manufacturer,
            model=coordinator.common.options,
            connections=connections,
        )
