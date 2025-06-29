#!/usr/bin/env bash
set -euo pipefail

HA_VERSION=$(jq -r '.homeassistant' hacs.json)
HA_REQUIREMENTS=(
    "ruff"      # Linting and formatting tool
    "git-cliff" # Changelog generator
    "homeassistant==${HA_VERSION}"
    "colorlog" # HA automatically uses this for colored logging if available
    "zlib-ng"  # Required by aiohttp_fast_zlib
)

mapfile -t MANIFEST_REQUIREMENTS < <(jq -r '.requirements[]' custom_components/*/manifest.json)

REQUIREMENTS=(
    "${HA_REQUIREMENTS[@]}"
    "${MANIFEST_REQUIREMENTS[@]}"
)

echo "Installing requirements: ${REQUIREMENTS[*]}"
pip install --no-cache-dir "${REQUIREMENTS[@]}"
