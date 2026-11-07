# Photo Play 2.0 on a Spirit 2.1 cabinet

This is for a Funworld Photo Play Spirit 2.1 with a 6WEV motherboard and an
Elo 2500S touchscreen. Photo Play 2004 already runs on that cabinet. Photo
Play 2.0 (PP20NLC2, July 1997) expects a MicroTouch screen and an ESS sound
chip, so the cracked 2.0 card by itself has no cabinet touch and no cabinet
sound.

The script in this repository builds a 2 GB image that does three things on
this cabinet:

- the menu starts
- the Elo screen answers a touch, and one press stays one press
- games play their own tune, and the menu plays music after the machine has
  been left alone

The calibration screen and the louder button in the service menu stay as they
are on the cracked card. The game programs are left alone. The script does
not remove a dongle check.

This repository is the instructions and the script. It does not contain the
game disks.

## What you need

- A Linux PC with Python 3. The script uses only the Python standard library.
  About 2 GB of free disk space.
- Your cracked Photo Play 2.0 CompactFlash image, file name
  `PP20NLC2_cf.img`, size exactly **2,097,930,240** bytes. That is the image
  that already has the Stones files put back. `MAIN.COM` in that image is
  md5 `e711b369a8ce1f2e1c11ca636bd82935`.
- Your Photo Play 2004 image, file name `PP2004NLC.img`. The script only
  reads four files from it: `TOUCH\ELO\ELODEV.EXE`, `SOUND\6WEV\CKUSB.EXE`,
  `SOUND\CMEDIA\SETAUDIO.COM`, and `SOUND\CMEDIA\C3DMIX.COM`. `ELODEV.EXE`
  must be md5 `b17373ea623f8e77bd05df2896d7b3c5`. The 2004 image used here is
  2,111,864,832 bytes.
- The 2 GB Photo Play 2.0 card, volume `120D-0B23`. Leave the 2004 card
  (volume `2218-100A`) and the PC's internal disk in place.

`PP20NLC2.img` is the larger cracked file, 2,111,864,832 bytes. The script
stops if you give it that file. The cabinet card is the smaller one.

## Step by step

### 1. Download this repository

```bash
mkdir -p ~/photoplay
cd ~/photoplay
git clone https://github.com/tuliptree-development/photoplay20.git
```

### 2. Put the two disk images next to it

The script looks for the images in the folder that contains `photoplay20`.
Create that layout:

```text
photoplay/
  photoplay20/                         this repository
  cracked_IGO2000/PP20NLC2_cf.img      cracked 2.0 card, 2,097,930,240 bytes
  cracked_IGO2004/PP2004NLC.img        2004 image, source of Elo and C-Media
```

Check the 2.0 file before you continue:

```bash
stat -c %s cracked_IGO2000/PP20NLC2_cf.img
```

The number must be `2097930240`.

If your images live somewhere else, you can point at them in step 3. The
output must be a new file. The script refuses to overwrite either input.

### 3. Build the cabinet image

From `~/photoplay`:

```bash
python3 photoplay20/build_cabinet_image.py
```

Or, with your own paths:

```bash
python3 photoplay20/build_cabinet_image.py \
  --cracked /path/to/PP20NLC2_cf.img \
  --pp2004 /path/to/PP2004NLC.img \
  --output /path/to/PP20NLC2_cabinet.img
```

The script copies the cracked card, then:

1. Patches `MAIN.COM` so Elo starts in mode `0x0E`, with a pause of about
   50 ms before a finger-up counts. The patched file must be md5
   `0b7385681f88c946a1ad9b907f6952cc`.
2. Adds the Elo startup line to `AUTOPTS.BAT`, before `main.com`.
3. Replaces `SOUND\SND_INIT.BAT` with the C-Media startup. `BLASTER` stays
   `A220 I5 D1 T4`.
4. Turns the screensaver list on, with the track lengths from the original
   2.0 disk.
5. Copies in `ELODEV.EXE`, `CKUSB.EXE`, `SETAUDIO.COM`, and `C3DMIX.COM`.

A good run ends with these two lines:

```text
verified
wrote .../PP20NLC2_cabinet.img
```

The new file is the same size as the cracked card, 2,097,930,240 bytes. The
two source images are unchanged.

### 4. Write it to the 2.0 card

Look at the disks first:

```bash
lsblk -o NAME,SIZE,MODEL,LABEL,UUID,MOUNTPOINT
```

