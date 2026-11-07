# Photo Play 2.0 op een Spirit 2.1 kast

Photo Play 2.0 (PP20NLC2, juli 1997) op een Funworld Photo Play Spirit 2.1.
De kast heeft een 6WEV-moederbord en een Elo 2500S-touchscreen. Photo Play 2004
draait daar al op: Elo via `ELODEV`, geluid via de C-Media-chip.

Het script `build_cabinet_image.py` maakt van de cracked 2.0-kaart een image
die op deze kast het menu, de touch en het geluid doet. Het haalt de
dongle-check niet weg. De cracked image is al zonder dongle. De spel-EXE's
worden niet aangepast.

## Bronnen

- `cracked_IGO2000/PP20NLC2_cf.img`, 2.097.930.240 bytes. De cracked 2.0-kaart,
  inclusief de eerder teruggezette Stones-bestanden. Dit is de invoer.
- `cracked_IGO2004/PP2004NLC.img`. Alleen de bron van `ELODEV.EXE`, `CKUSB.EXE`,
  `SETAUDIO.COM` en `C3DMIX.COM`.
- `PP20NLC2.img` is groter dan de kaart. Die niet gebruiken.
- De 2004-kaart (volume `2218-100A`) niet overschrijven. De interne schijf ook niet.

## Wat er misging

### Touch

2.0 verwacht een MicroTouch-scherm. De kast is een Elo 2500S. Die spreekt
SmartSet: 9600 8N1, pakketten van 10 bytes, eerste byte `0x55`.

De spellen lezen de seriële poort niet. `MAIN.COM` heeft COM3. Een spel krijgt
een aanraking via interrupt `62h` (`CX` = X, `DX` = Y, `BL` = 1 omlaag of 0
omhoog) en via de woorden op `0x25A`, `0x25C` en `0x25E`.

`ELODEV` komt uit 2004 en wordt gestart vóór `main.com`:

```
ELODEV 2310,3,9600,3 -C1,4096,4096,1,1,255 -W0 -I65
```

`2310` is de IntelliTouch E281-2310. `-C` is het bereik, met Y omgekeerd.
`-I65` is de driver-interrupt. Mode `0x0E` is stream, loslaten, en coördinaten
in schermpixels.

`-W50` vroeg de driver 50 ms te wachten voor hij een loslaten meldt. Die
wachttijd hangt aan de timer-interrupt. `MAIN.COM` vervangt die interrupt en
geeft hem niet door. Een vinger omhoog kwam daardoor nooit aan, en het eerste
scherm bleef op de aanraking wachten. `-W0` laat de driver het loslaten zelf
melden. De 50 ms zit daarna in `MAIN.COM`: een loslaten telt pas na 5 ticks
van de timer (ongeveer 50 ms). Een nieuwe aanraking binnen die tijd schrapt
het loslaten. Zonder die pauze werd één aanraking door de bounce van het
scherm een reeks aanrakingen.

Het werkende programma is `MAIN.COM`, md5 `0b7385681f88c946a1ad9b907f6952cc`.
De serviceknop op poort `210h` is ongewijzigd (`ba 10 02 ec 24 01` op
bestandspositie `0xC0B`).

### Geluid

2.0 zoekt bij het starten een ESS-chip. Die zit niet op de 6WEV. 2004 herkent
het bord en start C-Media: USB uit, `SETAUDIO` (Sound Blaster-adres 220, IRQ 5,
DMA 1), daarna de mixer. De WAV-bestanden van 2.0 zijn 8-bit, mono, 22050 Hz
en gebruiken DMA 1. `BLASTER` blijft `A220 I5 D1 T4`. De 16-bit DMA-instelling
`H5` uit 2004 hoort hier niet bij.

De eerste poging zette chip-start, `H5` en een spelende lijst tegelijk aan,
terwijl het openingsplaatje nog op het scherm stond. Dat bleef hangen. Daarna
is het in stappen gedaan. Eerst alleen de chip-start, met de lijst uit. Het
menu kwam terug en een spel speelde zijn eigen tune. Daarna pas de
achtergrondlijst.

