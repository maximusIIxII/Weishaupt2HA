# Weishaupt Home Assistant Integration — Grob- & Feinkonzept

## Inhaltsverzeichnis

1. [Recherche-Ergebnisse](#1-recherche-ergebnisse)
2. [Grobkonzept](#2-grobkonzept)
3. [Feinkonzept](#3-feinkonzept)

---

## 1. Recherche-Ergebnisse

### 1.1 Bestehende Weishaupt-Integration

| Kriterium | Status |
|-----------|--------|
| HA Core (offiziell) | **Nicht vorhanden** |
| HACS Default Store | **Nicht gelistet** |
| Community (HACS custom) | **OStrama/weishaupt_modbus** — 59 Stars, MIT, aktiv gepflegt |
| WEM Portal API | **Keine öffentliche API bekannt** |

**OStrama/weishaupt_modbus** (https://github.com/OStrama/weishaupt_modbus):
- Kommunikation via **Modbus TCP** über das **WCM-COM** Modul (Port 502)
- Plattformen: `sensor`, `number`, `select`, `climate`
- Config Flow vorhanden, aber kein DataUpdateCoordinator
- Keine separate Python-Bibliothek (Modbus-Logik direkt im Integration-Code)
- Kein `quality_scale.yaml`, kein `diagnostics.py`, kein `water_heater`
- Aktuelle Version: v0.0.54 (April 2025)

### 1.2 Best Practices aus vergleichbaren Integrationen

| Integration | Kommunikation | Architektur-Qualität | Besonderheiten |
|-------------|---------------|---------------------|----------------|
| **Wolf ISM7** (Feb 2025) | Lokal, Modbus TCP | ★★★★★ Modernste Referenz | Config Flow, Coordinator, CoordinatorEntity, quality_scale.yaml, separate PyPI-Lib `wolf-ism7` |
| **myVaillant** | Cloud API | ★★★★★ | Umfangreichste Entity-Abdeckung inkl. `calendar`, `water_heater`, `diagnostics.py` |
| **NIBE** | Lokal (Modbus) + Cloud | ★★★★☆ | Dual-Mode (lokal/cloud), Write-then-Refresh Pattern |
| **ViCare** (Viessmann) | Cloud API (OAuth2) | ★★★★☆ | Große Community, separate Lib `PyViCare` |
| **Stiebel Eltron ISG** (HACS) | Lokal, Modbus TCP | ★★★★☆ | Gutes Beispiel für Modbus-basierte WP-Integration |
| **Daikin** | Lokal HTTP | ★★★★☆ | Auto-Discovery via Zeroconf/DHCP |
| **Wolf SmartSet** | Cloud API | ★★☆☆☆ | Nur Sensoren, kein Coordinator |

### 1.3 Identifizierte Best-Practice-Muster (2025)

1. **Config Flow** — UI-basierte Konfiguration ist Pflicht (kein YAML)
2. **DataUpdateCoordinator** — Zentralisiert Datenabfrage, verhindert doppelte API-Calls
3. **CoordinatorEntity** — Basis-Entity-Klasse für automatische Verfügbarkeit und Updates
4. **runtime_data** — Coordinator in `entry.runtime_data` speichern (nicht `hass.data[DOMAIN]`)
5. **Separate Python-Bibliothek** — Protokoll-Kommunikation als eigenes PyPI-Paket
6. **Write-then-Refresh** — Nach Schreibvorgang lokalen Cache aktualisieren + Refresh triggern
7. **quality_scale.yaml** — Mindestens Bronze-Tier anstreben
8. **Entity-Naming** — `_attr_has_entity_name = True` für relative Entity-Namen
9. **Diagnostics** — `diagnostics.py` für Debug-Datenexport
10. **Translations** — `strings.json` für mehrsprachige UI

---

## 2. Grobkonzept

### 2.1 Zielsetzung

Entwicklung einer **Home Assistant Custom Integration** für Weishaupt Wärmepumpen, die:
- Dem aktuellen HA-Architekturstandard (2025) entspricht
- Lokale Kommunikation via **Modbus TCP** über das WCM-COM Modul nutzt
- Alle relevanten Entitäten (Heizkreis, Warmwasser, Sensoren, Einstellungen) abdeckt
- Langfristig als **offizielle HA-Core-Integration** eingereicht werden kann

### 2.2 Architektur-Überblick

```
┌─────────────────────────────────────────────────────────┐
│                    Home Assistant                         │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │         custom_components/weishaupt2ha/             │ │
│  │                                                       │ │
│  │  config_flow.py ──► Coordinator ──► Entity-Plattformen│ │
│  │       │                  │              │              │ │
│  │       │                  │         climate.py         │ │
│  │       │                  │         water_heater.py    │ │
│  │       │                  │         sensor.py          │ │
│  │       │                  │         binary_sensor.py   │ │
│  │       │                  │         number.py          │ │
│  │       │                  │         select.py          │ │
│  │       │                  │         switch.py          │ │
│  │       │                  │         button.py          │ │
│  └──────┼──────────────────┼─────────────────────────┘ │
│          │                  │                             │
│          ▼                  ▼                             │
│  ┌──────────────┐  ┌──────────────────┐                 │
│  │ manifest.json│  │ weishaupt-modbus │ ◄── PyPI Paket  │
│  │ strings.json │  │ (Python Library) │                  │
│  │ icons.json   │  └────────┬─────────┘                 │
│  └──────────────┘           │                            │
│                              │ Modbus TCP (Port 502)     │
└──────────────────────────────┼───────────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │    WCM-COM Modul     │
                    │  (Modbus Gateway)    │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Weishaupt WP/WBB   │
                    │   (Wärmepumpe)       │
                    └─────────────────────┘
```

### 2.3 Kommunikation

| Parameter | Wert |
|-----------|------|
| Protokoll | Modbus TCP |
| Port | 502 (konfigurierbar) |
| Geräteadresse | 1 (konfigurierbar) |
| Gateway | WCM-COM Modul |
| Polling-Intervall | 30 Sekunden (konfigurierbar) |
| IoT-Klasse | `local_polling` |

### 2.4 Unterstützte Entitäten (Übersicht)

| Bereich | Entity-Typ | Beispiele |
|---------|-----------|-----------|
| Heizkreis (HK) | `climate` | Betriebsmodus, Soll-/Ist-Temperatur |
| Warmwasser (WW) | `water_heater` | WW-Modus, Soll-/Ist-Temperatur |
| Mischkreis (MK) | `climate` | MK-Modus, Soll-/Ist-Temperatur |
| Temperaturen | `sensor` | Vorlauf, Rücklauf, Außen, Quelle, Heißgas |
| Energie/Leistung | `sensor` | Stromverbrauch, COP, Wärmemenge |
| Status | `binary_sensor` | Kompressor, Störung, 2. Wärmeerzeuger |
| Sollwerte | `number` | Komfort-/Eco-Temperatur, Heizkurve |
| Betriebsarten | `select` | WP-Modus, WW-Modus |
| Schaltfunktionen | `switch` | Legionellenschutz, Flüstermodus |
| Aktionen | `button` | WW-Einmalpush, Störung quittieren |

### 2.5 Zwei-Paket-Strategie

| Paket | Zweck | Repository |
|-------|-------|------------|
| **weishaupt-modbus** (PyPI) | Modbus-Kommunikation, Register-Map, Datenmodell | Eigenes Repo |
| **weishaupt2ha** (HA Integration) | HA-Plattformen, Config Flow, Coordinator, Entities | Dieses Repo |

Diese Trennung ist **Pflicht für HA-Core-Aufnahme** und ermöglicht unabhängige Tests der Modbus-Schicht.

---

## 3. Feinkonzept

### 3.1 Projektstruktur

```
weishaupt2ha/                          # HA Custom Integration
├── custom_components/
│   └── weishaupt2ha/
│       ├── __init__.py                # Setup, Coordinator-Init, Platform-Forwarding
│       ├── config_flow.py             # UI-Konfiguration (Host, Port, Device-Adresse)
│       ├── const.py                   # DOMAIN, Default-Werte, Register-Adressen
│       ├── coordinator.py             # WeishauptDataUpdateCoordinator
│       ├── entity.py                  # WeishauptEntity (Basis-Klasse)
│       ├── climate.py                 # Heizkreis + Mischkreis
│       ├── water_heater.py            # Warmwasser
│       ├── sensor.py                  # Temperaturen, Energie, COP
│       ├── binary_sensor.py           # Status-Sensoren
│       ├── number.py                  # Sollwerte, Heizkurven-Parameter
│       ├── select.py                  # Betriebsarten
│       ├── switch.py                  # Ein/Aus-Schaltfunktionen
│       ├── button.py                  # Einmalaktionen
│       ├── diagnostics.py             # Debug-Datenexport
│       ├── icons.json                 # Eigene Icons
│       ├── manifest.json              # Metadaten
│       ├── quality_scale.yaml         # Qualitätsstufe
│       ├── strings.json               # Übersetzungen (en + de)
│       └── translations/
│           └── de.json                # Deutsche Übersetzung
├── tests/                             # Pytest-Tests
│   ├── conftest.py
│   ├── test_config_flow.py
│   ├── test_coordinator.py
│   ├── test_climate.py
│   ├── test_sensor.py
│   └── ...
├── hacs.json                          # HACS-Metadaten
├── README.md
├── LICENSE                            # MIT
└── pyproject.toml

weishaupt-modbus/                      # Separate Python Library (PyPI)
├── src/
│   └── weishaupt_modbus/
│       ├── __init__.py
│       ├── client.py                  # ModbusClient (async, pymodbus)
│       ├── registers.py               # Register-Definitionen & Mapping
│       ├── models.py                  # Datenmodelle (dataclasses)
│       ├── const.py                   # Register-Adressen, Enums
│       └── exceptions.py              # Custom Exceptions
├── tests/
├── pyproject.toml
├── README.md
└── LICENSE
```

### 3.2 Kernkomponenten im Detail

#### 3.2.1 `manifest.json`

```json
{
  "domain": "weishaupt2ha",
  "name": "Weishaupt2HA",
  "codeowners": ["@maximusIIxII"],
  "config_flow": true,
  "dependencies": [],
  "documentation": "https://github.com/maximusIIxII/Weishaupt2HA",
  "iot_class": "local_polling",
  "requirements": ["weishaupt-modbus==0.1.0"],
  "version": "0.1.0",
  "integration_type": "device"
}
```

#### 3.2.2 `config_flow.py` — Konfiguration

```
Schritt 1: Verbindungsdaten
  ├── Host (IP-Adresse des WCM-COM)
  ├── Port (Default: 502)
  ├── Device-Adresse (Default: 1)
  └── Polling-Intervall (Default: 30s)

Schritt 2: Verbindungstest
  └── Modbus-Verbindung testen + Geräte-ID auslesen

Schritt 3: Options Flow (nachträgliche Änderungen)
  ├── Polling-Intervall anpassen
  └── Aktivierte Bereiche (HK, WW, MK, Solar) wählen
```

**Validierung:**
- Verbindungstest via `weishaupt-modbus` Library
- Geräte-Identifikation durch Auslesen der Modbus-Register für Gerätetyp/Seriennummer
- Duplicate-Check über eindeutige Geräte-ID

#### 3.2.3 `coordinator.py` — DataUpdateCoordinator

```python
class WeishauptDataUpdateCoordinator(DataUpdateCoordinator[WeishauptData]):
    """Coordinator für Weishaupt Wärmepumpe."""

    def __init__(self, hass, client, update_interval):
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=update_interval)
        self.client = client  # weishaupt_modbus.ModbusClient

    async def _async_update_data(self) -> WeishauptData:
        """Alle Register in einem Batch auslesen."""
        try:
            return await self.client.async_read_all()
        except ConnectionException as err:
            raise UpdateFailed(f"Verbindung verloren: {err}") from err

    async def async_write_register(self, address, value):
        """Register schreiben + sofortiges Refresh."""
        await self.client.async_write_register(address, value)
        await self.async_request_refresh()
```

**Datenmodell (`WeishauptData`):**
```python
@dataclass
class WeishauptData:
    heat_pump: HeatPumpData       # WP-Betriebsdaten
    hot_water: HotWaterData       # Warmwasser-Daten
    heating_circuit: CircuitData  # Heizkreis
    mixing_circuit: CircuitData | None  # Mischkreis (optional)
    solar: SolarData | None       # Solar (optional)
    statistics: StatisticsData    # Energie/COP
    system: SystemData            # Gerätestatus, Fehler
```

#### 3.2.4 `entity.py` — Basis-Entity

```python
class WeishauptEntity(CoordinatorEntity[WeishauptDataUpdateCoordinator]):
    """Basis-Entity für alle Weishaupt-Entitäten."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, description):
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.config_entry.entry_id)},
            name="Weishaupt Wärmepumpe",
            manufacturer="Weishaupt",
            model=self.coordinator.data.system.device_type,
            sw_version=self.coordinator.data.system.firmware_version,
        )
```

#### 3.2.5 Entity-Plattformen

**`climate.py` — Heizkreis/Mischkreis:**
- `hvac_modes`: OFF, HEAT, COOL, AUTO
- `preset_modes`: COMFORT, ECO, AWAY
- `target_temperature` ↔ Modbus-Register
- Mapping: Weishaupt-Modi (Auto, Heizen, Kühlen, Sommer, Standby) → HA HVACMode

**`water_heater.py` — Warmwasser:**
- `operation_list`: OFF, ECO, PERFORMANCE (=Komfort)
- `target_temperature` ↔ WW-Solltemperatur
- `current_temperature` ← WW-Ist-Temperatur
- Legionellenschutz als Feature

**`sensor.py` — Messwerte:**

| Sensor | Unit | Device Class | State Class |
|--------|------|-------------|-------------|
| Vorlauftemperatur | °C | TEMPERATURE | MEASUREMENT |
| Rücklauftemperatur | °C | TEMPERATURE | MEASUREMENT |
| Außentemperatur | °C | TEMPERATURE | MEASUREMENT |
| Quellentemperatur | °C | TEMPERATURE | MEASUREMENT |
| Heißgastemperatur | °C | TEMPERATURE | MEASUREMENT |
| WW-Temperatur | °C | TEMPERATURE | MEASUREMENT |
| Stromverbrauch | W | POWER | MEASUREMENT |
| COP | — | POWER_FACTOR | MEASUREMENT |
| Wärmemenge | kWh | ENERGY | TOTAL_INCREASING |
| Betriebsstunden | h | DURATION | TOTAL_INCREASING |

**`binary_sensor.py` — Status:**
- Kompressor aktiv
- Störung aktiv
- 2. Wärmeerzeuger aktiv
- Abtauung aktiv

**`number.py` — Einstellbare Werte:**
- Komfort-Temperatur (HK/WW)
- Eco-Temperatur (HK/WW)
- Heizkurve Steilheit
- Heizkurve Parallelverschiebung
- Kühlsollwert

**`select.py` — Betriebsarten:**
- WP-Betriebsmodus (Auto / Heizen / Kühlen / Sommer / Standby)
- WW-Betriebsmodus (Auto / Ein / Eco / Aus)
- MK-Betriebsmodus (falls vorhanden)

**`switch.py` — Schaltfunktionen:**
- Legionellenschutz Ein/Aus
- Flüstermodus Ein/Aus

**`button.py` — Einmalaktionen:**
- WW-Einmalpush (sofortige Aufheizung)
- Störung quittieren

#### 3.2.6 `diagnostics.py`

Exportiert anonymisierte Diagnosedaten:
- Alle aktuellen Registerwerte
- Verbindungsstatus
- Gerätetyp und Firmware
- Konfigurationsparameter (IP redacted)

### 3.3 Python Library: `weishaupt-modbus`

#### Verantwortlichkeiten
- Modbus TCP Verbindungsmanagement (basierend auf `pymodbus`)
- Register-Map mit allen bekannten Adressen, Datentypen, Skalierungsfaktoren
- Async Read/Write Operationen
- Datenkonvertierung (Raw-Register → typisierte Python-Objekte)
- Fehlerbehandlung und Retry-Logik

#### Register-Map Struktur
```python
@dataclass
class ModbusRegister:
    address: int
    name: str
    unit: str
    scale: float        # z.B. 0.1 für Temperatur-Register
    register_type: RegisterType  # INPUT oder HOLDING
    data_type: DataType  # INT16, UINT16, INT32
    writable: bool
```

#### Client-Interface
```python
class WeishauptModbusClient:
    async def connect(self) -> None
    async def disconnect(self) -> None
    async def async_read_all(self) -> WeishauptData
    async def async_write_register(self, address: int, value: int) -> None
    async def async_read_register(self, address: int) -> int
    async def async_identify_device(self) -> DeviceInfo
```

### 3.4 Modbus Register-Gruppen (basierend auf WCM-COM Dokumentation)

| Bereich | Register-Bereich | Typ | Zugriff |
|---------|-----------------|-----|---------|
| System/Gerät | 30001–30010 | Input | Lesen |
| WP Betrieb | 30011–30050 | Input | Lesen |
| WP Einstellungen | 40001–40030 | Holding | Lesen/Schreiben |
| Warmwasser Betrieb | 30051–30070 | Input | Lesen |
| Warmwasser Einst. | 40031–40050 | Holding | Lesen/Schreiben |
| Heizkreis Betrieb | 30071–30100 | Input | Lesen |
| Heizkreis Einst. | 40051–40080 | Holding | Lesen/Schreiben |
| Mischkreis | 30101–30130 / 40081–40100 | Input/Holding | Lesen/Schreiben |
| Solar | 30131–30150 | Input | Lesen |
| Statistik/Energie | 30151–30200 | Input | Lesen |

> **Hinweis:** Die exakten Register-Adressen müssen aus der WCM-COM Modbus-Dokumentation oder durch Reverse-Engineering (z.B. aus dem bestehenden OStrama-Projekt) validiert werden.

### 3.5 Implementierungs-Roadmap

#### Phase 1: Foundation (MVP)
- [ ] Python-Library `weishaupt-modbus` erstellen (PyPI)
- [ ] Modbus-Client mit `pymodbus` (async)
- [ ] Register-Map für Kern-Register (WP, WW, HK)
- [ ] HA Integration Grundgerüst: `manifest.json`, `config_flow.py`, `coordinator.py`, `entity.py`
- [ ] `sensor.py` — Alle Temperatursensoren
- [ ] `climate.py` — Heizkreis-Steuerung
- [ ] Grundlegende Tests

#### Phase 2: Vollständige Entity-Abdeckung
- [ ] `water_heater.py` — Warmwasser
- [ ] `number.py` — Sollwerte und Heizkurve
- [ ] `select.py` — Betriebsarten
- [ ] `binary_sensor.py` — Status-Sensoren
- [ ] `switch.py` — Schaltfunktionen
- [ ] `button.py` — Einmalaktionen
- [ ] `diagnostics.py`
- [ ] Erweiterte Tests

#### Phase 3: Polish & Distribution
- [ ] `quality_scale.yaml` (Bronze-Tier)
- [ ] `icons.json` mit eigenen Icons
- [ ] `translations/de.json` — Deutsche Übersetzung
- [ ] HACS-Kompatibilität (`hacs.json`)
- [ ] README mit Installationsanleitung
- [ ] Optionaler Mischkreis- und Solar-Support

#### Phase 4: Core-Submission (optional)
- [ ] Alle HA Quality-Scale-Anforderungen für Silver erfüllen
- [ ] 100% Test-Coverage für kritische Pfade
- [ ] Code-Review durch HA-Community
- [ ] PR an `home-assistant/core` einreichen

### 3.6 Technische Anforderungen

| Anforderung | Wert |
|-------------|------|
| Python | ≥ 3.12 |
| Home Assistant | ≥ 2025.1 |
| Modbus-Library | `pymodbus` ≥ 3.6 |
| Test-Framework | `pytest`, `pytest-homeassistant-custom-component` |
| Code-Style | `ruff` (Linting + Formatting) |
| Type-Checking | `mypy` (strict) |
| CI/CD | GitHub Actions |

### 3.7 Risiken & Mitigationen

| Risiko | Mitigation |
|--------|-----------|
| Unvollständige Register-Dokumentation | OStrama-Projekt als Referenz, Community-Feedback, eigene Hardware-Tests |
| Verschiedene WP-Modelle haben unterschiedliche Register | Geräte-Erkennung via Modbus + modellspezifische Register-Maps |
| WCM-COM Modbus-Verbindung instabil | Reconnect-Logik, Timeout-Handling, Error-Recovery im Coordinator |
| Breaking Changes in HA Core | Regelmäßige Updates, CI mit HA-Nightly |
| Parallele Modbus-Zugriffe (z.B. WEM Portal) | Connection-Pooling, konfigurierbare Polling-Intervalle |

### 3.8 Referenz-Integrationen (Code-Vorbilder)

| Für | Referenz-Integration | Grund |
|-----|---------------------|-------|
| Gesamtarchitektur | **Wolf ISM7** (`wolfism7`) | Neueste Modbus-Heizungs-Integration (Feb 2025), alle Best Practices |
| Entity-Abdeckung | **myVaillant** | Umfangreichste Entity-Typen inkl. `water_heater`, `calendar` |
| Modbus-Kommunikation | **NIBE** (local) | Ausgereiftes Write-then-Refresh Pattern |
| Register-Map Design | **OStrama/weishaupt_modbus** | Bestehende Weishaupt Register-Definitionen als Startpunkt |
| Config Flow | **Daikin** | Gutes Beispiel für lokale Geräte-Konfiguration mit Auto-Discovery |
