"""Extract the English lines and voice files of one mission from a retail FreeSpace 2.

usage: extract_en.py <FS2 folder with the .vp files> <mission or table file name> <work dir> [wav ...]

The file can be a mission (Training-1.fs2) or messages.tbl, whose built-in
messages all missions share. With wav names, only those lines are extracted.
Writes <work dir>/<file>.en.csv (wav, folder, xstr, seconds, en) and the voice
files as 16 kHz mono wav in <work dir>/voice/. The English text and the voice files
belong to the owners of FreeSpace 2, so the work dir is not in git.
"""
import csv, glob, os, re, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # python -I leaves this off
from vpx import read_vp  # noqa: E402

fs2, mission, work, *only = sys.argv[1:]
only = {w.lower() for w in only}
vps = sorted(glob.glob(os.path.join(fs2, "*.vp")))
files = {}  # lower-case name -> (vp, offset, size, folder); a later .vp overrides an earlier one, as in the engine
for vp in vps:
    for path, off, size in read_vp(vp):
        files[os.path.basename(path).lower()] = (vp, off, size, os.path.basename(os.path.dirname(path)))

def data(name):
    vp, off, size, _ = files[name.lower()]
    with open(vp, "rb") as f:
        f.seek(off)
        return f.read(size)

text = data(mission).decode("latin1")
# Each voice reference belongs to the last XSTR before it: stage text, briefing text, debriefing text or message.
refs = re.finditer(r"(?:\+Wave Filename|\$voice|\$Voice|\+Wave Name):\s*(\S+\.wav)", text, re.I)
rows = []
for m in refs:
    start = text.rfind('XSTR("', 0, m.start())
    x = re.match(r'XSTR\("(.*?)", (-?\d+)\)', text[start:], re.S)
    if not only or m.group(1).lower() in only:
        rows.append((m.group(1), x.group(2), " ".join(x.group(1).split())))

os.makedirs(os.path.join(work, "voice"), exist_ok=True)
base = os.path.splitext(mission)[0]
with open(os.path.join(work, base + ".en.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["wav", "folder", "xstr", "seconds", "en"])
    for wav, xid, en in rows:
        out = os.path.join(work, "voice", wav)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", "pipe:0", "-ar", "16000", "-ac", "1", out],
                       input=data(wav), check=True)
        secs = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out],
                              capture_output=True, text=True, check=True).stdout.strip()
        w.writerow([wav, files[wav.lower()][3], xid, f"{float(secs):.1f}", en])
print(f"{len(rows)} lines -> {work}")
