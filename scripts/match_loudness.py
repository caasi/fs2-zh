"""Set the loudness of each generated voice file to the loudness of its retail line.

usage: match_loudness.py <work dir> <mod data/voice dir> <language> [wav ...]

<work dir> holds the retail voice files in voice/ (the output of extract_en.py).
<language> is cn or tw: the script reads and rewrites the .ogg files in each <language>/ subfolder.
The TTS models give very different levels (BreezyVoice was 6 to 18 dB below the
retail lines), so each file gets the integrated loudness (EBU R128) of its
retail line. A limiter keeps the peaks at -1 dBFS.
"""
import os, re, subprocess, sys

work, voice, lang, *only = sys.argv[1:]


def loudness(path):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return float(re.findall(r"^\s+I:\s+(-?[\d.]+) LUFS", err, re.M)[-1])


retail = {f.lower(): os.path.join(work, "voice", f) for f in os.listdir(os.path.join(work, "voice"))}
for folder, _, files in os.walk(voice):
    for f in sorted(files):
        if os.path.basename(folder) != lang or not f.endswith(".ogg") or f.endswith(".tmp.ogg"):
            continue
        name = f[: -len(".ogg")] + ".wav"
        if only and name not in only:
            continue
        out = os.path.join(folder, f)
        target, now = loudness(retail[name.lower()]), loudness(out)
        tmp = out + ".tmp.ogg"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", out, "-af",
                        f"volume={target - now:.2f}dB,alimiter=limit=0.891:level=false", "-c:a", "libvorbis", "-q:a", "6", tmp], check=True)
        os.replace(tmp, out)
        print(f"{name}: {now:.1f} -> {loudness(out):.1f} LUFS (retail {target:.1f})", flush=True)
