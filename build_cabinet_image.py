#!/usr/bin/env python3
"""Build a Photo Play 2.0 image for a Spirit 2.1 cabinet.

The input is a July 1997 Photo Play 2.0 disk: any language, with or without
the dongle. The script copies ELODEV, CKUSB, SETAUDIO and C3DMIX out of a
Photo Play 2004 image, starts those drivers, and patches MAIN.COM so the Elo
screen and the C-Media chip work. It does not modify the inputs, does not
remove a dongle, and does not change the service button.

The written file is the 2 GB card size. A larger disk image is trimmed to
that size when its files fit.
"""

import argparse
import hashlib
import struct
import sys
from pathlib import Path

ORIG_MAIN = "e711b369a8ce1f2e1c11ca636bd82935"
GOOD_MAIN = "0b7385681f88c946a1ad9b907f6952cc"
ELODEV_MD5 = "b17373ea623f8e77bd05df2896d7b3c5"
SERVICE = bytes.fromhex("ba1002ec2401")

# File offsets in MAIN.COM. The program is a DOS COM image, so IP = offset + 0x100.
POLL = bytes.fromhex(
    "601e068cc88ed8803e3e12007474b80800cd6509c0744109d2752881fb7f027603"
    "bb7f0281f9df017603b9df01891e930a890e950ac606980a00c606970a01b301eb29"
    "803e970a007438803e980a007531c606980a05eb2a803e980a007423fe0e980a751d"
    "c606970a00b3008b0e930a8b16950a890e5a0289165c02881e5e02cd62071f6166bb"
    "0a00000066011e8b02e90301000000000000"
)
TIMER_JUMP = bytes.fromhex("e96cfe9090")
ELO_INIT = bytes.fromhex(
    "515256571e06fc8cc88ed831c08ec026c43e94018cc88ed883c702be6411b90600f3"
    "a6751fb80100cd65b80500bb0e00cd65b80f00bb6a11cd65b80300cd65c6063e1201"
    "071f5f5e5a595b58c3454c4f44455600007f020000df010000ff00"
    + "90" * 200
    + "00"
)
assert len(POLL) == 153 and len(TIMER_JUMP) == 5 and len(ELO_INIT) == 296

# Bytes MAIN.COM must contain before the touch patch. A matching file is the
# July 1997 program, whichever language or dongle the rest of the disk uses.
OLD_POLL = bytes.fromhex(
    "505351521e8ccb8edbbaea03ec24010f85c700baed03ec24010f84bd00bae803ec"
    "803e6b020074133c0d745f803e6b02087245c6066b0200e99f003c1c740f3c19740b"
    "3c1874173c017403e98c00bb6c028807c6066b0201a06b02eb7d90c6065e0200c606"
    "6b02008b0e5a028b165c028a1e5e02cd62eb62bb6c028a166b0232f603da8807fe06"
    "6b02eb4fbb6c028a166b0232f603da8807fe"
)
OLD_TIMER = bytes.fromhex("66011e8b02")
OLD_ELO = bytes.fromhex(
    "521ebaeb03b080eebae803b00ceebae903b000eebaec03b00beebaeb03b006eeb001"
    "e848f8b052e843f8b00de83ef8e8a4f9e8a1f9e89ef9e89bf9b001e82df8b041e828"
    "f8b044e823f8b00de81ef8e884f9b001e816f8b050e811f8b04ee80cf8b038e807f8"
    "b031e802f8b00de8fdf7e863f9baeb03b003eee83901a08109b435cd218c064c0289"
    "1e4e02a08109ba000ab425cd21b001bae903eefae4a18ae0e421a34a0223068209e6"
    "218ac4e6a1fbb001e8b8f7b052e8b3f7b00de8aef7e814f9e811f9e80ef9e80bf9b0"
    "01e89df7b041e898f7b044e893f7b00de88ef7e8f4f8b001e886f7b046e881f7b048"
    "e87cf7b00de877f7e8ddf8b001e86ff7b04de86af7b054e865f7b00de860f7e8c6f8"
    "b001e858f7b050e853f7b04ce84ef7b00de849f7c6065902"
)
assert len(OLD_POLL) == 153 and len(OLD_TIMER) == 5 and len(OLD_ELO) == 296

