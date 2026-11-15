"""The Vasudan radio voice: a made-up Vasudan layer under the translator voice. Used by gen_tw.py and gen_cn.py.

The made-up words follow the English line, so the layer of a line is the same in every language. gen_tw.py makes
it and keeps it as <work dir>/vasudan-tw/<name>-vasudan.wav; each generator keeps its raw translator voice as
<work dir>/vasudan-<lang>/<name>-zh.wav.

Remix the Vasudan lines of one language from the kept files, without the TTS model:
  python3 -I <repo>/scripts/vasudan.py <work dir> <mod data/voice dir> cn|tw [wav ...]
"""
import csv, os, random, subprocess, sys, tempfile
import numpy as np, soundfile as sf

# The Vasudans speak through a machine translator. In the retail files the Vasudan speech plays under the
# English, which comes 0.3 to 0.5 s later, also after each pause (heard by the project owner, 2026-11-15).
# The Vasudan layer sounds the same for every Vasudan; only the translator voice is male or female.
# The tw mod makes the Vasudan layer from made-up words (the word parts of the Hard Light Productions
# Vasudan reference), read in the timbre of a retail Vasudan line, lowered in pitch and with an echo.
VASUDAN = {"persona6", "persona7", "vasudan_support", "vasudan_awacs"}
VASUDAN_VOICE = "6_backup.wav"
VASUDAN_ROOTS = ["os", "ad", "ur", "osoy", "adoy", "uroy", "har", "sof", "yul", "sa"]
VASUDAN_ENDS = ["i", "at", "arut", "ibeh", "it", "eh"]
VASUDAN_DELAY_MS = 500  # 0.3 s was too short (2026-11-15)
# The level of the Vasudan layer against the translator voice (RMS, dB). A fixed gain of 0.35 gave -5 dB against
# the tw translator, which the project owner tuned by ear, but -11 dB against the louder cn translator (2026-11-16).
VASUDAN_REL_DB = -5.0
# The tw translator is a Taiwan speaker made to sound like a speech synthesizer of the 2000s: telephone band,
# 8 kHz and 6 bits, and a 70 Hz modulation for a metallic tone. The built-in CosyVoice voices had a mainland
# accent; the project owner chose this "strong" version from three (2026-11-15).
TW_TRANSLATOR_EFFECT = ("highpass=f=300,lowpass=f=3400,aresample=8000,acrusher=bits=6:mode=lin:mix=0.7,"
                        "aresample={sr},aeval=val(0)*(0.55+0.45*sin(2*PI*70*t)):c=same,volume=1.6")
# The Vasudan layer must end before the end of the translator, or it does not sound like a live translation (the
# project owner, 2026-11-15). The layer is first made faster, up to VASUDAN_MAX_TEMPO, then cut at a pause.
VASUDAN_END_BEFORE_S, VASUDAN_MAX_TEMPO = 0.6, 1.25