Write only when the 2 GB device is the Photo Play 2.0 card. On the machine
used for this cabinet that device was `/dev/sda` and the volume id was
`120D-0B23`. Your letter can be different. The internal disk and the 2004
card stay as they are.

```bash
sudo bash -c 'umount /dev/sda* 2>/dev/null || true; dd if="cracked_IGO2000/PP20NLC2_cabinet.img" of=/dev/sda bs=4M conv=fsync status=progress; sync'
```

Change `sda` if `lsblk` shows another name. The copy takes a few minutes.
`status=progress` shows bytes and speed. `sync` sits there with no new line,
then the command returns. That is the end of the write.

### 5. Boot the cabinet

Put the card back in the cabinet and start it. You get the opening picture,
then the menu.

- A touch on the menu and in a game lands where the finger is. A finger-up
  counts after about 50 ms, so the screen bounce does not turn one press
  into several.
- Starting a game plays that game's own tune.
- The menu stays quiet until the machine sits idle. Then the screensaver
  plays `class001.wav` for 60 seconds, `schwing.wav` for 30 seconds, and
  `tech_1.wav` for 30 seconds, with short effects between them.
- From 1 December through 31 December the Christmas tracks play instead, each
  up to 300 seconds. The cabinet date decides which list is used. A dead
  clock battery can land on the December list.

The service button on port `210h` is the original cabinet button.

## What you still see from the cracked card

The service menu can open the calibration page, and that page draws no
targets. The Elo board does not answer the old MicroTouch calibration
commands, and the menu program cannot be changed. Gameplay uses a fixed map
from the glass onto 640×480.

The louder button does not move the mixer. The mixer is set to maximum when
the card starts. `LOUDNESS.INI` is only a stored number.

## If the script stops

| Message | What to do |
| --- | --- |
| cracked image must be the 2,097,930,240-byte CF image | You gave it `PP20NLC2.img` or another dump. Use the CF-sized file. |
| MAIN.COM md5 is …, expected the cracked … | This is a different `MAIN.COM` from the one the patch fits. |
| ELODEV.EXE from the 2004 image is not the expected file | The 2004 image does not contain the Elo driver this cabinet uses. |
| AUTOPTS.BAT does not have the cracked startup | `AUTOPTS.BAT` was already edited. Start again from the untouched cracked card. |
| verified, then wrote | The image is ready to copy to the 2.0 card. |

## Why the cracked card needed this

### Touch

The games never read the serial port. `MAIN.COM` owns COM3 and hands a game
a touch through interrupt `62h`: `CX` is X, `DX` is Y, `BL` is 1 for down and
0 for up. The same point is stored at `0x25A`, `0x25C`, and `0x25E`.

The Elo 2500S speaks SmartSet at 9600 8N1, in 10-byte packets that start
with `0x55`. The driver from the 2004 disk is started before `main.com`:

```text
ELODEV 2310,3,9600,3 -C1,4096,4096,1,1,255 -W0 -I65
```

`2310` is the IntelliTouch E281-2310. `-C` is the glass range, with Y
reversed. `-I65` is the driver interrupt. Mode `0x0E` means a stream of
touches, including the lift, already converted to screen pixels.

`-W50` asked the driver to wait 50 ms before reporting a lift. That wait
uses the PC timer. `MAIN.COM` replaces the timer and does not call the
previous handler, so the lift never arrived and the opening screen waited
forever. `-W0` makes the driver report the lift itself. `MAIN.COM` then
waits 5 timer ticks, about 50 ms, before it accepts the lift. A new touch
during that wait cancels it. Without the wait, screen bounce turned one
press into many.

The working `MAIN.COM` is md5 `0b7385681f88c946a1ad9b907f6952cc`. The service
button bytes at file offset `0xC0B` stay `ba 10 02 ec 24 01`.

### Sound

2.0 looks for an ESS chip. The 6WEV board has a C-Media chip, which is what
2004 starts: `CKUSB.EXE` turns the USB audio path off, `SETAUDIO` sets Sound
Blaster address 220, IRQ 5, DMA 1, and `C3DMIX` sets the mixer. The 2.0 music
files are 8-bit mono at 22050 Hz and use DMA 1. `BLASTER` stays
`A220 I5 D1 T4`. The 16-bit DMA value `H5` from the 2004 startup is left out.