CARD_BYTES = 2097930240
PART_LBA = 63
PART_SECTORS = CARD_BYTES // 512 - PART_LBA

# Files the cracked 2.0 disk lost from Stones. Sizes are the protected disk.
# The bytes themselves stay on the user's disk.
STONES_FILES = (
    ("GFX", "WOOW", "PCX", 1594),
    ("GFX", "YEAHH", "PCX", 1526),
    ("GFX", "ZAHLEN", "PCX", 1944),
    ("ROUNDS", "BONUS", "DTA", 305),
    ("ROUNDS", "LEVEL1", "DTA", 374),
    ("ROUNDS", "LEVEL2", "DTA", 407),
    ("ROUNDS", "LEVEL3", "DTA", 459),
    ("ROUNDS", "LEVEL4", "DTA", 270),
    ("ROUNDS", "LEVEL5", "DTA", 358),
    ("SFX", "05SND030", "WAV", 11156),
    ("SFX", "05SND054", "WAV", 69788),
    ("SFX", "06SND034", "WAV", 59876),
    ("SFX", "BUTTON", "WAV", 12114),
    ("SFX", "CLICK21", "WAV", 808),
    ("SFX", "COMEON1", "WAV", 8444),
    ("SFX", "DIRTLAUG", "WAV", 25900),
    ("SFX", "FALSCH", "WAV", 19444),
    ("SFX", "GAMEOVER", "WAV", 129696),
    ("SFX", "GETBONUS", "WAV", 6426),
    ("SFX", "GOVER", "WAV", 33698),
    ("SFX", "HISCORE", "WAV", 41514),
    ("SFX", "NEXTRND", "WAV", 143354),
    ("SFX", "ROUND", "WAV", 60284),
    ("SFX", "SCRATCH", "WAV", 1610),
    ("SFX", "TIMESE20", "WAV", 40020),
    ("SFX", "TIMEUP", "WAV", 13354),
    ("SFX", "TOUCHST", "WAV", 9292),
    ("SFX", "UNMARK", "WAV", 7608),
    ("SFX", "WELLCOME", "WAV", 13532),
    ("SFX", "WRONG", "WAV", 10380),
)

ELO_LINE = (
    b"\\touch\\elo\\ELODEV 2310,3,9600,3 -C1,4096,4096,1,1,255 -W0 -I65\r\n"
)
SND_INIT = (
    b"@ECHO OFF\r\n"
    b"\\SOUND\\6WEV\\CKUSB.EXE\r\n"
    b"\\SOUND\\CMEDIA\\SETAUDIO\r\n"
    b"SET BLASTER=A220 I5 D1 T4\r\n"
    b"\\SOUND\\CMEDIA\\C3DMIX /MFF000 /FFF000 /WFF000 /L00100 "
    b"/E00100 /A00100 /C00100 /P20000 /400000 /R0f0ff /D040ff\r\n"
)
PLAYLIST = (
    b"ON\r\n"
    b"class001.wav;60\r\n"
    b"schwing.wav;30\r\n"
    b"tech_1.wav;30\r\n"
    b"XYLOPHON.WAV;5\r\n"
    b"XYLOPHON.WAV;5\r\n"
    b"KLINGELN.WAV;5\r\n"
    b"KLINGELN.WAV;5\r\n"
    b"legrind.wav;60\r\n"
    b"[1.12 31.12]\r\n"
    b"weihn001.wav;300\r\n"
    b"weihn002.wav;300\r\n"
    b"weihn003.wav;300\r\n"
    b"weihn004.wav;300\r\n"
    b"weihn005.wav;300\r\n"
    b"weihn006.wav;300\r\n"
)


