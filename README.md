# Weishaupt2HA — Home Assistant Integration

Home Assistant Custom Integration fuer **Weishaupt-Heizungen**: Waermepumpen via Modbus TCP sowie Gas-Brennwertkessel via ebusd.

## Supported Hardware

| Series | Transport | Notes |
|--------|-----------|-------|
| **WBB** (heat pump) | Modbus TCP | Requires a working Modbus TCP gateway (WCM-COM or equivalent) on port 502 |
| **WTC** (gas condensing boiler) | ebusd | Requires an eBUS adapter (e.g. Shield C6) and a running [ebusd](https://github.com/john30/ebusd) daemon |

Two transport stacks, one integration. The config flow asks which one you have and only wires up the matching platforms.

## Architecture

The integration is a thin Home Assistant layer on top of the [`weishaupt-modbus`](https://pypi.org/project/weishaupt-modbus/) Python library. The library handles the protocol (Modbus TCP via `pymodbus`, ebusd via plain TCP) and data modelling; the integration maps library data onto HA entities.

## Features

- **Climate** — heating circuit control (HVAC mode, target temperature) [Modbus only]
- **Water heater** — hot water target temperature and boost [Modbus only]
- **Sensors** — 30+ temperatures, energies, COP, operating hours, operating phase, seasons
- **Binary sensors** — compressor, defrost, flame, pump, gas valves, active fault
- **Number** — adjustable setpoints, including v0.6 write-support for seven ebusd user parameters:
  `HcSummerOverTemp`, `HcSummerUnderTemp`, `HcDayTemp`, `HcNightTemp`, `HcFrostTemp`, `HcCurve`, `DhwSetTemp`, `DhwMinTemp`
- **Select** — system operation mode, heating mode, party/pause [Modbus only]
- **Switch** — quiet mode, hot water boost [Modbus only]
- **Button** — hot water one-time boost [Modbus only]
- **Diagnostics** — downloadable debug bundle from the integration settings page

## Installation

### HACS (recommended)

1. Open HACS in Home Assistant
2. **Integrations** → **⋮** → **Custom repositories**
3. Add `https://github.com/maximusIIxII/Weishaupt2HA`, category **Integration**
4. Install **Weishaupt2HA**, restart Home Assistant

### Manual

1. Copy `custom_components/weishaupt2ha/` into your HA `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

1. **Settings** → **Devices & Services** → **Add Integration**
2. Search for **Weishaupt2HA**
3. Pick the connection type:
   - **Modbus TCP** — enter gateway IP, port (default `502`), slave ID (default `1`)
   - **ebusd** — enter daemon IP, port (default `8888`), and an optional circuit prefix
4. Polling interval is adjustable under Options (default 30 s, range 10–300 s)

### ebusd setup

ebusd needs the [J0EK3R Weishaupt config CSVs](https://github.com/J0EK3R/ebusd-configuration-weishaupt) loaded. A working Docker Compose example plus a walkthrough for QNAP Container Station lives under [`examples/ebusd/`](examples/ebusd/).

**Important:** run ebusd **without** the `--scanconfig` flag. The J0EK3R layout is flat (no vendor subfolder); with `--scanconfig`, ebusd fails the scan match, skips the `!include` directives, and `find -w` returns nothing — which silently breaks every v0.6 write target. The example compose file in this repo already has the flag removed.

## Examples

- [`examples/ebusd/`](examples/ebusd/) — Docker Compose setup for ebusd on QNAP (or any Docker host)
- [`examples/lovelace/`](examples/lovelace/) — picture-elements dashboard for the WTC 25-A gas boiler with an animated SVG schema

## Changelog

See [`CHANGELOG.md`](CHANGELOG.md) for the per-version history.

## Credits

- [J0EK3R/ebusd-configuration-weishaupt](https://github.com/J0EK3R/ebusd-configuration-weishaupt) — the ebusd CSVs that describe the WTC message layout
- [OStrama/weishaupt_modbus](https://github.com/OStrama/weishaupt_modbus) — the Modbus register research this integration builds on

## License

MIT