The first music card started the chip, set `H5`, and turned the playlist on
while the opening picture was still showing. The picture stayed on screen.
The working order was chip startup first, with the list off, and the list
only after that card had reached the menu.

The memory manager stays `himem486.sys`. The 2004 `HIMEM` swap and its reboot
program are left out.

### Menu music

`MENU.EXE` is the same file on the cracked disk and on the original disk.
The cracked `MAIN\PLAY_SND.INI` has the list switched off and the tracks set
to 0 seconds, so the menu stays silent. The number after the semicolon is
seconds, the length of the track.

The cabinet image uses the original list: 60, 30, and 30 seconds for the
three main tracks, short effects, and the December Christmas tracks at up to
300 seconds.

A tune that starts with a game comes from that game's own folder, such as
`STONES\TITLTUNE.WAV`. Those files do not use `PLAY_SND.INI`.

### Calibration

Building a fake MicroTouch answer into `MAIN.COM` removed the menu. One
build had a timer jump with a missing byte and froze on the opening picture.
Later builds reached a black screen once the working timer routine, or the
pixel touch mode, was replaced. The working timer is the one in this script.
The calibration page is left as it is.

---

# Photo Play 2.0 op een Spirit 2.1 kast

Dit is voor een Funworld Photo Play Spirit 2.1 met een 6WEV-moederbord en
een Elo 2500S-touchscreen. Photo Play 2004 draait op die kast al. Photo Play
2.0 (PP20NLC2, juli 1997) verwacht een MicroTouch-scherm en een ESS-geluidschip,
dus de cracked 2.0-kaart alleen heeft geen touch en geen geluid van deze kast.

Het script in deze repository bouwt een image van 2 GB die op deze kast drie
dingen doet:

- het menu start
- het Elo-scherm reageert op een aanraking, en één druk blijft één druk
- een spel speelt zijn eigen tune, en het menu speelt muziek nadat de kast
  even met rust is gelaten

Het calibratiescherm en de luider-knop in het servicemenu blijven zoals op de
cracked kaart. De spelprogramma's blijven onaangeroerd. Het script haalt geen
dongle-check weg.

Deze repository is de uitleg en het script. De spelschijven zitten er niet in.

## Wat je nodig hebt

- Een Linux-pc met Python 3. Het script gebruikt alleen de standaardbibliotheek
  van Python. Ongeveer 2 GB vrije schijfruimte.
- Je cracked Photo Play 2.0 CompactFlash-image, bestandsnaam
  `PP20NLC2_cf.img`, grootte precies **2.097.930.240** bytes. Dat is de image
  waarin de Stones-bestanden al zijn teruggezet. `MAIN.COM` in die image is
  md5 `e711b369a8ce1f2e1c11ca636bd82935`.
- Je Photo Play 2004-image, bestandsnaam `PP2004NLC.img`. Het script leest
  daar vier bestanden uit: `TOUCH\ELO\ELODEV.EXE`, `SOUND\6WEV\CKUSB.EXE`,
  `SOUND\CMEDIA\SETAUDIO.COM` en `SOUND\CMEDIA\C3DMIX.COM`. `ELODEV.EXE`
  moet md5 `b17373ea623f8e77bd05df2896d7b3c5` zijn. De 2004-image die hier is
  gebruikt is 2.111.864.832 bytes.
- De 2 GB-kaart van Photo Play 2.0, volume `120D-0B23`. De 2004-kaart
  (volume `2218-100A`) en de interne schijf van de pc blijven zoals ze zijn.

`PP20NLC2.img` is het grotere cracked bestand, 2.111.864.832 bytes. Het script
stopt als je dat bestand geeft. De kastkaart is de kleinere.

## Stap voor stap

### 1. Download deze repository

```bash
mkdir -p ~/photoplay
cd ~/photoplay
git clone https://github.com/tuliptree-development/photoplay20.git
```

### 2. Leg de twee schijfimages ernaast

Het script zoekt de images in de map waarin `photoplay20` staat. Maak deze
indeling:

```text
photoplay/
  photoplay20/                         deze repository
  cracked_IGO2000/PP20NLC2_cf.img      cracked 2.0-kaart, 2.097.930.240 bytes
  cracked_IGO2004/PP2004NLC.img        2004-image, bron van Elo en C-Media
```

Controleer het 2.0-bestand voor je verder gaat:

```bash
stat -c %s cracked_IGO2000/PP20NLC2_cf.img
```

Het getal moet `2097930240` zijn.

