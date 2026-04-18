# weishaupt-modbus

Async Python library for Weishaupt heating systems. Two transports in one package:

- **Modbus TCP** via WCM-COM — for Weishaupt heat pumps (WBB series)
- **ebusd** TCP — for Weishaupt gas boilers (WTC series) via an eBUS adapter and a running [ebusd](https://github.com/john30/ebusd) daemon

The library is used by the [Weishaupt2HA](https://github.com/maximusIIxII/Weishaupt2HA) Home Assistant integration but has no HA dependencies and can be used standalone.

## Install

```bash
pip install weishaupt-modbus
```

Requires Python 3.12+.

## Usage

### Heat pump via Modbus TCP (WCM-COM)

```python
import asyncio
from weishaupt_modbus import WeishauptModbusClient

async def main():
    client = WeishauptModbusClient(host="192.168.1.50", port=502, slave=1)
    await client.connect()
    try:
        data = await client.async_read_all()
        print(data.heat_pump.flow_temp, data.hot_water.temp)
    finally:
        await client.close()

asyncio.run(main())
```

### Gas boiler via ebusd

```python
import asyncio
from weishaupt_modbus import WeishauptEbusdClient

async def main():
    client = WeishauptEbusdClient(host="192.168.1.10", port=8888)
    await client.connect()
    try:
        data = await client.async_read_all()
        print(data.sensors.flow_temp, data.sensors.operating_phase)

        # write a user-level setpoint (e.g. heating curve)
        await client.async_write_field("hc1", "HcCurve", 1.2)
    finally:
        await client.close()

asyncio.run(main())
```

The ebusd client expects a running ebusd daemon loaded with the [J0EK3R Weishaupt configs](https://github.com/J0EK3R/ebusd-configuration-weishaupt). Important: run ebusd **without** `--scanconfig` — otherwise the J0EK3R `!include` directives are not processed and writes fail. See the [Weishaupt2HA docs](https://github.com/maximusIIxII/Weishaupt2HA/tree/main/examples/ebusd) for a Docker compose example.

## Supported writes (ebusd, `hc1.user.inc`)

- `HcSummerOverTemp`, `HcSummerUnderTemp` — summer/winter switch thresholds
- `HcDayTemp`, `HcNightTemp` — normal/reduced room temperature
- `HcFrostTemp` — frost protection setpoint
- `HcCurve` — heating curve slope
- `DhwSetTemp`, `DhwMinTemp` — domestic hot water set/minimum

## Exceptions

- `WeishauptConnectionError` — TCP connection issues
- `WeishauptReadError` — malformed or empty response
- `WeishauptWriteError` — ebusd rejected the write (`ERR:` response)
- `WeishauptModbusError` — base class for all of the above

## License

MIT
