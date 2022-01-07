# BETA - Solis PV Inverter component for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://hacs.xyz/)
![stability-wip](https://img.shields.io/badge/stability-beta-red.svg?style=for-the-badge&color=red)

![Zonneplan ONE](./images/logo.png)

## Current features
- Sensor for current power
- Sensor for total yield today
- Sensor for total yield overall

## Installation

### Install with HACS (recommended)

Do you have [HACS](https://hacs.xyz/) installed?
1. Add **AwoX** as custom repository.
   1. Go to: `HACS` -> `Integrations` -> Click menu in right top -> Custom repositories
   1. A modal opens
   1. Fill https://github.com/jansaris/solis-pv-inverter in the input in the footer of the modal
   1. Select `integration` in category select box
   1. Click **Add**
1. Search integrations for **Solis PV Inverter**
1. Click `Install`
1. Restart Home Assistant
1. See [Setup](#setup)

### Install manually

1. Install this platform by creating a `custom_components` folder in the same folder as your configuration.yaml, if it doesn't already exist.
2. Create another folder `zonneplan_one` in the `custom_components` folder. Copy all files from `custom_components/solis_pv_inverter` into the `solis_pv_inverter` folder.

## Setup
1. In Home Assitant click on `Configuration`
1. Click on `Integrations`
1. Click on `+ Add integration`
1. Search for and select `Solis PV Inverter`
1. Enter your `hostname` of your inverter
1. Enter your `credentials` of your inverter
1. Click `Save`
1. Enjoy
