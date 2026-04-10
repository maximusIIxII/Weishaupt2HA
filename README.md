# Weishaupt Heat Pump — Home Assistant Integration

Custom Home Assistant integration for **Weishaupt heat pumps** via the **WCM-COM Modbus TCP** interface.

## Features

- **Climate entity** — Control heating circuit (mode, target temperature)
- **Water heater entity** — Control hot water (temperature, boost)
- **30+ sensors** — Temperatures, energy statistics, COP, operating hours
- **Binary sensors** — Compressor, defrost, error/warning status
- **Number entities** — Adjust setpoints, heating curve, summer/winter switch
- **Select entities** — System operation mode, heating mode, party/pause
- **Switch entities** — Quiet mode, hot water boost
- **Button entities** — One-time hot water boost trigger
- **Diagnostics** — Export debug data from the integration settings

## Requirements

- **Weishaupt heat pump** with **WCM-COM** communication module
- WCM-COM connected to your local network (Modbus TCP, default port 502)
- Home Assistant 2025.1 or newer

## Installation

### HACS (recommended)

1. Open HACS in Home Assistant
2. Go to **Integrations** → **⋮** → **Custom repositories**
3. Add this repository URL and select **Integration**
4. Search for "Weishaupt Heat Pump" and install
5. Restart Home Assistant

### Manual

1. Copy the `custom_components/weishaupt_wp` folder to your HA `custom_components/` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services** → **Add Integration**
2. Search for **Weishaupt Heat Pump**
3. Enter the IP address of your WCM-COM module
4. Adjust port (default: 502) and slave ID (default: 1) if needed

### Options

After setup, you can adjust:
- **Polling interval** (default: 30 seconds, range: 10–300s)

## Supported Entities

| Platform | Count | Examples |
|----------|-------|---------|
| Climate | 1 | Heating circuit control |
| Water heater | 1 | Hot water control |
| Sensor | 25+ | Temperatures, energy, humidity, operating hours |
| Binary sensor | 6 | Compressor, defrost, errors, e-heaters |
| Number | 9 | Comfort/normal/reduced temp, heating curve |
| Select | 3 | System mode, heating mode, party/pause |
| Switch | 2 | Quiet mode, hot water boost |
| Button | 1 | Hot water one-time boost |

## Architecture

This integration follows Home Assistant best practices (2025):

- **Config Flow** — UI-based setup with connection validation
- **DataUpdateCoordinator** — Centralized, efficient data fetching
- **CoordinatorEntity** — Base entity with automatic availability
- **runtime_data** — Modern data storage pattern
- **Separate library** — `weishaupt-modbus` PyPI package for Modbus communication
- **Translations** — English and German

## Communication

The integration communicates locally via **Modbus TCP** through the Weishaupt WCM-COM module. No cloud connection required.

```
Home Assistant  ←→  WCM-COM Module (Port 502)  ←→  Weishaupt Heat Pump
```

## Credits

- Register map based on research from [OStrama/weishaupt_modbus](https://github.com/OStrama/weishaupt_modbus)
- Architecture patterns from Wolf ISM7, myVaillant, and NIBE integrations

## License

MIT
