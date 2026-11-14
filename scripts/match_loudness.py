"""Set the loudness of each generated voice file to the loudness of its retail line.

usage: match_loudness.py <work dir> <mod data/voice dir> <suffix> [wav ...]

<work dir> holds the retail voice files in voice/ (the output of extract_en.py).
<suffix> is cn or tw: the script reads and rewrites <name>-<suffix>.ogg.
The TTS models give very different levels (BreezyVoice was 6 to 18 dB below the
retail lines), so each file gets the integrated loudness (EBU R128) of its
retail line. A limiter keeps the peaks at -1 dBFS.
"""
import os, re, subprocess, sys

work, voice, suffix, *only = sys.argv[1:]


def loudness(path):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return float(re.findall(r"^\s+I:\s+(-?[\d.]+) LUFS", err, re.M)[-1])


retail = {f.lower(): os.path.join(work, "voice", f) for f in os.listdir(os.path.join(work, "voice"))}
for folder, _, files in os.walk(voice):
    for f in sorted(files):
        if not f.endswith(f"-{suffix}.ogg"):
            continue
        name = f[: -len(f"-{suffix}.ogg")] + ".wav"
        if only and name not in only:
            continue
        out = os.path.join(folder, f)
        target, now = loudness(retail[name.lower()]), loudness(out)
        tmp = out + ".tmp.ogg"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", out, "-af",
                        f"volume={target - now:.2f}dB,alimiter=limit=0.891:level=false", "-c:a", "libvorbis", "-q:a", "6", tmp], check=True)
        os.replace(tmp, out)
        print(f"{name}: {now:.1f} -> {loudness(out):.1f} LUFS (retail {target:.1f})", flush=True)
