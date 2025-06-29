from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .coordinator import E3dcConfigEntry, E3dcCoordinator

PLATFORMS = [
    Platform.SENSOR,
]


async def async_setup_entry(hass: HomeAssistant, entry: E3dcConfigEntry) -> bool:
    coordinator = E3dcCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: E3dcConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