Staan de images ergens anders, dan wijs je ze in stap 3 aan. De uitvoer moet
een nieuw bestand zijn. Het script weigert een van de invoerbestanden te
overschrijven.

### 3. Bouw de kastimage

Vanuit `~/photoplay`:

```bash
python3 photoplay20/build_cabinet_image.py
```

Of met je eigen paden:

```bash
python3 photoplay20/build_cabinet_image.py \
  --cracked /pad/naar/PP20NLC2_cf.img \
  --pp2004 /pad/naar/PP2004NLC.img \
  --output /pad/naar/PP20NLC2_cabinet.img
```

Het script kopieert de cracked kaart en doet daarna dit:

1. Past `MAIN.COM` aan zodat Elo start in mode `0x0E`, met een pauze van
   ongeveer 50 ms voor een vinger omhoog telt. Het aangepaste bestand moet
   md5 `0b7385681f88c946a1ad9b907f6952cc` zijn.
2. Zet de Elo-startregel in `AUTOPTS.BAT`, vóór `main.com`.
3. Vervangt `SOUND\SND_INIT.BAT` door de C-Media-start. `BLASTER` blijft
   `A220 I5 D1 T4`.
4. Zet de screensaverlijst aan, met de nummertijden van de originele
   2.0-schijf.
5. Kopieert `ELODEV.EXE`, `CKUSB.EXE`, `SETAUDIO.COM` en `C3DMIX.COM` erbij.

Een goede run eindigt met deze twee regels:

```text
verified
wrote .../PP20NLC2_cabinet.img
```

Het nieuwe bestand is even groot als de cracked kaart, 2.097.930.240 bytes.
De twee bronimages blijven ongewijzigd.

### 4. Schrijf hem naar de 2.0-kaart

Kijk eerst naar de schijven:

```bash
lsblk -o NAME,SIZE,MODEL,LABEL,UUID,MOUNTPOINT
```

Schrijf pas als het 2 GB-apparaat de Photo Play 2.0-kaart is. Op de pc waarmee
deze kast is gemaakt was dat `/dev/sda` en was het volume `120D-0B23`. De
letter kan bij jou anders zijn. De interne schijf en de 2004-kaart blijven
zoals ze zijn.

```bash
sudo bash -c 'umount /dev/sda* 2>/dev/null || true; dd if="cracked_IGO2000/PP20NLC2_cabinet.img" of=/dev/sda bs=4M conv=fsync status=progress; sync'
```

Verander `sda` als `lsblk` een andere naam toont. Het schrijven duurt een
paar minuten. `status=progress` toont bytes en snelheid. `sync` blijft staan
zonder nieuwe regel, en daarna keert het commando terug. Dan is het schrijven
klaar.

### 5. Start de kast

Zet de kaart terug in de kast en start hem. Je krijgt het openingsplaatje,
daarna het menu.

- Een aanraking op het menu en in een spel komt waar de vinger staat. Een
  vinger omhoog telt na ongeveer 50 ms, zodat het stuiteren van het scherm
  van één druk geen reeks drukken maakt.
- Het starten van een spel speelt de tune van dat spel.
- Het menu blijft stil tot de kast even niets doet. Dan speelt de screensaver
  `class001.wav` 60 seconden, `schwing.wav` 30 seconden en `tech_1.wav` 30
  seconden, met korte effecten ertussen.
- Van 1 december tot en met 31 december spelen de kerstnummers, elk tot 300
  seconden. De datum van de kast kiest welke lijst dat is. Een lege
  klokbatterij kan op de decemberlijst uitkomen.

De serviceknop op poort `210h` is de oorspronkelijke kastknop.

## Wat je nog van de cracked kaart houdt

Het servicemenu kan de calibratiepagina openen, en die pagina tekent geen
doelen. Het Elo-bord antwoordt niet op de oude MicroTouch-calibratiecommando's,
en het menuprogramma is niet te wijzigen. Het spelen gebruikt een vaste
indeling van het glas naar 640×480.

De luider-knop verzet de mixer niet. De mixer gaat bij het starten op
maximaal. `LOUDNESS.INI` is alleen een bewaard getal.

## Als het script stopt

