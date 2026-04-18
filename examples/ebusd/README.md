# ebusd Deployment für Weishaupt WTC

Anleitung zum Aufsetzen von ebusd in Docker zur Kommunikation mit einer
Weishaupt WTC Gas-Brennwertheizung via eBUS-Adapter (z.B. Shield C6).

## Voraussetzungen

- eBUS-Adapter (Shield C6 o.ä.) am eBUS der Heizung angeschlossen
- Adapter erreichbar im Netz (WLAN/LAN, feste IP empfohlen)
- Docker-Host (NAS, Raspberry Pi, Server) im gleichen Netz

## Setup auf QNAP Container Station

### 1. Konfigurationsdateien holen

Die Weishaupt-CSVs liegen bei J0EK3R im Ordner `weishaupt/` (mit Dateien
wie `08..sc.csv` = System Controller, `35..hc1.csv` = Heizkreis 1 etc.).
`ebusd --scanconfig` lädt die passende CSV anhand der gefundenen eBUS-Adresse.

```bash
ssh admin@<qnap-ip>
cd /share/Container
mkdir -p ebusd/configs ebusd/logs
cd ebusd

git clone https://github.com/J0EK3R/ebusd-configuration-weishaupt.git /tmp/j0ek3r
cp -r /tmp/j0ek3r/weishaupt/* configs/
rm -rf /tmp/j0ek3r

# Kontrolle: es müssen CSV-Dateien im configs/ liegen
ls configs/*.csv
```

### 2. docker-compose.yml anpassen

- `--device=ens:192.168.1.241:9999` → IP und Port des C6 anpassen
- `ens:` = enhanced high-speed (Shield C6 und v5, offizielle Empfehlung)
- Default-Port des C6 ist 9999

### 3. Container starten

Über Container Station → Applications → Create → docker-compose importieren,
oder via SSH:

```bash
docker compose up -d
docker logs -f ebusd
```

### 4. Verbindung prüfen

```bash
# Bus-Signal muss "acquired" sein
docker exec ebusd ebusctl state

# Gefundene Geräte
docker exec ebusd ebusctl find -F name,class,circuit

# Verfügbare Messages eines Circuits listen (z.B. 35..hc1)
docker exec ebusd ebusctl find -c hc1 -F name

# Eine Temperatur lesen (Circuit-Namen aus 'find' verwenden)
docker exec ebusd ebusctl read -c bai FlowTemp
docker exec ebusd ebusctl read -c hc1 RoomTemp
```

## HA-Integration konfigurieren

In Home Assistant:

1. Einstellungen → Integrationen → Weishaupt Heat Pump hinzufügen
2. Verbindungstyp: **ebusd (eBUS Adapter)**
3. Host: IP der QNAP (z.B. `192.168.1.x`)
4. Port: `8888`
5. Circuit: leer lassen (Auto-Detect) oder `wtc` / `bai`

## Troubleshooting

### "signal lost" / kein Signal

- eBUS-Spannung an Heizung messen (sollte 15-24V DC sein)
- C6 LEDs prüfen (RX-Blink = Bus-Traffic)
- Nur EIN Bus-Master darf aktiv sein (WCM-COM vorher abziehen!)

### Keine Messages gefunden

- `ebusctl find` zeigt leere Liste → `--scanconfig` greift nicht
- Manuell scannen: `ebusctl scan`
- Circuit-Namen checken: CSV-Dateien haben einen Namen wie `wtc.*.csv`

### HA-Integration "cannot_connect"

- QNAP-Firewall: Port 8888 eingehend erlauben
- `telnet <qnap-ip> 8888` von HA-Host testen
