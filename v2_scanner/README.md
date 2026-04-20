# Scanner v2 — Binary Checklist

## Dossier

```
C:\Users\[ton_username]\signaux-trading-vs-code\v2_scanner\
```

## Comment lancer

### Option 1 : Double-cliquer (plus simple)
Ouvre le dossier `v2_scanner`, puis **double-cliquez sur `RUN_SCANNER.bat`**

Le scanner démarre automatiquement et scanne toutes les 30 minutes pendant London Open et NY Open.

### Option 2 : Ligne de commande
Ouvre CMD/Terminal, navigue vers le dossier :

```bash
cd C:\Users\[ton_username]\signaux-trading-vs-code\v2_scanner
python scan_auto_v2.py
```

### Option 3 : Un seul scan (test)
```bash
python scan_auto_v2.py once
```

## Ce qu'il fait

6 conditions obligatoires — si une seule échoue, paire rejetée :

1. **Session active** — London Open (7-10 GMT) ou NY Open (13-15 GMT)
2. **Biais H4 clair** — 4 closes du bon côté de l'EMA20 + HH/HL
3. **MSS M15** — break de swing high/low dans direction du biais
4. **FVG frais** — < 40% rempli dans jambe de déplacement
5. **Prix DANS le FVG** — pas "proche", vraiment dedans
6. **SL valide** — 5-20p (majors), 5-25p (exotiques), 5-30p (JPY)

Maximum **2 signaux** par scan, envoyés via Telegram.

## Fichiers dans ce dossier

- `scan_auto_v2.py` — le scanner (ne pas modifier)
- `RUN_SCANNER.bat` — lanceur Windows (double-cliquez)
- `README.md` — ce fichier

## Logs

Les logs s'écrivent dans `scan_auto_v2.log` (même dossier)