| Melding | Wat je doet |
| --- | --- |
| cracked image must be the 2,097,930,240-byte CF image | Je gaf `PP20NLC2.img` of een andere dump. Gebruik het CF-bestand. |
| MAIN.COM md5 is …, expected the cracked … | Dit is een andere `MAIN.COM` dan waar de patch op past. |
| ELODEV.EXE from the 2004 image is not the expected file | De 2004-image bevat de Elo-driver van deze kast niet. |
| AUTOPTS.BAT does not have the cracked startup | `AUTOPTS.BAT` is al eerder bewerkt. Begin opnieuw vanaf de onaangeroerde cracked kaart. |
| verified, daarna wrote | De image is klaar om naar de 2.0-kaart te kopiëren. |

## Waarom de cracked kaart dit nodig had

### Touch

De spellen lezen de seriële poort niet. `MAIN.COM` heeft COM3 en geeft een
spel een aanraking via interrupt `62h`: `CX` is X, `DX` is Y, `BL` is 1 voor
omlaag en 0 voor omhoog. Hetzelfde punt staat op `0x25A`, `0x25C` en `0x25E`.

De Elo 2500S spreekt SmartSet op 9600 8N1, in pakketten van 10 bytes die
beginnen met `0x55`. De driver van de 2004-schijf start vóór `main.com`:

```text
ELODEV 2310,3,9600,3 -C1,4096,4096,1,1,255 -W0 -I65
```

`2310` is de IntelliTouch E281-2310. `-C` is het bereik van het glas, met Y
omgekeerd. `-I65` is de driver-interrupt. Mode `0x0E` is een stroom van
aanrakingen, inclusief het loslaten, al omgerekend naar schermpixels.

`-W50` vroeg de driver 50 ms te wachten voor hij een loslaten meldt. Die
wachttijd gebruikt de pc-timer. `MAIN.COM` vervangt die timer en roept de
vorige handler niet aan, dus het loslaten kwam nooit aan en het
openingsscherm bleef wachten. `-W0` laat de driver het loslaten zelf melden.
`MAIN.COM` wacht daarna 5 timerticks, ongeveer 50 ms, voor hij het loslaten
aanneemt. Een nieuwe aanraking in die wachttijd schrapt hem. Zonder de
wachttijd maakte het stuiteren van het scherm van één druk een reeks.

De werkende `MAIN.COM` is md5 `0b7385681f88c946a1ad9b907f6952cc`. De
serviceknop op bestandspositie `0xC0B` blijft `ba 10 02 ec 24 01`.

### Geluid

2.0 zoekt een ESS-chip. Het 6WEV-bord heeft een C-Media-chip, en dat is wat
2004 start: `CKUSB.EXE` zet het USB-geluidspad uit, `SETAUDIO` zet
Sound Blaster-adres 220, IRQ 5, DMA 1, en `C3DMIX` zet de mixer. De
muziekbestanden van 2.0 zijn 8-bit mono op 22050 Hz en gebruiken DMA 1.
`BLASTER` blijft `A220 I5 D1 T4`. De 16-bit DMA-waarde `H5` uit de
2004-start blijft weg.

De eerste muziekkaart startte de chip, zette `H5` en zette de afspeellijst
aan terwijl het openingsplaatje nog in beeld stond. Het plaatje bleef staan.
De werkende volgorde was eerst de chip starten, met de lijst uit, en de lijst
pas nadat die kaart het menu had gehaald.

De geheugenbeheerder blijft `himem486.sys`. De 2004-verwisseling van `HIMEM`
en het bijbehorende herstartprogramma blijven weg.

### Menumuziek

`MENU.EXE` is hetzelfde bestand op de cracked schijf en op de originele
schijf. De cracked `MAIN\PLAY_SND.INI` heeft de lijst uit en de nummers op
0 seconden, dus het menu blijft stil. Het getal achter de puntkomma is
seconden, de lengte van het nummer.

De kastimage gebruikt de originele lijst: 60, 30 en 30 seconden voor de drie
hoofnummers, korte effecten, en de december-kerstnummers tot 300 seconden.

Een tune die met een spel start komt uit de eigen map van dat spel, zoals
`STONES\TITLTUNE.WAV`. Die bestanden gebruiken `PLAY_SND.INI` niet.

### Calibratie

Een nagemaakt MicroTouch-antwoord in `MAIN.COM` haalde het menu weg. Eén
bouw had een timersprong waar een byte in ontbrak en bleef op het
openingsplaatje staan. Latere bouws kregen een zwart scherm zodra de
werkende timerroutine, of de pixel-touchmode, werd vervangen. De werkende
timer is die in dit script. De calibratiepagina blijft zoals hij is.