`HIMEM` is niet verwisseld. De kast haalt het menu met `himem486.sys`.

### Achtergrondmuziek

Het menu-programma is op de cracked schijf en op de originele schijf hetzelfde
bestand. Het verschil zit in `MAIN\PLAY_SND.INI`.

Op de cracked schijf staat de lijst uit, en de gewone nummers op 0 seconden.
Het menu blijft dan stil, ook in de screensaver. Het getal achter de puntkomma
is hoelang het nummer speelt, in seconden, geen volume.

Op de originele schijf staat de lijst aan: `class001.wav` 60 seconden,
`schwing.wav` 30 seconden, `tech_1.wav` 30 seconden, met korte effecten
ertussen. Van 1 tot en met 31 december spelen de kerstnummers, elk tot 300
seconden. Die lijst staat in de kastversie.

Een tune die meteen na het openen van een spel klinkt, komt uit dat spel
(`STONES\TITLTUNE.WAV`, `HANGMAN\HANGMAN.WAV`, enzovoort). Die gebruikt
`PLAY_SND.INI` niet.

### Wat niet in deze versie zit

Het admin-scherm voor calibratie tekent zijn doelen pas als de oude
MicroTouch-controller antwoordt. De Elo-chip doet dat niet. Pogingen om dat
antwoord in `MAIN.COM` te bouwen haalden het menu weg: eerst een sprong in de
timer die één byte miste, daarna een zwart scherm zodra de timer-routine of de
ruwe touch-mode werd vervangen. Calibratie is daarom weggelaten. De
luider-knop in het admin-scherm ook. `LOUDNESS.INI` is het bewaarde
softwareniveau; de mixer gaat bij het starten op maximaal.

De één-toets-patch voor de serviceknop hoort alleen bij de 86Box-speelimage,
niet bij de kast.

## Script

```bash
python3 photoplay20/build_cabinet_image.py
```

Standaard leest het `cracked_IGO2000/PP20NLC2_cf.img` en
`cracked_IGO2004/PP2004NLC.img`, en schrijft het
`cracked_IGO2000/PP20NLC2_cabinet.img`. Beide bronnen blijven onaangeroerd.

Het script:

1. Kopieert de cracked kaart.
2. Past `MAIN.COM` aan: Elo-start in mode `0x0E`, en de 50 ms-pauze in de
   timer. Het resultaat moet md5 `0b7385681f88c946a1ad9b907f6952cc` zijn.
3. Zet de `ELODEV`-regel in `AUTOPTS.BAT`, vóór `main.com`.
4. Vervangt `SOUND\SND_INIT.BAT` door CKUSB, SETAUDIO en de 2004-mixerregel.
5. Zet de screensaverlijst aan, met de tijden van de originele schijf.
6. Zet `ELODEV.EXE`, `CKUSB.EXE`, `SETAUDIO.COM` en `C3DMIX.COM` erbij.

## Naar de kaart

Alleen de 2 GB-kaart van 2.0 (volume `120D-0B23`). Eerst `lsblk` kijken.
Nooit de interne schijf, nooit de 2004-kaart.

```bash
sudo bash -c 'umount /dev/sda* 2>/dev/null || true; dd if="PP20NLC2_cabinet.img" of=/dev/sda bs=4M conv=fsync status=progress; sync'
```

`/dev/sda` alleen als dat de 2 GB-kaart is.

## 86Box

86Box op deze machine heeft een ESS-chip en een MicroTouch-muis. Daarmee is de
cracked schijf te beluisteren: stille screensaver, tune in een spel. De
kastimage start C-Media en Elo. Een stille of hangende emulator zegt dan niets
over de kast.

De CF-image is 63 sectoren, 16 koppen, 4065 cilinders. De originele 2.0-image
is 4092 cilinders en 2.111.864.832 bytes. 86Box met 4092 cilinders heeft de
kleinere kastimage ingekort tot 14 MB. Voor de kastimage de cilinders op 4065
zetten, of de image niet in 86Box openen.