class Image:
    def __init__(self, path, write=False):
        self.path = path
        self.f = open(path, "r+b" if write else "rb")
        self.f.seek(0, 2)
        self.size = self.f.tell()
        self.f.seek(63 * 512)
        boot = self.f.read(512)
        if boot[510:512] != b"\x55\xAA":
            raise SystemExit(f"{path} has no FAT boot sector at sector 63")
        self.spc = boot[13]
        self.rsvd = struct.unpack_from("<H", boot, 14)[0]
        self.nfats = boot[16]
        self.nroot = struct.unpack_from("<H", boot, 17)[0]
        self.spf = struct.unpack_from("<H", boot, 22)[0]
        self.fat_lba = 63 + self.rsvd
        self.root_lba = self.fat_lba + self.nfats * self.spf
        self.root_secs = (self.nroot * 32 + 511) // 512
        self.data_lba = self.root_lba + self.root_secs
        self.cluster = self.spc * 512
        self.f.seek(self.fat_lba * 512)
        self.fat = bytearray(self.f.read(self.spf * 512))
        self.f.seek((self.fat_lba + self.spf) * 512)
        second = self.f.read(self.spf * 512)
        if second != self.fat:
            raise SystemExit(f"{path} has two different FAT copies")

    def close(self):
        self.f.close()

    def getfat(self, cluster):
        return struct.unpack_from("<H", self.fat, cluster * 2)[0]

    def setfat(self, cluster, value):
        struct.pack_into("<H", self.fat, cluster * 2, value)

    def flush_fats(self):
        raw = bytes(self.fat)
        for copy in range(self.nfats):
            self.f.seek((self.fat_lba + copy * self.spf) * 512)
            self.f.write(raw)

    def cluster_offset(self, cluster):
        return (self.data_lba + (cluster - 2) * self.spc) * 512

    def read_chain(self, cluster, size):
        out = bytearray()
        seen = set()
        while 2 <= cluster < 0xFFF8 and len(out) < size:
            if cluster in seen:
                break
            seen.add(cluster)
            self.f.seek(self.cluster_offset(cluster))
            out += self.f.read(min(self.cluster, size - len(out)))
            cluster = self.getfat(cluster)
        return bytes(out)

    def chain_is_one(self, cluster):
        return self.getfat(cluster) >= 0xFFF8

    def write_file_cluster(self, cluster, data):
        if not self.chain_is_one(cluster):
            raise SystemExit(f"cluster {cluster} is more than one cluster")
        if len(data) > self.cluster:
            raise SystemExit("file does not fit in its cluster")
        buf = bytearray(self.cluster)
        buf[: len(data)] = data
        self.f.seek(self.cluster_offset(cluster))
        self.f.write(buf)

    def alloc(self):
        limit = len(self.fat) // 2
        for cluster in range(2, limit):
            if self.getfat(cluster) == 0:
                self.setfat(cluster, 0xFFFF)
                self.f.seek(self.cluster_offset(cluster))
                self.f.write(bytes(self.cluster))
                return cluster
        raise SystemExit("no free cluster")

    def read_root(self):
        self.f.seek(self.root_lba * 512)
        return bytearray(self.f.read(self.root_secs * 512))

    def write_root(self, data):
        self.f.seek(self.root_lba * 512)
        self.f.write(data)

    def read_dir(self, cluster):
        if not self.chain_is_one(cluster):
            raise SystemExit(f"directory cluster {cluster} spans more than one cluster")
        self.f.seek(self.cluster_offset(cluster))
        return bytearray(self.f.read(self.cluster))

    def write_dir(self, cluster, data):
        self.f.seek(self.cluster_offset(cluster))
        self.f.write(data[: self.cluster])


def entries(data):
    for offset in range(0, len(data) - 31, 32):
        entry = data[offset : offset + 32]
        if entry[0] == 0:
            return
        if entry[0] in (0xE5, 0x05) or entry[11] == 0x0F:
            continue
        name = entry[:8].decode("latin1").rstrip()
        ext = entry[8:11].decode("latin1").rstrip()
        cluster = struct.unpack_from("<H", entry, 26)[0]
        size = struct.unpack_from("<I", entry, 28)[0]
        yield name, ext, cluster, size, entry[11], offset


def find_entry(data, name, ext="", directory=False):
    for item in entries(data):
        if item[0] == name and item[1] == ext and (not directory or item[4] & 0x10):
            return item
    raise SystemExit(f"missing {name}.{ext}" if ext else f"missing {name}")


