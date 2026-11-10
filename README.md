# Photo Play 2.0 on a Spirit 2.1 cabinet

These notes and this script are for a Funworld Photo Play Spirit 2.1 with a
6WEV motherboard and an Elo 2500S touchscreen. Photo Play 2004 already
supports that board. Photo Play 2.0 (PP20NLC2, July 1997) needs the image
from the script, written to its 2 GB card.

The script builds that image from a Photo Play 2.0 disk. The disk can be
protected or already without its dongle, and the language does not matter
when `MAIN.COM` is the July 1997 program. The script copies four programs
out of a Photo Play 2004 image. It leaves the game programs alone, so a
dongle check that is present stays present.

The disk images themselves are not in this repository. Neither are the four
programs the script copies. Photo Play is by Funworld. `ELODEV.EXE` is Elo's
touch driver. `SETAUDIO.COM` and `C3DMIX.COM` are by C-Media Electronics
(1999). `CKUSB.EXE` is Funworld's 6WEV startup tool from Photo Play 2004.

Those disk images come from the Internet Archive item
[Photoplay Dos CHD collection](https://archive.org/details/photoplay)
(added 22 July 2024). `PP20NL.chd` is the protected Dutch 2.0 disk.
`PP20NLC2.chd` is the same 2.0 games without the dongle check.
`PP2004NLC.chd` holds the Elo and C-Media programs. Extract a CHD with
`chdman extractraw -i PP20NL.chd -o PP20NL.img`. That file is 2,111,864,832
bytes. The script accepts it and writes a 2,097,930,240-byte card image.

## What the finished card does

- The menu appears after the opening picture.
- The Elo touchscreen works in the menu and in the games.
- Each game plays its own tune as soon as it starts.
- The menu stays quiet while you use it. Music starts after the machine has
  been left idle. That is the screensaver list.
- From 1 through 31 December, with the cabinet date in December, the
  screensaver plays the Christmas tracks.
- The service button on port 210h is unchanged.

The admin calibration screen and the louder button are left as they are.
The calibration targets are drawn only after a MicroTouch controller
answers, and this cabinet has an Elo screen. The mixer is set to maximum
when the machine starts.

## What you need

- Python 3 on Windows, Linux, or macOS. The script uses only the Python
  standard library.
- About 2 GB of free disk space for the new image.
- A Photo Play 2.0 disk from July 1997, protected or not. In the
  [Photoplay Dos CHD collection](https://archive.org/details/photoplay),
  `PP20NL.chd` is the protected Dutch disk and `PP20NLC2.chd` is the same
  games without the dongle check. The games, including Stones, already have
  to be on that disk. The script does not add missing game files.
- A Photo Play 2004 image, `PP2004NLC.img`, extracted from `PP2004NLC.chd`
  in the same collection. The script reads four files from it and nothing
  else: `ELODEV.EXE`, `CKUSB.EXE`, `SETAUDIO.COM`, and `C3DMIX.COM`.
- The 2 GB Photo Play 2.0 card. In the write step, pick the disk whose size
  is about 2 GB. The computer's internal disk and a Photo Play 2004 card are
  the wrong targets.

## Step by step

### 1. Download this repository

With Git, from a terminal:

```bash
git clone https://github.com/tuliptree-development/photoplay20.git
```

Without Git, open the repository page, choose Code, then Download ZIP, and
unpack the zip.

### 2. Put the two disk images next to it

When you run the script with no extra arguments, it looks one folder above
itself. This layout matches those defaults:

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

An extracted 2.0 CHD is 2,111,864,832 bytes. The script trims that to the
2 GB card. If the command `python` is missing, use `python3` instead, here
and in the next step.

Images can also stay in any other folder. Pass their full paths in step 3.

### 3. Build the cabinet image

Open a terminal in the `photoplay20` folder.

With the layout from step 2:

```bash
python build_cabinet_image.py
```

With the images somewhere else, one line, and your own paths. Quotes matter
when a path contains spaces:

```bash
python build_cabinet_image.py --input "C:\images\PP20NL.img" --pp2004 "C:\images\PP2004NLC.img" --output "C:\images\PP20NLC2_cabinet.img"
```

On Linux or macOS the same line works. Use the paths on that computer, for
example `--input "$HOME/images/PP20NL.img"`.

The script copies the 2.0 disk, then changes that copy. A larger disk is
trimmed to the 2 GB card. The two source images stay as they were. Wait
until the last lines say `verified` and `wrote ...`. With the default layout
the new file is `cracked_IGO2000/PP20NLC2_cabinet.img`. It is 2,097,930,240
bytes.

The script stops with an error when `MAIN.COM` is not the July 1997 program,
or when `ELODEV.EXE` in the 2004 image is not the expected file.

### 4. Write the image to the card

The new file is a whole-card image. Write it to the card itself, so the card
is replaced. The right card is the one whose size is about 2 GB. The
internal disk of the computer is larger. Unplug a Photo Play 2004 card
before this step. Writing takes a few minutes.

**Linux.** List the disks:

```bash
lsblk -o NAME,SIZE,MODEL,TRAN
```

Find the disk of about 2 GB. Its name might be `sdb`, `sdc`, or another
letter. Use that name wherever the command says `sdX`. Run the command from
the parent folder of step 2, or change the `if=` path to where you saved the
new image:

```bash
sudo umount /dev/sdX* || true
sudo dd if="cracked_IGO2000/PP20NLC2_cabinet.img" of=/dev/sdX bs=4M conv=fsync status=progress
sudo sync
```

`status=progress` shows how many bytes have been written. `sync` stays quiet
until the card has finished.

**macOS.** List the disks with `diskutil list` and find the disk of about
2 GB, for example `disk2`. Use that number wherever the command says `N`:

```bash
diskutil unmountDisk /dev/diskN
sudo dd if="cracked_IGO2000/PP20NLC2_cabinet.img" of=/dev/rdiskN bs=4m
```

**Windows.** Use a program that writes a raw image to a physical disk.
[balenaEtcher](https://etcher.balena.io/) can do it: Flash from file, choose
`PP20NLC2_cabinet.img`, then choose the disk of about 2 GB. Win32 Disk Imager
does the same job: the image file is the source, and the 2 GB removable disk
is the destination. Read the size shown next to the disk before you start.

### 5. Boot the cabinet

Put the card back in the cabinet and switch it on. After the opening picture
you get the menu. Touch should respond. Open a game to hear that game's
tune. Leave the menu alone for a while to hear the screensaver music.

## What the script changes

1. It copies the 2.0 disk to a new file and trims a larger disk to the 2 GB card.
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

Deze notities en dit script zijn voor een Funworld Photo Play Spirit 2.1 met
een 6WEV-moederbord en een Elo 2500S-touchscreen. Photo Play 2004 ondersteunt
dat bord al. Photo Play 2.0 (PP20NLC2, juli 1997) heeft de image uit het
script nodig, geschreven naar de 2 GB-kaart.

Het script maakt die image van een Photo Play 2.0-schijf. De schijf mag
beveiligd zijn of al zonder dongle, en de taal maakt niet uit wanneer
`MAIN.COM` het programma van juli 1997 is. Het script kopieert vier
programma's uit een Photo Play 2004-image. De spelprogramma's blijven staan,
dus een dongle-check die erin zit, blijft erin.

De schijfimages zelf zitten niet in deze repository. De vier programma's die
het script kopieert ook niet. Photo Play is van Funworld. `ELODEV.EXE` is het
touch-stuurprogramma van Elo. `SETAUDIO.COM` en `C3DMIX.COM` zijn van C-Media
Electronics (1999). `CKUSB.EXE` is Funworlds 6WEV-startprogramma uit Photo
Play 2004.

Die schijfimages komen uit het Internet Archive-item
[Photoplay Dos CHD collection](https://archive.org/details/photoplay)
(toegevoegd 22 juli 2024). `PP20NL.chd` is de beveiligde Nederlandse
2.0-schijf. `PP20NLC2.chd` zijn dezelfde 2.0-spellen zonder dongle-check.
`PP2004NLC.chd` bevat de Elo- en C-Media-programma's. Een CHD pak je uit met
`chdman extractraw -i PP20NL.chd -o PP20NL.img`. Dat bestand is 2.111.864.832
bytes. Het script neemt het aan en schrijft een kaartimage van 2.097.930.240
bytes.

## Wat de afgewerkte kaart doet

- Het menu verschijnt na het openingsplaatje.
- Het Elo-touchscreen werkt in het menu en in de spellen.
- Elk spel speelt meteen zijn eigen tune.
- Het menu blijft stil zolang je het gebruikt. Muziek begint nadat de kast
  even met rust is gelaten. Dat is de screensaverlijst.
- Van 1 tot en met 31 december, als de datum van de kast in december valt,
  speelt de screensaver de kerstnummers.
- De serviceknop op poort 210h blijft ongewijzigd.

Het admin-scherm voor calibratie en de luider-knop blijven zoals ze zijn.
De calibratiedoelen verschijnen pas als een MicroTouch-controller antwoordt,
en deze kast heeft een Elo-scherm. De mixer gaat bij het starten op maximaal.

## Wat je nodig hebt

- Python 3 op Windows, Linux of macOS. Het script gebruikt alleen de
  standaardbibliotheek van Python.
- Ongeveer 2 GB vrije schijfruimte voor de nieuwe image.
- Een Photo Play 2.0-schijf van juli 1997, beveiligd of niet. In de
  [Photoplay Dos CHD collection](https://archive.org/details/photoplay)
  is `PP20NL.chd` de beveiligde Nederlandse schijf en `PP20NLC2.chd` dezelfde
  spellen zonder dongle-check. De spellen, inclusief Stones, moeten al op die
  schijf staan. Het script zet ontbrekende spelbestanden niet terug.
- Een Photo Play 2004-image, `PP2004NLC.img`, uitgepakt uit `PP2004NLC.chd`
  in dezelfde verzameling. Het script leest daar vier bestanden uit en verder
  niets: `ELODEV.EXE`, `CKUSB.EXE`, `SETAUDIO.COM` en `C3DMIX.COM`.
- De 2 GB-kaart van Photo Play 2.0. Kies bij het schrijven de schijf van
  ongeveer 2 GB. De interne schijf van de computer en een Photo Play
  2004-kaart zijn de verkeerde doelen.

## Stap voor stap

### 1. Download deze repository

Met Git, vanuit een terminal:

```bash
git clone https://github.com/tuliptree-development/photoplay20.git
```

Zonder Git: open de repositorypagina, kies Code, dan Download ZIP, en pak
de zip uit.

### 2. Zet de twee schijfimages ernaast

Zonder extra argumenten kijkt het script één map boven zichzelf. Deze
indeling hoort bij die standaardpaden:

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

Een uitgepakte 2.0-CHD is 2.111.864.832 bytes. Het script past dat aan tot
de 2 GB-kaart. Bestaat het commando `python` niet, gebruik dan `python3`,
hier en in de volgende stap.

De images mogen ook in een andere map blijven. Geef hun volledige pad mee in
stap 3.

### 3. Maak de kastimage

Open een terminal in de map `photoplay20`.

Met de indeling uit stap 2:

```bash
python build_cabinet_image.py
```

Met de images ergens anders, op één regel, met je eigen paden. Aanhalingstekens
zijn nodig als een pad spaties bevat:

```bash
python build_cabinet_image.py --input "C:\images\PP20NL.img" --pp2004 "C:\images\PP2004NLC.img" --output "C:\images\PP20NLC2_cabinet.img"
```

Op Linux of macOS werkt dezelfde regel. Gebruik de paden van die computer,
bijvoorbeeld `--input "$HOME/images/PP20NL.img"`.

Het script kopieert de 2.0-schijf en past die kopie aan. Een grotere schijf
wordt bijgesneden tot de 2 GB-kaart. De twee bronimages blijven zoals ze
waren. Wacht tot de laatste regels `verified` en `wrote ...` zeggen. Bij de
standaardindeling is het nieuwe bestand `cracked_IGO2000/PP20NLC2_cabinet.img`.
Het is 2.097.930.240 bytes.

Het script stopt met een fout als `MAIN.COM` niet het programma van juli 1997
is, of als `ELODEV.EXE` in de 2004-image niet het verwachte bestand is.

### 4. Schrijf de image naar de kaart

Het nieuwe bestand is een image van de hele kaart. Schrijf het naar de kaart
zelf, zodat de kaart wordt vervangen. De juiste kaart is degene van ongeveer
2 GB. De interne schijf van de computer is groter. Koppel een Photo Play
2004-kaart los voor deze stap. Schrijven duurt een paar minuten.

**Linux.** Toon de schijven:

```bash
lsblk -o NAME,SIZE,MODEL,TRAN
```

Zoek de schijf van ongeveer 2 GB. De naam kan `sdb`, `sdc` of een andere
letter zijn. Gebruik die naam overal waar het commando `sdX` zegt. Voer het
uit vanuit de bovenliggende map van stap 2, of pas het `if=`-pad aan naar de
plek van de nieuwe image:

```bash
sudo umount /dev/sdX* || true
sudo dd if="cracked_IGO2000/PP20NLC2_cabinet.img" of=/dev/sdX bs=4M conv=fsync status=progress
sudo sync
```

`status=progress` toont hoeveel bytes al geschreven zijn. `sync` blijft stil
tot de kaart klaar is.

**macOS.** Toon de schijven met `diskutil list` en zoek de schijf van
ongeveer 2 GB, bijvoorbeeld `disk2`. Gebruik dat nummer overal waar het
commando `N` zegt:

```bash
diskutil unmountDisk /dev/diskN
sudo dd if="cracked_IGO2000/PP20NLC2_cabinet.img" of=/dev/rdiskN bs=4m
```

**Windows.** Gebruik een programma dat een ruwe image naar een fysieke schijf
schrijft. [balenaEtcher](https://etcher.balena.io/) kan dat: Flash from file,
kies `PP20NLC2_cabinet.img`, en kies daarna de schijf van ongeveer 2 GB.
Win32 Disk Imager doet hetzelfde: het imagebestand is de bron, en de
verwijderbare schijf van 2 GB is de bestemming. Lees de grootte naast de
schijf voor je start.

### 5. Start de kast

Zet de kaart terug in de kast en schakel hem in. Na het openingsplaatje
komt het menu. Aanraken moet reageren. Open een spel om de tune van dat
spel te horen. Laat het menu even met rust om de screensavermuziek te horen.

## Wat het script verandert

1. Het kopieert de 2.0-schijf naar een nieuw bestand en snijdt een grotere schijf bij tot de 2 GB-kaart.
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
