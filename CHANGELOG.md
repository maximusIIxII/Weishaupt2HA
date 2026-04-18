# Changelog

Alle nennenswerten Aenderungen an der HA-Integration **Weishaupt2HA** und der Python-Library **weishaupt-modbus** sind hier dokumentiert.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versionierung: [Semantic Versioning](https://semver.org/).

Die HA-Integration (`custom_components/weishaupt2ha/`) und die Library (`weishaupt_modbus/`) versionieren unabhaengig. Eintraege hier beziehen sich auf die HA-Integration; Library-Bumps sind explizit markiert.

---

## [1.0.0] — 2026-04-18

### Breaking
- DOMAIN umbenannt: `weishaupt_wp` → `weishaupt2ha`. Bestehende HA-Installationen muessen die Integration einmal entfernen und neu hinzufuegen. Alte `sensor.weishaupt_wp_*` Entity-IDs werden verwaist; Automationen und Dashboards muessen ggf. migriert werden. Die `sensor.ebusd_*` / `binary_sensor.ebusd_*` Naming ist DOMAIN-unabhaengig und bleibt stabil.

### Changed
- Ordner `custom_components/weishaupt_wp/` → `custom_components/weishaupt2ha/`.
- Display-Namen ueberall auf **"Weishaupt2HA"**: `manifest.json`, `hacs.json`, `strings.json`, `translations/de.json`.
- `README.md` komplett neu geschrieben — dokumentiert den aktuellen Two-Transport-Stand (Modbus TCP fuer Waermepumpen + ebusd fuer Brennwertkessel), inkl. der `--scanconfig`-Warnung fuer ebusd.
- `manifest.json` repository-URL auf `maximusIIxII/Weishaupt2HA` korrigiert; neues Feld `issue_tracker`.

### Added
- [`examples/lovelace/`](examples/lovelace) — picture-elements Dashboard fuer WTC 25-A Brennwertkessel mit modernem SVG-Schema (animierte Flamme, rotierende Pumpe, Flow/Return-Pipes) und 18 gemappten Entities.

### Unchanged
- Python-Library `weishaupt-modbus` bleibt bei **0.6.0** auf PyPI. Keine API-Aenderungen.
- Alle Write-Features aus v0.6.0 (sieben User-Setpoints ueber ebusd) bleiben bestehen.

---

## [0.6.0] — 2026-04-18

### Added (HA + Library)
- **Schreibzugriff** auf sieben User-Level-Parameter der Heizung ueber ebusd als Number-Entities:
  - `number.ebusd_summer_threshold` (5–30 °C)
  - `number.ebusd_room_normal_temp` (10–25 °C)
  - `number.ebusd_room_reduced_temp` (10–25 °C)
  - `number.ebusd_frost_protection` (0–10 °C)
  - `number.ebusd_heating_curve` (0–4 in 0.05-Schritten)
  - `number.ebusd_dhw_setpoint` (30–65 °C)
  - `number.ebusd_dhw_min` (20–50 °C)
- Library: `WeishauptEbusdClient.async_write_field(circuit, message, value)`.

### Fixed
- Voraussetzung fuer Write-Support: ebusd muss **ohne `--scanconfig`** laufen. J0EK3R's CSVs sind flat-layout; mit `--scanconfig` werden alle `!include`-Direktiven ignoriert und `ebusctl find -w` liefert `ERR: element not found`. In README, examples/ebusd/ und KONZEPT dokumentiert.

### Library Bump
- `weishaupt-modbus` **0.4.0 → 0.6.0** (0.5.x wurde nur auf Integrationsseite vergeben).

---

## [0.5.2] — 2026-04-18

### Fixed
- ebusd multi-line response buffer leak: `_send_command` hat nur eine Zeile gelesen, waehrend ebusd jede Telnet-Antwort mit einer Leerzeile terminiert. Beim Startup-Call `ebusctl info` (10+ Zeilen Output) blieben alle nachfolgenden Zeilen im Socket-Buffer und wurden beim naechsten `read -c hc1 Set` als Broadcast-Response missinterpretiert. Symptom: `sensor.ebusd_hc_status = "max symbol rate: 64"` oder andere offensichtlich falsche Werte.

---

## [0.5.1] — 2026-04-18

### Added
- `binary_sensor.ebusd_active_fault` (`device_class=PROBLEM`, enabled by default). Erkennt Fehler- und Warnzustaende ueber Prefix-Match (`S:`, `W:`, `W/S:`) am `operating_phase`-Feld in `sc.Act`. Robust gegen neue Weishaupt-Codes.

### Won't fix
- `ErrorHistory`-Message ueber ebusd. Auf dem WTC 25-A gibt es fuer `sc` nur **eine** Message — `Act`. Die interne Historie liegt nur im Service-Menu des Geraets. Der neue `active_fault`-Sensor + HA-History decken den Use-Case ab.

---

## [0.5.0] — 2026-04-18

### Removed (Breaking für WCM-COM-HTTP-Nutzer)
- WCM-COM HTTP/coco-Transport komplett entfernt (Hardware war defekt — Bus-Spannung fiel von 20V auf 3.9V, Modul wurde entsorgt und durch direkten eBUS-Adapter + ebusd ersetzt). Uebrig bleiben die Verbindungstypen **Modbus TCP** (Waermepumpe) und **ebusd** (Gas-Brennwert).
- Library: `wcm_client.py`, `wcm_const.py`, `wcm_models.py` (~479 Zeilen). Dependency `httpx` entfernt.
- HA-Integration: WCM-HTTP-Option aus Config-Flow, alle `WCM_*_SENSORS`, `CONF_USERNAME/PASSWORD`, `DEFAULT_HTTP_PORT`, Translations fuer `wcm_*`.

### Unchanged
- WCM-COM **Modbus TCP** (Gateway-Pfad fuer Waermepumpen) bleibt — das ist der primaere Transport fuer WBB-Serie.

---

## [0.4.1] — 2026-04-18

### Added
- `sensor.ebusd_diagnostics` (`entity_category=diagnostic`, default disabled). State = Anzahl geparster Felder; `extra_state_attributes` enthaelt das komplette `raw_values`-Dict.
- End-to-End-Tests fuer `async_read_all` mit echtem `asyncio.StreamReader`: Happy-Path, Teil-Ausfall, Voll-Ausfall. **59/59 Tests gruen.**

### Fixed
- Off-by-one in `ebusd_const.py`: sc.Act hat 26 Felder, nicht 27 (bestaetigt gegen [J0EK3R `f6..sc.csv`](https://github.com/J0EK3R/ebusd-configuration-weishaupt/blob/master/weishaupt/f6..sc.csv)).

---

## Aeltere Versionen

Vor v0.4.1 siehe [Git-Tags](https://github.com/maximusIIxII/Weishaupt2HA/tags) und [GitHub-Releases](https://github.com/maximusIIxII/Weishaupt2HA/releases).

[1.0.0]: https://github.com/maximusIIxII/Weishaupt2HA/releases/tag/v1.0.0
[0.6.0]: https://github.com/maximusIIxII/Weishaupt2HA/releases/tag/v0.6.0
[0.5.2]: https://github.com/maximusIIxII/Weishaupt2HA/releases/tag/v0.5.2
[0.5.1]: https://github.com/maximusIIxII/Weishaupt2HA/releases/tag/v0.5.1
[0.5.0]: https://github.com/maximusIIxII/Weishaupt2HA/releases/tag/v0.5.0
[0.4.1]: https://github.com/maximusIIxII/Weishaupt2HA/releases/tag/v0.4.1
