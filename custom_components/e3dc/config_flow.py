import logging
from typing import Any
from urllib.parse import urlparse

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST
from homeassistant.helpers import selector
from homeassistant.helpers.service_info.ssdp import SsdpServiceInfo

from .api import sunspec
from .const import (
    ABORT_ALREADY_CONFIGURED,
    ABORT_DISCOVERY_FAILED,
    CONF_SSDP_UDN,
    DOMAIN,
    ERROR_CANNOT_CONNECT,
    ERROR_NOT_IN_SUNSPEC_MODE,
)

_LOGGER = logging.getLogger(__name__)


class E3dcConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1
    MINOR_VERSION = 1

    _ssdp_info: SsdpServiceInfo | None = None
    _host: str | None = None
    _common: sunspec.Common | None = None

    async def _test_connection(self) -> str | None:
        assert self._host is not None  # noqa: S101

        try:
            e3dc = await sunspec.E3dc.connect(self._host)
            if not await e3dc.is_sunspec():
                _LOGGER.error("Device at %r is not in sunspec mode", self._host)
                return ERROR_NOT_IN_SUNSPEC_MODE

            self._common = await e3dc.read_common()
        except Exception:
            _LOGGER.exception("Test connection to %r failed", self._host)
            return ERROR_CANNOT_CONNECT

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            self._host = user_input[CONF_HOST]
            if err := await self._test_connection():
                errors["base"] = err
            else:
                assert self._common is not None  # noqa: S101
                return self.async_create_entry(
                    title=self._common.options,
                    data={
                        CONF_HOST: self._host,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required(CONF_HOST, default=self._host): selector.TextSelector()}
            ),
            errors=errors,
        )

    async def async_step_ssdp(
        self, discovery_info: SsdpServiceInfo
    ) -> ConfigFlowResult:
        self._ssdp_info = discovery_info
        await self.async_set_unique_id(self._ssdp_info.ssdp_udn)

        assert discovery_info.ssdp_location  # noqa: S101
        self._host = urlparse(discovery_info.ssdp_location).hostname
        self._abort_if_unique_id_configured(
            {CONF_HOST: self._host},
            error=ABORT_ALREADY_CONFIGURED,
        )
        if _err := await self._test_connection():
            return self.async_abort(reason=ABORT_DISCOVERY_FAILED)

        return await self.async_step_discovery_confirm()

    async def async_step_discovery_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        assert self._host is not None  # noqa: S101
        assert self._ssdp_info is not None  # noqa: S101

        if user_input is not None:
            return self.async_create_entry(
                title=self._ssdp_info.upnp["friendlyName"],
                data={
                    CONF_HOST: self._host,
                    CONF_SSDP_UDN: self._ssdp_info.ssdp_udn,
                },
            )

        return self.async_show_form(
            step_id="discovery_confirm",
            data_schema=None,
            description_placeholders={
                "name": str(self._ssdp_info.upnp["friendlyName"]),
                "host": self._host,
            },
        )