def make_entry(name, ext, attr, cluster, size):
    entry = bytearray(32)
    entry[0:8] = name.encode("ascii")[:8].ljust(8)
    entry[8:11] = ext.encode("ascii")[:3].ljust(3)
    entry[11] = attr
    struct.pack_into("<H", entry, 26, cluster)
    struct.pack_into("<I", entry, 28, size)
    return entry


def append_entry(data, entry):
    for offset in range(0, len(data) - 31, 32):
        if data[offset] == 0:
            data[offset : offset + 32] = entry
            return offset
        if data[offset] == 0xE5:
            continue
    raise SystemExit("directory is full")


def set_size(data, offset, size):
    struct.pack_into("<I", data, offset + 28, size)


def empty_dir(self_cluster, parent_cluster):
    raw = bytearray(32768)
    raw[0:32] = make_entry(".", "", 0x10, self_cluster, 0)
    raw[32:64] = make_entry("..", "", 0x10, parent_cluster, 0)
    return raw


def read_named(image, directory, name, ext):
    item = find_entry(directory, name, ext)
    return image.read_chain(item[2], item[3]), item


def walk_dir(image, data, parts):
    here = data
    for part in parts:
        item = find_entry(here, part, directory=True)
        here = image.read_dir(item[2])
    return here


def file_from(image, folder_parts, name, ext):
    image_root = image.read_root()
    directory = walk_dir(image, image_root, folder_parts)
    data, item = read_named(image, directory, name, ext)
    return data


def main_regions(data):
    return (
        data[0x900 : 0x900 + len(POLL)],
        data[0xA91 : 0xA91 + len(TIMER_JUMP)],
        data[0x1017 : 0x1017 + len(ELO_INIT)],
    )


def patch_main(image, root):
    main_dir_item = find_entry(root, "MAIN", directory=True)
    main_dir = image.read_dir(main_dir_item[2])
    data, item = read_named(image, main_dir, "MAIN", "COM")
    digest = hashlib.md5(data).hexdigest()
    regions = main_regions(data)
    if digest == GOOD_MAIN or regions == (POLL, TIMER_JUMP, ELO_INIT):
        print("MAIN.COM already patched")
        return
    if regions != (OLD_POLL, OLD_TIMER, OLD_ELO):
        raise SystemExit(
            "MAIN.COM is not the July 1997 program this touch change fits"
        )
    if data[0xC0B : 0xC0B + 6] != SERVICE:
        raise SystemExit("service button bytes are not the cabinet button")
    patched = bytearray(data)
    patched[0x900 : 0x900 + len(POLL)] = POLL
    patched[0xA91 : 0xA91 + len(TIMER_JUMP)] = TIMER_JUMP
    patched[0x1017 : 0x1017 + len(ELO_INIT)] = ELO_INIT
    if digest == ORIG_MAIN and hashlib.md5(patched).hexdigest() != GOOD_MAIN:
        raise SystemExit("MAIN.COM patch did not reproduce the cabinet program")
    if patched[0xC0B : 0xC0B + 6] != SERVICE:
        raise SystemExit("service button changed")
    image.write_file_cluster(item[2], patched)
    print("MAIN.COM", hashlib.md5(patched).hexdigest())


def replace_text_file(image, directory, name, ext, old_prefix, new_bytes):
    data, item = read_named(image, directory, name, ext)
    if data == new_bytes:
        print(f"{name}.{ext} already set")
        return directory
    if name == "PLAY_SND" and not data.startswith(old_prefix):
        print(f"{name}.{ext} left unchanged")
        return directory
    if name == "SND_INIT" and not data.startswith(old_prefix):
        if b"esscfg" not in data.lower():
            raise SystemExit(f"{name}.{ext} is not the Photo Play 2.0 sound startup")
    elif not data.startswith(old_prefix):
        raise SystemExit(f"{name}.{ext} does not have the expected Photo Play 2.0 text")
    image.write_file_cluster(item[2], new_bytes)
    set_size(directory, item[5], len(new_bytes))
    print(f"{name}.{ext} {len(data)} -> {len(new_bytes)} bytes")
    return directory


