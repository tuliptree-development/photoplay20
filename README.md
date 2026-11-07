# Photo Play 2.0 on a Spirit 2.1 cabinet

This repository holds the notes and the script for one cabinet: a Funworld
Photo Play Spirit 2.1 with a 6WEV motherboard and an Elo 2500S touchscreen.
Photo Play 2004 already runs on that cabinet. Photo Play 2.0 (PP20NLC2, July
1997) does not, until the image below is written to its 2 GB card.

The script builds that image. It starts from a cracked 2.0 card and copies
four programs out of a Photo Play 2004 image. It leaves the game programs
alone, and it does not remove a dongle check. The cracked 2.0 image is
already without a dongle.

The disk images themselves are not in this repository.

## What the finished card does

- The menu appears after the opening picture.
- The Elo touchscreen works in the menu and in the games.
- Each game plays its own tune as soon as it starts.
- The menu stays quiet while you use it. Music starts after the machine has
  been left idle. That is the screensaver list.
- From 1 through 31 December, with the cabinet date in December, the
  screensaver plays the Christmas tracks.
- The service button on port 210h is the same as on the cracked card.

The admin calibration screen and the louder button are left as they are.
The calibration targets are drawn only after a MicroTouch controller
answers, and this cabinet has an Elo screen. The mixer is set to maximum
when the machine starts.

## What you need

- A Linux computer with Python 3. The script uses only the Python standard
  library.
- About 2 GB of free disk space for the new image.
- The cracked Photo Play 2.0 CF image, file name `PP20NLC2_cf.img`, size
  exactly 2,097,930,240 bytes. Stones is already restored on the image this
  script was written for. The larger file `PP20NLC2.img` (2,111,864,832
  bytes) is a different disk. Leave that file unused.
- A Photo Play 2004 image, file name `PP2004NLC.img`. The script reads four
  files from it and nothing else: `ELODEV.EXE`, `CKUSB.EXE`, `SETAUDIO.COM`,
  and `C3DMIX.COM`.
- The 2 GB Photo Play 2.0 card. On the cabinet used here its volume id is
  `120D-0B23`. Keep the 2004 card (volume `2218-100A`) and the computer's
  internal disk out of the write step.

## Step by step

### 1. Download this repository

```bash
git clone https://github.com/tuliptree-development/photoplay20.git
```

### 2. Put the two disk images next to it

The script looks one folder above itself. This layout matches the defaults:

```text
parent/
  photoplay20/                 this repository
    build_cabinet_image.py
    README.md
  cracked_IGO2000/
    PP20NLC2_cf.img            cracked 2.0 card, 2,097,930,240 bytes
  cracked_IGO2004/
    PP2004NLC.img              Photo Play 2004 image
```

Check the 2.0 file before you continue:

```bash
stat -c %s cracked_IGO2000/PP20NLC2_cf.img
```

The number must be `2097930240`.

If your images live somewhere else, keep them there and pass the paths in
step 3.

### 3. Build the cabinet image

From the `photoplay20` folder:

```bash
python3 build_cabinet_image.py
```

With images in other folders:

```bash
python3 build_cabinet_image.py \
  --cracked /path/to/PP20NLC2_cf.img \
  --pp2004 /path/to/PP2004NLC.img \
  --output /path/to/PP20NLC2_cabinet.img
```

The script copies the cracked card, then changes that copy. The two source
images stay as they were. Wait until the last lines say `verified` and
`wrote ...`. The new file is `cracked_IGO2000/PP20NLC2_cabinet.img`, unless
you chose another `--output`. It is the same size as the cracked card:
2,097,930,240 bytes.

The script stops with an error when the 2.0 image has the wrong size, when
`MAIN.COM` is not the cracked program it expects, or when `ELODEV.EXE` in
the 2004 image is not the expected file.

### 4. See which device the card is

Plug in only the 2 GB 2.0 card, then:

```bash
lsblk -o NAME,SIZE,MODEL,LABEL,UUID,TRAN
```

Use the name whose size is about 2 GB and whose id is `120D-0B23`. On the
computer used here that name was `sda`. A different computer, or a different
USB socket, can show `sdb` or another letter. In the command below, replace
`sdX` with the letter `lsblk` shows for that card. Leave the internal disk
and the 2004 card unplugged or, if they are present, do not use their names.

