# Lovelace — WTC 25-A Schema Card

Ein picture-elements Dashboard fuer den Weishaupt WTC 25-A Gas-Brennwertkessel mit Schema-Ansicht aehnlich einer Waermepumpen-Steuerung, aber passend zu einem Brennwertkessel (Brennkammer, Gasventile, Warmwasserspeicher, Vorlauf/Ruecklauf, Heizkreis, Abgas).

## Dateien

- `wtc25a_schema.svg` — statisches SVG-Schema (Hintergrundgrafik)
- `wtc25a_dashboard.yaml` — Lovelace-YAML mit state-labels/icons ueber das Schema

## Installation

1. **SVG auf den HA-Server kopieren:**
   ```
   <HA-config>/www/wtc25a_schema.svg
   ```
   (erreichbar unter `/local/wtc25a_schema.svg`)

2. **Dashboard-Eintrag hinzufuegen** — entweder einen existierenden View erweitern oder eine neue View anlegen. Den Inhalt von `wtc25a_dashboard.yaml` als Card einfuegen.

3. **Entity-IDs pruefen** — die YAML geht von Default-Entity-Namen aus (`sensor.ebusd_*`, `binary_sensor.ebusd_*`). Wenn deine HA-Installation abweichende IDs hat, anpassen.

## Verwendete Entities

| Entity | Zweck |
|---|---|
| `sensor.ebusd_outdoor_temp` | Aussentemperatur |
| `sensor.ebusd_trend_temp` | Aussentemp-Trend |
| `sensor.ebusd_exhaust_temp` | Abgastemperatur |
| `sensor.ebusd_flow_temp` | Vorlauf Ist |
| `sensor.ebusd_flow_set_temp` | Vorlauf Soll |
| `sensor.ebusd_hot_water_temp` | Speichertemperatur |
| `sensor.ebusd_dhw_set_temp` | DHW-Soll |
| `sensor.ebusd_load_position` | Modulation % |
| `sensor.ebusd_operating_phase` | Betriebsphase |
| `sensor.ebusd_operating_mode` | Betriebsmodus |
| `sensor.ebusd_season` | Saison |
| `sensor.ebusd_hc_status` | Heizkreis-Status |
| `binary_sensor.ebusd_active_fault` | Aktive Stoerung |
| `binary_sensor.ebusd_flame_active` | Flamme an/aus |
| `binary_sensor.ebusd_pump_active` | Umwaelzpumpe an/aus |
| `binary_sensor.ebusd_gas_valve1_active` | Gasventil 1 |
| `binary_sensor.ebusd_gas_valve2_active` | Gasventil 2 |

## Anpassen

- **Positionen:** Jedes Element hat `top`/`left` in Prozent. Feinjustage direkt im YAML.
- **Farben / Schriftgroesse:** pro Element im `style`-Block.
- **Weitere Entities:** fuege `type: state-label` Bloecke hinzu und positioniere sie ueber dem SVG.
- **Write-Setpoints** (Heizkurve, Sommerschwelle, DHW-Soll usw.) lassen sich zusaetzlich als `number`-Entities unten drunter als eigene Card anordnen — dafuer die sieben `number.ebusd_*` Entities nutzen (summer_threshold, room_normal_temp, room_reduced_temp, frost_protection, heating_curve, dhw_setpoint, dhw_min).

## Optik

Modernes Dashboard-Design mit soft neumorphism Cards, animierter Flamme (CSS-loser Pulse direkt im SVG), rotierende Pumpen-Impeller, animierte Flow/Return-Pipes, Wasserwellen im Speicher-Tile. ViewBox 1400x820, skaliert responsive mit.

Die Referenz-Vorlage (typisches Waermepumpen-Schema mit Verdichter/Verdampfer/EEV) passt **nicht 1:1** auf einen Brennwertkessel. Dieses Schema zeigt stattdessen die real vorhandenen Komponenten des WTC 25-A: Brennkammer mit Flamme, zwei Gasventile, Waermetauscher, Umwaelzpumpe, Vorlauf- und Ruecklaufpipes, Warmwasserspeicher, Heizkreis, Abgas.