def add_dir(image, parent, parent_cluster, name):
    for item in entries(parent):
        if item[0] == name and item[4] & 0x10:
            return image.read_dir(item[2]), item[2], parent
    cluster = image.alloc()
    image.write_dir(cluster, empty_dir(cluster, parent_cluster))
    append_entry(parent, make_entry(name, "", 0x10, cluster, 0))
    print("dir", name, "cluster", cluster)
    return image.read_dir(cluster), cluster, parent


def add_file(image, directory, directory_cluster, name, ext, payload):
    for item in entries(directory):
        if item[0] == name and item[1] == ext:
            have = image.read_chain(item[2], item[3])
            if have != payload:
                raise SystemExit(f"{name}.{ext} is already present and differs")
            print(f"{name}.{ext} already present")
            return directory
    cluster = image.alloc()
    image.write_file_cluster(cluster, payload)
    append_entry(directory, make_entry(name, ext, 0x20, cluster, len(payload)))
    image.write_dir(directory_cluster, directory)
    print(f"{name}.{ext} {len(payload)} bytes, cluster {cluster}")
    return image.read_dir(directory_cluster)


def stones_holes(image):
    holes = []
    try:
        root = image.read_root()
        stones = image.read_dir(find_entry(root, "STONES", directory=True)[2])
    except SystemExit:
        return list(STONES_FILES)
    folders = {}
    for folder, name, ext, size in STONES_FILES:
        if folder not in folders:
            try:
                item = find_entry(stones, folder, directory=True)
                folders[folder] = image.read_dir(item[2])
            except SystemExit:
                folders[folder] = None
        directory = folders[folder]
        if directory is None:
            holes.append((folder, name, ext, size))
            continue
        try:
            data, _ = read_named(image, directory, name, ext)
        except SystemExit:
            holes.append((folder, name, ext, size))
            continue
        if len(data) == 0:
            holes.append((folder, name, ext, size))
    return holes