### 5. Write the image to the card

Run this from the parent folder, so the path to the image is correct.
Replace `sdX` first.

```bash
sudo bash -c 'umount /dev/sdX* 2>/dev/null || true; dd if="cracked_IGO2000/PP20NLC2_cabinet.img" of=/dev/sdX bs=4M conv=fsync status=progress; sync'
```

Writing takes a few minutes. `status=progress` shows how many bytes have
been written. The final `sync` stays quiet until the card has finished.

### 6. Boot the cabinet

Put the card back in the cabinet and switch it on. After the opening picture
you get the menu. Touch should respond. Open a game to hear that game's
tune. Leave the menu alone for a while to hear the screensaver music.

## What the script changes

1. It copies the cracked 2.0 card to a new file.
2. It patches `MAIN.COM` so the Elo driver starts in mode `0x0E`, and so a
   finger-up counts only after about 50 ms. The patched file must have md5
   `0b7385681f88c946a1ad9b907f6952cc`.
3. It adds this line to `AUTOPTS.BAT`, before `main.com`:

   ```text
   ELODEV 2310,3,9600,3 -C1,4096,4096,1,1,255 -W0 -I65
   ```

4. It replaces `SOUND\SND_INIT.BAT` with the C-Media startup from the 2004
   card: `CKUSB`, `SETAUDIO`, `SET BLASTER=A220 I5 D1 T4`, then the mixer at
   maximum. There is no `H5` in that line.
5. It turns the screensaver list on, with the timings from the original
   disk. The number after `;` is seconds, the length of the track.
6. It copies in `ELODEV.EXE`, `CKUSB.EXE`, `SETAUDIO.COM`, and `C3DMIX.COM`.

`HIMEM` stays `himem486.sys`. That is the memory manager the cabinet already
uses to reach the menu.

## Why the cracked card needed this

Photo Play 2.0 expects a MicroTouch screen. The Spirit cabinet has an Elo
2500S. The games never read the serial port themselves. `MAIN.COM` owns COM3
and hands a touch to the game.

The Elo driver can wait 50 ms before it reports a finger-up, but that wait
uses the PC timer. `MAIN.COM` takes that timer over and does not pass it on,
so the finger-up never arrived and the first screen sat there. With `-W0`
the driver reports the lift itself. `MAIN.COM` then waits about 50 ms on its
own timer. Without that short wait, one touch became several touches.

The 2.0 startup looks for an ESS sound chip. The 6WEV board has a C-Media
chip, which is what Photo Play 2004 starts. The 2.0 music files are 8-bit,
mono, 22050 Hz, and they use DMA 1, so the Sound Blaster line stays
`A220 I5 D1 T4`.

The menu program is the same file on the cracked disk and on the original
disk. On the cracked disk `MAIN\PLAY_SND.INI` is off and the tracks are set
to 0 seconds, so the menu stays silent. The cabinet image uses the original
list: `class001.wav` for 60 seconds, `schwing.wav` for 30 seconds,
`tech_1.wav` for 30 seconds, short effects in between, and the Christmas
tracks (up to 300 seconds each) from 1 through 31 December. A tune that
starts with a game comes from that game, for example `STONES\TITLTUNE.WAV`.
That tune does not use the screensaver list.

---

# Photo Play 2.0 op een Spirit 2.1 kast

Deze repository bevat de notities en het script voor één kast: een Funworld
Photo Play Spirit 2.1 met een 6WEV-moederbord en een Elo 2500S-touchscreen.
Photo Play 2004 draait daar al op. Photo Play 2.0 (PP20NLC2, juli 1997) doet
dat pas nadat de image hieronder op de 2 GB-kaart staat.

Het script maakt die image. Het begint bij een cracked 2.0-kaart en kopieert
vier programma's uit een Photo Play 2004-image. De spelprogramma's blijven
staan, en een dongle-check wordt niet weggehaald. De cracked 2.0-image is al
zonder dongle.

De schijfimages zelf zitten niet in deze repository.

## Wat de afgewerkte kaart doet

