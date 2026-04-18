# PyPI-Upload: weishaupt-modbus

Anleitung fuer das Veroeffentlichen einer neuen Version der Library auf PyPI.
HA-User beziehen die Library dann automatisch ueber die `requirements`-Zeile in
`custom_components/weishaupt2ha/manifest.json`.

## Einmalige Vorbereitung

### 1. Tools installieren

```bash
pip install --upgrade build twine
```

- `build` erzeugt die Distribution-Artefakte (wheel + sdist) aus `pyproject.toml`
- `twine` laedt sie sicher zu PyPI hoch (nutzt HTTPS + API-Token statt User/Passwort)

### 2. PyPI-Accounts anlegen

Zwei Accounts empfohlen:

- **Test-PyPI**: https://test.pypi.org/account/register/ (zum Probeladen, aendert nichts an Production)
- **Production-PyPI**: https://pypi.org/account/register/ (der echte Upload)

2FA fuer beide aktivieren.

### 3. API-Tokens erzeugen

Auf beiden Plattformen je einen API-Token erstellen:

- Production: https://pypi.org/manage/account/token/
- Test: https://test.pypi.org/manage/account/token/

Beim ersten Upload: Scope "Entire account" waehlen (weil das Projekt `weishaupt-modbus`
vorher noch nicht existiert auf deinem Account — der Scope kann erst nach dem Upload
auf das einzelne Projekt eingeschraenkt werden).

**Wichtig:** Der Token wird nur einmal angezeigt. Sofort kopieren. Format ist
`pypi-AgEIcHlwaS5vcmcC...` (langer Base64-String).

Nach dem ersten erfolgreichen Upload: Token loeschen, einen projekt-gebundenen Token
mit Scope nur auf `weishaupt-modbus` neu erstellen und `~/.pypirc` aktualisieren.

### 4. Token speichern

Datei `~/.pypirc` anlegen (Windows: `C:\Users\<User>\.pypirc`):

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmcC...     # Production-Token

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-AgENdGVzdC5weXBpLm9yZ...  # Test-PyPI-Token
```

Rechte einschraenken (optional aber empfohlen):
```bash
chmod 600 ~/.pypirc
```

Alternative ohne `.pypirc`: Token jedes Mal interaktiv eingeben, wenn twine danach fragt.
User ist immer `__token__`, Passwort ist der komplette Token-String inkl. Prefix `pypi-`.

## Fuer jeden Release

### 1. Version bumpen

Vor dem Upload beide Versionsangaben pruefen:

- `weishaupt_modbus/pyproject.toml` → Feld `version`
- `custom_components/weishaupt2ha/manifest.json` → Feld `version` UND `requirements`

Beide muessen auf die gleiche neue Version zeigen. Die HA-Integration pinnt die
Library per `weishaupt-modbus==X.Y.Z`, sonst laufen HA und Library auseinander.

### 2. Git-Tag setzen und pushen

```bash
cd C:/dev/Weishaupt
git tag v0.4.0
git push origin v0.4.0
```

### 3. Alte Build-Artefakte entfernen

PyPI erlaubt kein Re-Upload unter gleichem Dateinamen. Vorher sauber aufraeumen:

```bash
rm -rf weishaupt_modbus/dist/ weishaupt_modbus/build/ weishaupt_modbus/*.egg-info
```

### 4. Paket bauen

```bash
cd weishaupt_modbus
python -m build
```

Das erzeugt im Ordner `dist/`:
- `weishaupt_modbus-0.4.0-py3-none-any.whl` (wheel, bevorzugt bei pip install)
- `weishaupt_modbus-0.4.0.tar.gz` (source distribution, fallback)

Pruefe kurz dass beide Dateien existieren und die erwartete Versionsnummer tragen:

```bash
ls dist/
```

### 5. Optional: erst zu Test-PyPI hochladen

```bash
twine upload --repository testpypi dist/*
```

Dann aus einer frischen venv probeweise installieren:

```bash
python -m venv /tmp/testvenv
source /tmp/testvenv/bin/activate   # Windows: /tmp/testvenv/Scripts/activate
pip install --index-url https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple/ \
            weishaupt-modbus==0.4.0
python -c "from weishaupt_modbus import EbusdData; print('OK')"
deactivate
```

Der `--extra-index-url` holt Dependencies wie `pymodbus` und `httpx` aus dem
echten PyPI, da Test-PyPI nur ein Teil-Mirror ist.

### 6. Zu Production-PyPI hochladen

```bash
twine upload dist/*
```

twine liest die Credentials aus `~/.pypirc` (Abschnitt `[pypi]`), falls konfiguriert.
Sonst fragt es nach Username/Passwort — `__token__` / Token-String eingeben.

### 7. Verifizieren

```bash
pip index versions weishaupt-modbus
```

oder im Browser: https://pypi.org/project/weishaupt-modbus/

Neue Version sollte innerhalb weniger Sekunden sichtbar sein.

## Troubleshooting

**`400 Bad Request: File already exists`**
PyPI erlaubt keine Re-Uploads unter dem gleichen Versionsstring. Wenn die Version
schon hochgeladen wurde: bumpen auf die naechste Patch-Version (0.4.0 → 0.4.1).
Loeschen geht in der PyPI-Weboberflaeche nur manuell und auch nur innerhalb
bestimmter Zeitfenster.

**`403 Invalid or non-existent authentication information`**
- Token falsch kopiert (muss mit `pypi-` beginnen, kompletter Base64-String)
- Username ist nicht dein Login-Name, sondern woertlich `__token__`
- Token wurde auf der falschen Plattform erstellt (Test vs. Production)

**`HTTPError: 403 ... You are not allowed to edit 'weishaupt-modbus'`**
Token-Scope deckt das Projekt nicht ab. Neuen Token mit Scope "Entire account"
oder mit dem richtigen Projekt-Scope erstellen.

**`long_description` Warnungen beim Build**
`pyproject.toml` referenziert `README.md` ueber `readme = "README.md"`. Wenn die
README fehlt, macht twine keine Rendering-Vorschau — ist aber nicht blockierend.

**HA Integration findet die neue Version nicht**
PyPI-Mirrors brauchen manchmal bis zu 5 Minuten bis die neue Version ueberall
gecacht ist. HA-Core-Installation nach dem Upload kurz warten und nochmal triggern,
oder `pip install --upgrade weishaupt-modbus` im HA-Container laufen lassen.

## Checkliste fuer v0.4.0 → v0.5.0 (naechstes Mal)

- [ ] Version bumpen in `pyproject.toml` und `manifest.json` (inkl. `requirements`)
- [ ] Commit + Push
- [ ] Git-Tag setzen und pushen (`git tag vX.Y.Z && git push origin vX.Y.Z`)
- [ ] `dist/`, `build/`, `*.egg-info` loeschen
- [ ] `python -m build`
- [ ] Optional: `twine upload --repository testpypi dist/*` + Install-Test
- [ ] `twine upload dist/*`
- [ ] GitHub-Release erstellen (ueber `gh release create` oder im Web)
- [ ] PyPI-Seite kurz checken: https://pypi.org/project/weishaupt-modbus/