def vasudan_text(en, seed):
    """Made-up Vasudan words, one for each word of the English line, the same for each run.

    In the story the Vasudan line is the original and the Chinese is its translation, so the length of the
    Vasudan line follows the retail line, not the Chinese (the project owner, 2026-11-15)."""
    rng = random.Random(seed)
    # One made-up word for each English word made the layer 1.75 times too long (median of 41 lines, 2026-11-15).
    n = max(3, round(len(en.split()) * 0.5))  # two short words gave 0.16 s of sound (7_Death, 2026-11-15)
    words = [rng.choice(VASUDAN_ROOTS) + rng.choice(VASUDAN_ENDS) for _ in range(n)]
    if n < 4:  # a one-word first sentence left a pause right after the first syllable (6_Delta, 2026-11-15)
        return " ".join(words).capitalize() + "."
    return " ".join(words[: n // 2]).capitalize() + ". " + " ".join(words[n // 2:]).capitalize() + "."


def lead_trim(x, sample_rate, below_peak_db=30):
    """Cut the start up to the first 30 ms within below_peak_db of the loudest frame.

    ffmpeg silenceremove at -40 dB left 0.3 to 0.4 s of near silence before many Vasudan layers (measured
    2026-11-15): a single loud sample at the start ends its trim. A threshold relative to the peak also
    follows a quiet take."""
    n = int(sample_rate * 0.01)
    if len(x) < 3 * n:
        return x
    frames = x[: len(x) // n * n].reshape(-1, n)
    rms = (frames.astype("float64") ** 2).mean(axis=1) ** 0.5 + 1e-9
    loud = rms >= rms.max() * 10 ** (-below_peak_db / 20)
    held = loud[:-2] & loud[1:-1] & loud[2:]  # 30 ms of sound, so that a click does not count
    first = int(held.argmax()) if held.any() else 0
    return x[max(0, first - 2) * n:]


def ffmpeg_filter(x, sample_rate, filt):
    with tempfile.TemporaryDirectory() as d:
        a, b = os.path.join(d, "in.wav"), os.path.join(d, "out.wav")
        sf.write(a, x, sample_rate)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", a, "-af", filt, b], check=True)
        return sf.read(b, dtype="float32")[0]


def resample(x, rate, to_rate):
    """x at rate, made rate to_rate (CosyVoice writes 24 kHz, IndexTTS 22.05 kHz)."""
    if rate == to_rate:
        return x
    with tempfile.TemporaryDirectory() as d:
        a, b = os.path.join(d, "in.wav"), os.path.join(d, "out.wav")
        sf.write(a, x, rate)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", a, "-ar", str(to_rate), b], check=True)
        return sf.read(b, dtype="float32")[0]


def last_pause(x, sample_rate, before, below_peak_db=25, min_s=0.05):
    """Sample index inside the last pause (of at least min_s) before the index `before`, or None."""
    n = int(sample_rate * 0.01)
    if len(x) < n:
        return None
    frames = x[: len(x) // n * n].reshape(-1, n)
    rms = (frames.astype("float64") ** 2).mean(axis=1) ** 0.5 + 1e-9
    quiet = rms < rms.max() * 10 ** (-below_peak_db / 20)
    best, run = None, 0
    for i, q in enumerate(quiet[: before // n]):
        run = run + 1 if q else 0
        if run >= min_s / 0.01:
            best = (i - run // 2) * n
    return best


def fit_vasudan(bed, sample_rate, target):
    """Make the layer at most `target` samples long: faster first, then cut at a pause, with a fade-out."""
    if len(bed) <= target:
        return bed
    bed = ffmpeg_filter(bed, sample_rate, f"atempo={min(len(bed) / target, VASUDAN_MAX_TEMPO):.4f}")
    if len(bed) <= target:
        return bed
    # A pause in the first half would leave a fragment of the layer, so it is cut hard at the target then.
    cut = last_pause(bed, sample_rate, target)
    if cut is None or cut < target // 2:
        cut = target
    bed = bed[:cut].copy()
    fade = min(len(bed), int(sample_rate * 0.15))
    bed[len(bed) - fade:] *= np.linspace(1.0, 0.0, fade, dtype=bed.dtype)
    return bed


def vasudan_mix(translator, vasudan, sample_rate, out, effect=None):
    """The translator voice VASUDAN_DELAY_MS after the Vasudan layer; the layer ducks while the translator speaks.

    effect is an ffmpeg filter for the translator voice, with {sr} for the sample rate (tw: TRANSLATOR_EFFECT)."""
    with tempfile.TemporaryDirectory() as d:
        a, b = os.path.join(d, "t.wav"), os.path.join(d, "v.wav")
        # The delay counts from the first sound of each voice: the model output can start with silence, and the
        # project owner heard the Vasudan layer start late (2026-11-15).
        translator = lead_trim(translator, sample_rate)
        if effect:
            translator = ffmpeg_filter(translator, sample_rate, effect.format(sr=sample_rate))
        sf.write(a, translator, sample_rate)
        # The made-up words carry no meaning, so the Vasudan layer can lose a soft first syllable: at 30 dB the
        # layer kept a start 20 dB softer than the rest, which sounded like a gap (2026-11-15).
        # The lower pitch also makes the layer 1.25 times longer, so the fit comes after it.
        # The model can pause inside the made-up words, which sounded like a gap before the translator
        # (6_Delta, 2026-11-15); a pause longer than 0.08 s is cut (0.15 s left a dip in 6_repair).
        bed = ffmpeg_filter(lead_trim(vasudan, sample_rate, below_peak_db=20), sample_rate,
                            "silenceremove=stop_periods=-1:stop_duration=0.08:stop_threshold=-40dB,"
                            f"asetrate={sample_rate}*0.8,aresample={sample_rate}")
        # The layer ends VASUDAN_END_BEFORE_S before the end of the delayed translator. A translator take of a
        # few tens of ms would leave no room, so the layer always keeps at least 0.3 s.
        target = max(len(translator) + int(sample_rate * (VASUDAN_DELAY_MS / 1000 - VASUDAN_END_BEFORE_S)),
                     int(sample_rate * 0.3))
        bed = fit_vasudan(bed, sample_rate, target)
        rms = lambda x: float(np.sqrt(np.mean(np.square(x, dtype="float64")))) + 1e-9
        bed = (bed * (rms(translator) / rms(bed) * 10 ** (VASUDAN_REL_DB / 20))).astype("float32")
        sf.write(b, bed, sample_rate)
        filt = ("[1:a]aecho=0.8:0.6:40:0.4[bed];"
                f"[0:a]adelay={VASUDAN_DELAY_MS},asplit=2[zh][sc];"
                "[bed][sc]sidechaincompress=threshold=0.02:ratio=6:attack=15:release=250[d];"
                "[d][zh]amix=inputs=2:duration=longest:normalize=0")
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", a, "-i", b, "-filter_complex", filt,
                        "-c:a", "libvorbis", "-q:a", "6", out], check=True)


def remix(work, voice_out, lang, only=(), effect=None):
    """Mix again the kept voices of each Vasudan line of messages.csv; returns the names it wrote."""
    lines = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lines", "messages.csv")
    folder_of = {}
    for name in sorted(os.listdir(work)):
        if name.endswith(".en.csv"):
            with open(os.path.join(work, name), encoding="utf-8") as f:
                for e in csv.DictReader(f):
                    folder_of.setdefault(e["wav"].lower(), e["folder"])
    done = []
    with open(lines, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            base = r["wav"][:-4]
            if r["speaker"] not in VASUDAN or base in done or (only and r["wav"] not in only):
                continue
            zh, sr = sf.read(os.path.join(work, f"vasudan-{lang}", base + "-zh.wav"), dtype="float32")
            bed, bed_sr = sf.read(os.path.join(work, "vasudan-tw", base + "-vasudan.wav"), dtype="float32")
            bed = resample(bed, bed_sr, sr)
            vasudan_mix(zh, bed, sr, os.path.join(voice_out, folder_of[r["wav"].lower()], f"{base}-{lang}.ogg"), effect)
            done.append(base)
    return done


if __name__ == "__main__":
    work, voice_out, lang, *only = sys.argv[1:]
    print("remixed", len(remix(work, voice_out, lang, only, TW_TRANSLATOR_EFFECT if lang == "tw" else None)))
