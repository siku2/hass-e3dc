# E3/DC Home Assistant Integration

[![GitHub Release](https://img.shields.io/github/release/siku2/hass-e3dc.svg?style=flat-square)](https://github.com/siku2/hass-e3dc/releases)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg?style=flat-square)](https://hacs.xyz/docs/faq/custom_repositories)

[![License](https://img.shields.io/github/license/siku2/hass-e3dc.svg?style=flat-square)](LICENSE)
[![GitHub Activity](https://img.shields.io/github/commit-activity/y/siku2/hass-e3dc.svg?style=flat-square)](https://github.com/siku2/hass-e3dc/commits/main)

Home Assistant integration for the E3/DC S10 devices.

> [!IMPORTANT]
> I created this integration to use the sunspec interface of the E3/DC S10 devices.
> Later I found out about their proprietary "RCSP" protocol, which allows for more control. Please check out the integration here: https://github.com/torbennehmer/hacs-e3dc
>
> This integration works, but I'm not actively using it myself or maintaining it.

## Installation

1. Make sure you have [HACS](https://hacs.xyz) installed.
2. Add this repository as a custom repository to HACS: [![Add Repository](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=siku2&repository=hass-e3dc&category=integration)
3. Use HACS to install the integration.
4. Restart Home Assistant.
5. Set up the integration using the UI: [![Add Integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=e3dc)

## Contributions are welcome

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

### Providing translations for other languages

Modify the files in [custom_components/e3dc/translations/](./custom_components/e3dc/translations/) and open a pull request with the changes.