- Het menu verschijnt na het openingsplaatje.
- Het Elo-touchscreen werkt in het menu en in de spellen.
- Elk spel speelt meteen zijn eigen tune.
- Het menu blijft stil zolang je het gebruikt. Muziek begint nadat de kast
  even met rust is gelaten. Dat is de screensaverlijst.
- Van 1 tot en met 31 december, als de datum van de kast in december valt,
  speelt de screensaver de kerstnummers.
- De serviceknop op poort 210h is dezelfde als op de cracked kaart.

Het admin-scherm voor calibratie en de luider-knop blijven zoals ze zijn.
De calibratiedoelen verschijnen pas als een MicroTouch-controller antwoordt,
en deze kast heeft een Elo-scherm. De mixer gaat bij het starten op maximaal.

## Wat je nodig hebt

- Een Linux-computer met Python 3. Het script gebruikt alleen de standaard-
  bibliotheek van Python.
- Ongeveer 2 GB vrije schijfruimte voor de nieuwe image.
- De cracked Photo Play 2.0 CF-image, bestandsnaam `PP20NLC2_cf.img`, precies
  2.097.930.240 bytes. Stones staat al terug op de image waarvoor dit script
  is geschreven. Het grotere bestand `PP20NLC2.img` (2.111.864.832 bytes) is
  een andere schijf. Laat dat bestand liggen.
- Een Photo Play 2004-image, bestandsnaam `PP2004NLC.img`. Het script leest
  daar vier bestanden uit en verder niets: `ELODEV.EXE`, `CKUSB.EXE`,
  `SETAUDIO.COM` en `C3DMIX.COM`.
- De 2 GB-kaart van Photo Play 2.0. Op de kast hier is het volume-id
  `120D-0B23`. De 2004-kaart (volume `2218-100A`) en de interne schijf van
  de computer blijven buiten de schrijfstap.

## Stap voor stap

### 1. Download deze repository

```bash
git clone https://github.com/tuliptree-development/photoplay20.git
```

### 2. Zet de twee schijfimages ernaast

Het script kijkt één map boven zichzelf. Deze indeling hoort bij de
standaardpaden:

```text
boven/
  photoplay20/                 deze repository
    build_cabinet_image.py
    README.md
  cracked_IGO2000/
    PP20NLC2_cf.img            cracked 2.0-kaart, 2.097.930.240 bytes
  cracked_IGO2004/
    PP2004NLC.img              Photo Play 2004-image
```

Controleer het 2.0-bestand voor je verdergaat:

```bash
stat -c %s cracked_IGO2000/PP20NLC2_cf.img
```

Het getal moet `2097930240` zijn.

Staan de images ergens anders, laat ze daar en geef de paden mee in stap 3.

### 3. Maak de kastimage

Vanuit de map `photoplay20`:

```bash
python3 build_cabinet_image.py
```

Met images in andere mappen:

```bash
python3 build_cabinet_image.py \
  --cracked /pad/naar/PP20NLC2_cf.img \
  --pp2004 /pad/naar/PP2004NLC.img \
  --output /pad/naar/PP20NLC2_cabinet.img
```

Het script kopieert de cracked kaart en past die kopie aan. De twee
bronimages blijven zoals ze waren. Wacht tot de laatste regels `verified`
en `wrote ...` zeggen. Het nieuwe bestand is
`cracked_IGO2000/PP20NLC2_cabinet.img`, tenzij je een ander `--output` koos.
Het is even groot als de cracked kaart: 2.097.930.240 bytes.

Het script stopt met een fout als de 2.0-image de verkeerde grootte heeft,
als `MAIN.COM` niet het cracked programma is dat het verwacht, of als
`ELODEV.EXE` in de 2004-image niet het verwachte bestand is.

### 4. Kijk welk apparaat de kaart is

Sluit alleen de 2 GB-kaart van 2.0 aan, en dan:

```bash
lsblk -o NAME,SIZE,MODEL,LABEL,UUID,TRAN
```

Gebruik de naam waarvan de grootte ongeveer 2 GB is en het id `120D-0B23`.
Op de computer hier was die naam `sda`. Een andere computer, of een andere
USB-aansluiting, kan `sdb` of een andere letter tonen. Vervang in het
commando hieronder `sdX` door de letter die `lsblk` voor die kaart toont.
Laat de interne schijf en de 2004-kaart losgekoppeld, of gebruik hun namen
niet als ze wel aanwezig zijn.

