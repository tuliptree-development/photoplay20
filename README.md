# Photo Play 2.0 on a Spirit 2.1 cabinet

Photo Play 2.0 (PP20NLC2, July 1997) on a Funworld Photo Play Spirit 2.1.
The cabinet has a 6WEV motherboard and an Elo 2500S touchscreen. Photo Play
2004 already runs on it: Elo through `ELODEV`, sound through the C-Media chip.

`build_cabinet_image.py` turns the cracked 2.0 card into an image that brings
up the menu, the touchscreen, and the sound on this cabinet. It does not
remove the dongle check. The cracked image is already without a dongle. The
game EXEs are not modified.

## Sources

- `cracked_IGO2000/PP20NLC2_cf.img`, 2,097,930,240 bytes. The cracked 2.0 card,
  including the Stones files that were put back earlier. This is the input.
- `cracked_IGO2004/PP2004NLC.img`. Only the source of `ELODEV.EXE`,
  `CKUSB.EXE`, `SETAUDIO.COM`, and `C3DMIX.COM`.
- `PP20NLC2.img` is larger than the card. Do not use it.
- Do not overwrite the 2004 card (volume `2218-100A`). Do not overwrite the
  internal disk either.

## What went wrong

### Touch

2.0 expects a MicroTouch screen. The cabinet is an Elo 2500S. It speaks
SmartSet: 9600 8N1, 10-byte packets, first byte `0x55`.

The games do not read the serial port. `MAIN.COM` owns COM3. A game receives
a touch through interrupt `62h` (`CX` = X, `DX` = Y, `BL` = 1 down or 0 up)
and through the words at `0x25A`, `0x25C`, and `0x25E`.

`ELODEV` comes from 2004 and is started before `main.com`:

```
ELODEV 2310,3,9600,3 -C1,4096,4096,1,1,255 -W0 -I65
```

`2310` is the IntelliTouch E281-2310. `-C` is the range, with Y reversed.
`-I65` is the driver interrupt. Mode `0x0E` is stream, untouch, and
coordinates in screen pixels.

`-W50` asked the driver to wait 50 ms before reporting a lift. That wait
depends on the timer interrupt. `MAIN.COM` replaces that interrupt and does
not pass it on. A finger-up therefore never arrived, and the first screen
kept waiting on the touch. `-W0` lets the driver report the lift itself. The
50 ms then lives in `MAIN.COM`: a lift counts only after 5 timer ticks (about
50 ms). A new touch inside that time cancels the lift. Without that pause,
contact bounce turned one touch into a series of touches.

The working program is `MAIN.COM`, md5 `0b7385681f88c946a1ad9b907f6952cc`.
The service button on port `210h` is unchanged (`ba 10 02 ec 24 01` at file
offset `0xC0B`).

### Sound

2.0 looks for an ESS chip at startup. The 6WEV board does not have one. 2004
recognises the board and starts C-Media: USB off, `SETAUDIO` (Sound Blaster
address 220, IRQ 5, DMA 1), then the mixer. The 2.0 WAV files are 8-bit,
mono, 22050 Hz, and use DMA 1. `BLASTER` stays `A220 I5 D1 T4`. The 16-bit
DMA setting `H5` from 2004 does not belong here.

The first attempt turned on the chip startup, `H5`, and a playing list at the
same time, while the opening picture was still on screen. That hung. After
that it was done in steps. First only the chip startup, with the list off.
The menu came back and a game played its own tune. Only then was the
background list turned on.

`HIMEM` was not swapped. The cabinet reaches the menu with `himem486.sys`.

### Background music

The menu program is the same file on the cracked disk and on the original
disk. The difference is `MAIN\PLAY_SND.INI`.

On the cracked disk the list is off, and the ordinary tracks are set to 0
seconds. The menu stays silent, including the screensaver. The number after
the semicolon is how long the track plays, in seconds. It is not a volume.

On the original disk the list is on: `class001.wav` for 60 seconds,
`schwing.wav` for 30 seconds, `tech_1.wav` for 30 seconds, with short effects
in between. From 1 through 31 December the Christmas tracks play, each up to
300 seconds. That list is in the cabinet version.

A tune that starts as soon as a game opens comes from that game
(`STONES\TITLTUNE.WAV`, `HANGMAN\HANGMAN.WAV`, and so on). It does not use
`PLAY_SND.INI`.

### What this version leaves out

The admin calibration screen draws its targets only after the old MicroTouch
controller answers. The Elo chip does not. Attempts to build that answer into
`MAIN.COM` took the menu away: first a timer jump that was missing one byte,
then a black screen as soon as the timer routine or the raw touch mode was
replaced. Calibration is therefore left out. So is the louder button in the
admin screen. `LOUDNESS.INI` is the stored software level; the mixer is set
to maximum at startup.

The one-key patch for the service button belongs only on the 86Box play
image, not on the cabinet.

## Script

```bash
python3 photoplay20/build_cabinet_image.py
```

By default it reads `cracked_IGO2000/PP20NLC2_cf.img` and
`cracked_IGO2004/PP2004NLC.img`, and writes
`cracked_IGO2000/PP20NLC2_cabinet.img`. Both sources are left untouched.

The script:

1. Copies the cracked card.
2. Patches `MAIN.COM`: Elo startup in mode `0x0E`, and the 50 ms pause in the
   timer. The result must be md5 `0b7385681f88c946a1ad9b907f6952cc`.
3. Puts the `ELODEV` line in `AUTOPTS.BAT`, before `main.com`.
4. Replaces `SOUND\SND_INIT.BAT` with CKUSB, SETAUDIO, and the 2004 mixer line.
5. Turns the screensaver list on, with the timings from the original disk.
6. Adds `ELODEV.EXE`, `CKUSB.EXE`, `SETAUDIO.COM`, and `C3DMIX.COM`.

## Onto the card

Only the 2 GB 2.0 card (volume `120D-0B23`). Check `lsblk` first. Never the
internal disk, never the 2004 card.

```bash
sudo bash -c 'umount /dev/sda* 2>/dev/null || true; dd if="PP20NLC2_cabinet.img" of=/dev/sda bs=4M conv=fsync status=progress; sync'
```

Use `/dev/sda` only when that is the 2 GB card.

## 86Box

86Box on this machine has an ESS chip and a MicroTouch mouse. That is enough
to listen to the cracked disk: a silent screensaver, and a tune inside a
game. The cabinet image starts C-Media and Elo. A silent or hung emulator
then says nothing about the cabinet.

The CF image is 63 sectors, 16 heads, 4065 cylinders. The original 2.0 image
is 4092 cylinders and 2,111,864,832 bytes. 86Box with 4092 cylinders truncated
the smaller cabinet image to 14 MB. For the cabinet image, set the cylinders
to 4065, or do not open the image in 86Box.

---

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