def put_file(image, directory, directory_cluster, name, ext, payload):
    count = max(1, (len(payload) + image.cluster - 1) // image.cluster)
    first = None
    prev = None
    for _ in range(count):
        cluster = image.alloc()
        if first is None:
            first = cluster
        if prev is not None:
            image.setfat(prev, cluster)
        prev = cluster
    remaining = payload
    cluster = first
    while remaining:
        chunk = remaining[: image.cluster]
        remaining = remaining[image.cluster :]
        buf = bytearray(image.cluster)
        buf[: len(chunk)] = chunk
        image.f.seek(image.cluster_offset(cluster))
        image.f.write(buf)
        cluster = image.getfat(cluster)
    replaced = False
    for item in entries(directory):
        if item[0] == name and item[1] == ext:
            struct.pack_into("<H", directory, item[5] + 26, first)
            set_size(directory, item[5], len(payload))
            replaced = True
            break
    if not replaced:
        append_entry(directory, make_entry(name, ext, 0x20, cluster=first, size=len(payload)))
    image.write_dir(directory_cluster, directory)


def restore_stones(image, donor_path, holes):
    donor = Image(donor_path)
    try:
        donor_root = donor.read_root()
        donor_stones = donor.read_dir(find_entry(donor_root, "STONES", directory=True)[2])
        out_root = image.read_root()
        out_stones = image.read_dir(find_entry(out_root, "STONES", directory=True)[2])
        donor_dirs = {}
        out_dirs = {}
        for folder, name, ext, size in holes:
            if folder not in donor_dirs:
                item = find_entry(donor_stones, folder, directory=True)
                donor_dirs[folder] = donor.read_dir(item[2])
                out_item = find_entry(out_stones, folder, directory=True)
                out_dirs[folder] = [image.read_dir(out_item[2]), out_item[2]]
            data, _ = read_named(donor, donor_dirs[folder], name, ext)
            if len(data) != size:
                raise SystemExit(
                    f"STONES\\{folder}\\{name}.{ext} is {len(data)} bytes on the "
                    f"source disk, expected {size}"
                )
            directory, directory_cluster = out_dirs[folder]
            put_file(image, directory, directory_cluster, name, ext, data)
            out_dirs[folder][0] = image.read_dir(directory_cluster)
            print(f"STONES\\{folder}\\{name}.{ext}", len(data))
    finally:
        donor.close()


def filesystem_end(image):
    last = 2
    for cluster in range(2, len(image.fat) // 2):
        if image.getfat(cluster) != 0:
            last = cluster
    return (image.data_lba + (last - 1) * image.spc) * 512


def copy_for_card(src, dst):
    size = src.stat().st_size
    if size < CARD_BYTES:
        raise SystemExit(
            f"{src} is {size} bytes. Photo Play 2.0 for this card is "
            f"{CARD_BYTES} bytes, or the larger disk image that contains it."
        )
    with src.open("rb") as source, dst.open("wb") as target:
        left = CARD_BYTES
        while left:
            chunk = source.read(min(8 * 1024 * 1024, left))
            if len(chunk) != min(8 * 1024 * 1024, left):
                raise SystemExit(f"{src} ended before {CARD_BYTES} bytes")
            target.write(chunk)
            left -= len(chunk)
    if size == CARD_BYTES:
        return
    with dst.open("r+b") as card:
        card.seek(446 + 8)
        lba = struct.unpack("<I", card.read(4))[0]
        if lba != PART_LBA:
            raise SystemExit("partition does not start at sector 63")
        card.seek(446 + 12)
        card.write(struct.pack("<I", PART_SECTORS))
        card.seek(PART_LBA * 512 + 32)
        card.write(struct.pack("<I", PART_SECTORS))
    print("fitted the disk image to the 2 GB card")


def build(source, pp2004, output, stones_from=None):
    source = Path(source)
    pp2004 = Path(pp2004)
    output = Path(output)
    stones_from = Path(stones_from) if stones_from else None
    protected = {source.resolve(), pp2004.resolve()}
    if stones_from is not None:
        protected.add(stones_from.resolve())
    if output.resolve() in protected:
        raise SystemExit("output must be a new file")
    probe = Image(source)
    if probe.spc != 64 or probe.cluster != 32768:
        probe.close()
        raise SystemExit("unexpected FAT layout on the Photo Play 2.0 image")
    holes = stones_holes(probe)
    end = filesystem_end(probe)
    probe.close()
    if holes and stones_from is None:
        missing = "\n".join(f"  STONES\\{folder}\\{name}.{ext}" for folder, name, ext, _ in holes)
        raise SystemExit(
            "Stones is missing sound, round, or picture files. They are not stored "
            "in this script. Re-run with --stones-from pointing at a Photo Play 2.0 "
            "disk that still has them, such as the protected PP20NL image.\n"
            + missing
        )
    if end > CARD_BYTES:
        raise SystemExit("the Photo Play files extend past the 2 GB card")
    print("copy", source, "->", output)
    copy_for_card(source, output)

    src = Image(pp2004)
    elodev = file_from(src, ["TOUCH", "ELO"], "ELODEV", "EXE")
    ckusb = file_from(src, ["SOUND", "6WEV"], "CKUSB", "EXE")
    setaudio = file_from(src, ["SOUND", "CMEDIA"], "SETAUDIO", "COM")
    c3dmix = file_from(src, ["SOUND", "CMEDIA"], "C3DMIX", "COM")
    src.close()
    if hashlib.md5(elodev).hexdigest() != ELODEV_MD5:
        raise SystemExit("ELODEV.EXE from the 2004 image is not the expected file")
    if b"H5" in SND_INIT:
        raise SystemExit("sound startup must not set H5")

    out = Image(output, write=True)
    root = out.read_root()
    patch_main(out, root)

    autopts, auto_item = read_named(out, root, "AUTOPTS", "BAT")
    needle = b"call \\sound\\snd_init.bat\r\n\r\ncd\\main\r\n"
    insert = b"call \\sound\\snd_init.bat\r\n\r\n" + ELO_LINE + b"\r\ncd\\main\r\n"
    if ELO_LINE in autopts:
        print("AUTOPTS.BAT already starts ELODEV")
    elif needle not in autopts:
        raise SystemExit("AUTOPTS.BAT does not start the sound script before main")
    else:
        updated = autopts.replace(needle, insert, 1)
        out.write_file_cluster(auto_item[2], updated)
        set_size(root, auto_item[5], len(updated))
        print("AUTOPTS.BAT starts ELODEV with -W0")

    main_item = find_entry(root, "MAIN", directory=True)
    main_dir = out.read_dir(main_item[2])
    main_dir = replace_text_file(
        out, main_dir, "PLAY_SND", "INI", b"OFF\r\n", PLAYLIST
    )
    out.write_dir(main_item[2], main_dir)

    sound_item = find_entry(root, "SOUND", directory=True)
    sound = out.read_dir(sound_item[2])
    sound = replace_text_file(
        out, sound, "SND_INIT", "BAT", b"SET BLASTER=A220 I5 D1 T4\r\n", SND_INIT
    )

    touch, touch_cluster, root = add_dir(out, root, 0, "TOUCH")
    elo, elo_cluster, touch = add_dir(out, touch, touch_cluster, "ELO")
    elo = add_file(out, elo, elo_cluster, "ELODEV", "EXE", elodev)
    out.write_dir(touch_cluster, touch)

    wev, wev_cluster, sound = add_dir(out, sound, sound_item[2], "6WEV")
    wev = add_file(out, wev, wev_cluster, "CKUSB", "EXE", ckusb)
    media, media_cluster, sound = add_dir(out, sound, sound_item[2], "CMEDIA")
    media = add_file(out, media, media_cluster, "SETAUDIO", "COM", setaudio)
    media = add_file(out, media, media_cluster, "C3DMIX", "COM", c3dmix)
    out.write_dir(sound_item[2], sound)
    out.write_root(root)
    if holes:
        restore_stones(out, stones_from, holes)
    out.flush_fats()
    out.f.flush()
    verify(out)
    out.close()
    print("wrote", output)


def verify(image):
    image.f.seek((image.fat_lba + image.spf) * 512)
    if image.f.read(image.spf * 512) != image.fat:
        raise SystemExit("FAT copies differ")
    root = image.read_root()
    main_dir = image.read_dir(find_entry(root, "MAIN", directory=True)[2])
    main, _ = read_named(image, main_dir, "MAIN", "COM")
    if main_regions(main) != (POLL, TIMER_JUMP, ELO_INIT):
        raise SystemExit("MAIN.COM verification failed")
    if main[0xC0B : 0xC0B + 6] != SERVICE:
        raise SystemExit("service button verification failed")
    play, _ = read_named(image, main_dir, "PLAY_SND", "INI")
    if play != PLAYLIST and play.startswith(b"OFF\r\n"):
        raise SystemExit("playlist verification failed")
    autopts, _ = read_named(image, root, "AUTOPTS", "BAT")
    if ELO_LINE not in autopts or b"H5" in autopts:
        raise SystemExit("AUTOPTS verification failed")
    sound = image.read_dir(find_entry(root, "SOUND", directory=True)[2])
    startup, _ = read_named(image, sound, "SND_INIT", "BAT")
    if startup != SND_INIT:
        raise SystemExit("SND_INIT verification failed")
    elo = walk_dir(image, root, ["TOUCH", "ELO"])
    driver, _ = read_named(image, elo, "ELODEV", "EXE")
    if hashlib.md5(driver).hexdigest() != ELODEV_MD5:
        raise SystemExit("ELODEV verification failed")
    if stones_holes(image):
        raise SystemExit("Stones files are still missing")
    print("verified")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    here = Path(__file__).resolve().parents[1]
    parser.add_argument(
        "--input",
        "--cracked",
        dest="source",
        default=here / "cracked_IGO2000" / "PP20NLC2_cf.img",
        help="Photo Play 2.0 image, protected or not",
    )
    parser.add_argument(
        "--pp2004",
        default=here / "cracked_IGO2004" / "PP2004NLC.img",
        help="Photo Play 2004 image, source of ELODEV and the C-Media tools",
    )
    parser.add_argument(
        "--output",
        default=here / "cracked_IGO2000" / "PP20NLC2_cabinet.img",
        help="new cabinet image to create",
    )
    parser.add_argument(
        "--stones-from",
        help="Photo Play 2.0 disk that still has the Stones sounds, used when the input disk lost them",
    )
    args = parser.parse_args()
    build(args.source, args.pp2004, args.output, args.stones_from)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.exit(0)