### 5. Schrijf de image naar de kaart

Voer dit uit vanuit de bovenliggende map, zodat het pad naar de image klopt.
Vervang eerst `sdX`.

```bash
sudo bash -c 'umount /dev/sdX* 2>/dev/null || true; dd if="cracked_IGO2000/PP20NLC2_cabinet.img" of=/dev/sdX bs=4M conv=fsync status=progress; sync'
```

Schrijven duurt een paar minuten. `status=progress` toont hoeveel bytes al
geschreven zijn. De laatste `sync` blijft stil tot de kaart klaar is.

### 6. Start de kast

Zet de kaart terug in de kast en schakel hem in. Na het openingsplaatje
komt het menu. Aanraken moet reageren. Open een spel om de tune van dat
spel te horen. Laat het menu even met rust om de screensavermuziek te horen.

## Wat het script verandert

1. Het kopieert de cracked 2.0-kaart naar een nieuw bestand.
2. Het past `MAIN.COM` aan, zodat de Elo-driver in mode `0x0E` start en een
   loslaten pas na ongeveer 50 ms telt. Het aangepaste bestand moet md5
   `0b7385681f88c946a1ad9b907f6952cc` hebben.
3. Het zet deze regel in `AUTOPTS.BAT`, vóór `main.com`:

   ```text
   ELODEV 2310,3,9600,3 -C1,4096,4096,1,1,255 -W0 -I65
   ```

4. Het vervangt `SOUND\SND_INIT.BAT` door de C-Media-start van de 2004-kaart:
   `CKUSB`, `SETAUDIO`, `SET BLASTER=A220 I5 D1 T4`, en daarna de mixer op
   maximaal. In die regel staat geen `H5`.
5. Het zet de screensaverlijst aan, met de tijden van de originele schijf.
   Het getal achter `;` is seconden, de speelduur van het nummer.
6. Het kopieert `ELODEV.EXE`, `CKUSB.EXE`, `SETAUDIO.COM` en `C3DMIX.COM`
   erbij.

`HIMEM` blijft `himem486.sys`. Dat is het geheugenbeheer waarmee de kast het
menu al haalt.

## Waarom de cracked kaart dit nodig had

Photo Play 2.0 verwacht een MicroTouch-scherm. De Spirit-kast heeft een Elo
2500S. De spellen lezen de seriële poort zelf niet. `MAIN.COM` heeft COM3 en
geeft een aanraking aan het spel door.

De Elo-driver kan 50 ms wachten voor hij een loslaten meldt, maar die
wachttijd gebruikt de pc-timer. `MAIN.COM` neemt die timer over en geeft hem
niet door, waardoor het loslaten nooit aankwam en het eerste scherm bleef
wachten. Met `-W0` meldt de driver het loslaten zelf. `MAIN.COM` wacht daarna
ongeveer 50 ms op zijn eigen timer. Zonder die korte pauze werd één
aanraking een reeks aanrakingen.

De 2.0-start zoekt een ESS-geluidschip. Het 6WEV-bord heeft een C-Media-chip,
en die start Photo Play 2004. De muziekbestanden van 2.0 zijn 8-bit, mono,
22050 Hz, en ze gebruiken DMA 1, dus de Sound Blaster-regel blijft
`A220 I5 D1 T4`.

Het menuprogramma is hetzelfde bestand op de cracked schijf en op de
originele schijf. Op de cracked schijf staat `MAIN\PLAY_SND.INI` uit en
staan de nummers op 0 seconden, dus het menu blijft stil. De kastimage
gebruikt de originele lijst: `class001.wav` 60 seconden, `schwing.wav` 30
seconden, `tech_1.wav` 30 seconden, korte effecten ertussen, en de
kerstnummers (elk tot 300 seconden) van 1 tot en met 31 december. Een tune
die met een spel meekomt, komt uit dat spel, bijvoorbeeld
`STONES\TITLTUNE.WAV`. Die tune gebruikt de screensaverlijst niet.
