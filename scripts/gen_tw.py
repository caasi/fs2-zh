"""Make the zh-TW voice files of one mission with CosyVoice 3.

usage (from the CosyVoice checkout):
  .venv/bin/python <repo>/scripts/gen_tw.py <CosyVoice 3 model dir> <lines.csv> <work dir> <Common Voice zh-TW dir> <mod data/voice dir> [wav ...]

<CosyVoice 3 model dir> holds the weights of FunAudioLLM/Fun-CosyVoice3-0.5B-2512.
<work dir> holds the output of extract_en.py. <Common Voice zh-TW dir> is the
folder with validated.tsv and clips/ of Common Voice 27.0 zh-TW. Each speaker
of the game gets one Common Voice speaker as the reference voice (see
docs/voices-tw.md). The reference clip is made once in <work dir>/refs-tw/.
Output is <name>-tw.ogg in the voice folder of the retail file.

The model reads the line in Simplified script: with Traditional script the
output was less fluent (heard on 2026-11-14). The line in the CSV stays in
Traditional script. A bopomofo mark 字[:ㄗㄞ3] becomes the CosyVoice pinyin
mark [z][ǎi], which replaces the character.
"""
import csv, os, random, re, subprocess, sys, tempfile, time
import numpy as np, soundfile as sf, torch
from opencc import OpenCC

INITIALS = {"ㄅ": "b", "ㄆ": "p", "ㄇ": "m", "ㄈ": "f", "ㄉ": "d", "ㄊ": "t", "ㄋ": "n", "ㄌ": "l", "ㄍ": "g", "ㄎ": "k",
            "ㄏ": "h", "ㄐ": "j", "ㄑ": "q", "ㄒ": "x", "ㄓ": "zh", "ㄔ": "ch", "ㄕ": "sh", "ㄖ": "r", "ㄗ": "z", "ㄘ": "c", "ㄙ": "s"}
FINALS = {"ㄚ": "a", "ㄛ": "o", "ㄜ": "e", "ㄝ": "e", "ㄞ": "ai", "ㄟ": "ei", "ㄠ": "ao", "ㄡ": "ou", "ㄢ": "an", "ㄣ": "en",
          "ㄤ": "ang", "ㄥ": "eng", "ㄦ": "er", "ㄧ": "i", "ㄨ": "u", "ㄩ": "ü", "ㄧㄚ": "ia", "ㄧㄝ": "ie", "ㄧㄠ": "iao",
          "ㄧㄡ": "iu", "ㄧㄢ": "ian", "ㄧㄣ": "in", "ㄧㄤ": "iang", "ㄧㄥ": "ing", "ㄨㄚ": "ua", "ㄨㄛ": "uo", "ㄨㄞ": "uai",
          "ㄨㄟ": "ui", "ㄨㄢ": "uan", "ㄨㄣ": "un", "ㄨㄤ": "uang", "ㄨㄥ": "ong", "ㄩㄝ": "üe", "ㄩㄢ": "üan", "ㄩㄣ": "ün", "ㄩㄥ": "iong"}
TONED = {"a": "āáǎà", "o": "ōóǒò", "e": "ēéěè", "i": "īíǐì", "u": "ūúǔù", "ü": "ǖǘǚǜ"}
t2s = OpenCC("t2s")


def pinyin_mark(bopomofo):
    """ㄗㄞ3 -> [z][ǎi].  Only a syllable with an initial; a mark without one is an error."""
    tone = int(bopomofo[-1]) if bopomofo[-1].isdigit() else 1
    body = bopomofo.rstrip("0123456789")
    if body[0] not in INITIALS:
        raise ValueError(f"no initial in [:{bopomofo}]; write this mark by hand")
    if tone not in (1, 2, 3, 4):
        # CosyVoice 3 has a toneless token ([e]), but it dropped the syllable when tested (DTM_IN_24, 2026-11-15)
        raise ValueError(f"neutral tone in [:{bopomofo}] is not read by CosyVoice; leave the character unmarked")
    # ㄓㄔㄕㄖㄗㄘㄙ alone have an empty final, written -i in pinyin (ㄕ = shi)
    final = "i" if body[1:] == "" and body[0] in "ㄓㄔㄕㄖㄗㄘㄙ" else FINALS[body[1:]]
    # the tone mark goes on a, then o or e, else on the last vowel (iu, ui)
    if body[0] in "ㄐㄑㄒ":  # pinyin writes ü as u after j, q and x (ㄐㄩ = ju)
        final = final.replace("ü", "u")
    vowel = next((v for v in "aoe" if v in final), None) or [c for c in final if c in TONED][-1]
    i = final.index(vowel)
    final = final[:i] + TONED[vowel][tone - 1] + final[i + 1:]
    return f"[{INITIALS[body[0]]}][{final}]"


# Characters whose standard reading in Taiwan differs from the mainland reading that CosyVoice uses.
# Each unmarked one gets the Taiwan reading. Add a character here only after a listen confirms the
# mainland reading in the output; mark a word-specific reading in the CSV instead.
TW_READINGS = {"擊": "ㄐㄧ2",  # CosyVoice says jī; Taiwan says jí (攻擊, 2026-11-15)
               "識": "ㄕ4"}  # CosyVoice says shí; Taiwan says shì (識別, 2026-11-15)


def tts_text(zh_tw):
    """The line as CosyVoice reads it: a marked character becomes its pinyin mark, the rest Simplified script."""
    marked = re.sub(r".\[:([^\]]+)\]", lambda m: pinyin_mark(m.group(1)), zh_tw)
    marked = "".join(pinyin_mark(TW_READINGS[c]) if c in TW_READINGS else c for c in marked)
    return t2s.convert(marked)


# The first 10 characters of the Common Voice client_id; docs/voices-tw.md records the selection.
SPEAKER = {"loukakis": "d070d9ecfc", "briefing": "47f5d1a312", "instructor": "49460f8c97",
           # messages.tbl. Terran Command is the briefing voice. The Vasudans speak through a machine
           # translator with one male and one female voice, so the male Vasudan speakers share one id.
           "terran_command": "47f5d1a312", "persona1": "557ebe984b", "persona2": "7296001402", "persona3": "7af1af1921",
           "persona4": "dee6c34e84", "persona5": "ce175bd795", "persona6": "b7e8c8f4be", "persona7": "4be53f68d4",
           "vasudan_support": "b7e8c8f4be", "vasudan_awacs": "b7e8c8f4be", "support": "9076596318", "awacs": "c1a8a2007f"}
# A cry with no words keeps the retail voice: the engine plays <name>.wav when <name>-tw.ogg does not exist.
RETAIL_VOICE = {"2_Death.wav"}

# The Vasudans speak through a machine translator. In the retail files the Vasudan speech plays under the
# English, which comes 0.3 to 0.5 s later, also after each pause (heard by the project owner, 2026-11-15).
# The Vasudan layer sounds the same for every Vasudan; only the translator voice is male or female.
# The tw mod makes the Vasudan layer from made-up words (the word parts of the Hard Light Productions
# Vasudan reference), read in the timbre of a retail Vasudan line, lowered in pitch and with an echo.
VASUDAN = {"persona6", "persona7", "vasudan_support", "vasudan_awacs"}
VASUDAN_VOICE = "6_backup.wav"
VASUDAN_ROOTS = ["os", "ad", "ur", "osoy", "adoy", "uroy", "har", "sof", "yul", "sa"]
VASUDAN_ENDS = ["i", "at", "arut", "ibeh", "it", "eh"]
VASUDAN_DELAY_MS, VASUDAN_LEVEL = 500, 0.35  # 0.3 s and 0.2 were too short and too quiet (2026-11-15)
# The Vasudan layer must end before the end of the translator, or it does not sound like a live translation (the
# project owner, 2026-11-15). The layer is first made faster, up to VASUDAN_MAX_TEMPO, then cut at a pause.
VASUDAN_END_BEFORE_S, VASUDAN_MAX_TEMPO = 0.6, 1.25
# The translator is a Taiwan speaker made to sound like a speech synthesizer of the 2000s: telephone band,
# 8 kHz and 6 bits, and a 70 Hz modulation for a metallic tone. The built-in CosyVoice voices had a mainland
# accent; the project owner chose this "strong" version from three (2026-11-15).
TRANSLATOR_EFFECT = ("highpass=f=300,lowpass=f=3400,aresample=8000,acrusher=bits=6:mode=lin:mix=0.7,"
                     "aresample={sr},aeval=val(0)*(0.55+0.45*sin(2*PI*70*t)):c=same,volume=1.6")


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


def vasudan_mix(translator, vasudan, sample_rate, out):
    """The translator voice VASUDAN_DELAY_MS after the Vasudan layer; the layer ducks while the translator speaks."""
    with tempfile.TemporaryDirectory() as d:
        a, b = os.path.join(d, "t.wav"), os.path.join(d, "v.wav")
        # The delay counts from the first sound of each voice: the model output can start with silence, and the
        # project owner heard the Vasudan layer start late (2026-11-15).
        translator = ffmpeg_filter(lead_trim(translator, sample_rate), sample_rate,
                                   TRANSLATOR_EFFECT.format(sr=sample_rate))
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
        sf.write(b, fit_vasudan(bed, sample_rate, target), sample_rate)
        filt = (f"[1:a]aecho=0.8:0.6:40:0.4,volume={VASUDAN_LEVEL}[bed];"
                f"[0:a]adelay={VASUDAN_DELAY_MS},asplit=2[zh][sc];"
                "[bed][sc]sidechaincompress=threshold=0.02:ratio=6:attack=15:release=250[d];"
                "[d][zh]amix=inputs=2:duration=longest:normalize=0")
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", a, "-i", b, "-filter_complex", filt,
                        "-c:a", "libvorbis", "-q:a", "6", out], check=True)


# The Common Voice references are calm reading, so a cry comes out flat. These lines get a style instruction
# (CosyVoice instruct mode) in place of the plain zero-shot prompt.
STYLE = {"_Death.wav": "请用极度惊恐、拼命大声喊叫的语气说这句话，像飞机正在坠毁。"}


def style_of(wav):
    return next((v for k, v in STYLE.items() if wav.endswith(k)), None)


REF_SECONDS = 13  # 10 to 20 s of speech is enough for a zero-shot reference


def reference(work, cv, speaker_id):
    """Join the first validated clips of one speaker into one wav, and return it with its transcript."""
    out = os.path.join(work, "refs-tw", speaker_id + ".wav")
    clips, total = [], 0.0
    with open(os.path.join(cv, "validated.tsv"), encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            if r["client_id"].startswith(speaker_id) and total < REF_SECONDS:
                clips.append(r)
                total += sf.info(os.path.join(cv, "clips", r["path"])).duration
    text = "，".join(r["sentence"] for r in clips) + "。"
    if not os.path.exists(out):
        os.makedirs(os.path.dirname(out), exist_ok=True)
        # A hard cut at the start of a clip gave noise at the start of the generated lines
        # (Loukakis, 2026-11-14). Each clip gets short fades, and the clips get gaps of silence.
        # -45 dB cut the soft last syllable of a clip (統一 became 統), and the model then said the missing
        # syllable at the start of each line (8176d3, 2026-11-15); -60 dB keeps it.
        trim = "silenceremove=start_periods=1:start_threshold=-60dB,areverse,silenceremove=start_periods=1:start_threshold=-60dB,areverse"
        fade = "afade=t=in:d=0.03,areverse,afade=t=in:d=0.03,areverse,apad=pad_dur=0.15"
        filt = "anullsrc=r=16000:cl=mono,atrim=0:0.15[lead];"
        filt += "".join(f"[{i}:a]{trim},aresample=16000,{fade}[a{i}];" for i in range(len(clips)))
        filt += "[lead]" + "".join(f"[a{i}]" for i in range(len(clips))) + f"concat=n={len(clips) + 1}:v=0:a=1"
        cmd = ["ffmpeg", "-loglevel", "error", "-y"] + sum([["-i", os.path.join(cv, "clips", r["path"])] for r in clips], [])
        subprocess.run(cmd + ["-filter_complex", filt, "-ac", "1", out], check=True)
    return out, text


def main(model_dir, lines_csv, work, cv, voice_out, *only):
    sys.path[:0] = [".", "third_party/Matcha-TTS"]  # python -I leaves the checkout off sys.path
    from cosyvoice.cli.cosyvoice import AutoModel

    # The first row of a file name wins, for its folder, length and English alike.
    folder_of, seconds, english = {}, {}, {}
    for name in sorted(os.listdir(work)):
        if name.endswith(".en.csv"):
            with open(os.path.join(work, name), encoding="utf-8") as f:
                for e in csv.DictReader(f):
                    key = e["wav"].lower()
                    folder_of.setdefault(key, e["folder"])
                    seconds.setdefault(key, e["seconds"])
                    english.setdefault(key, e["en"])
    rows = [r for r in csv.DictReader(open(lines_csv, encoding="utf-8"))
            if r["speaker"] in SPEAKER and r["wav"] not in RETAIL_VOICE and (not only or r["wav"] in only)]
    refs = {s: reference(work, cv, i) for s, i in SPEAKER.items() if any(r["speaker"] == s for r in rows)}
    model = AutoModel(model_dir=model_dir)
    t0, done = time.time(), set()
    for r in rows:
        base = r["wav"][:-4]
        # messages.tbl gives some files two texts; the first row is the one the retail file says
        if base in done:
            continue
        done.add(base)
        folder = os.path.join(voice_out, folder_of[r["wav"].lower()])
        os.makedirs(folder, exist_ok=True)
        ref, text = refs[r["speaker"]]
        # The Vasudans speak through a machine translator, which does not cry out; a cry also hid the
        # female reference voice (7_Death, 2026-11-15).
        style = None if r["speaker"] in VASUDAN else style_of(r["wav"])
        if style:
            parts = [x["tts_speech"] for x in model.inference_instruct2(
                tts_text(r["zh_tw"]), "You are a helpful assistant. " + style + "<|endofprompt|>", ref, stream=False)]
        else:
            parts = [x["tts_speech"] for x in model.inference_zero_shot(
                tts_text(r["zh_tw"]), "You are a helpful assistant.<|endofprompt|>" + t2s.convert(text), ref, stream=False)]
        audio = torch.cat(parts, dim=1).squeeze(0).numpy()
        out = os.path.join(folder, base + "-tw.ogg")
        if r["speaker"] in VASUDAN:
            vref = os.path.join(work, "voice", VASUDAN_VOICE)
            for attempt in range(3):
                # A very short output can fail in the vocoder ("Kernel size can't be greater than actual input
                # size", 6_praise, 2026-11-15); a new sample usually works.
                try:
                    vparts = [x["tts_speech"] for x in model.inference_zero_shot(
                        vasudan_text(english[r["wav"].lower()], base),
                        "You are a helpful assistant.<|endofprompt|>" + english[VASUDAN_VOICE.lower()], vref, stream=False)]
                    vasudan = torch.cat(vparts, dim=1).squeeze(0).numpy()  # no output at all raises here too
                    break
                except RuntimeError:
                    if attempt == 2:
                        raise
            # Both voices are kept, so that a change of the mix does not need the model again.
            keep = os.path.join(work, "vasudan-tw")
            os.makedirs(keep, exist_ok=True)
            sf.write(os.path.join(keep, base + "-zh.wav"), audio, model.sample_rate)
            sf.write(os.path.join(keep, base + "-vasudan.wav"), vasudan, model.sample_rate)
            vasudan_mix(audio, vasudan, model.sample_rate, out)
        else:
            sf.write(out, audio, model.sample_rate, format="OGG", subtype="VORBIS")
        print(f"{base}: {len(audio) / model.sample_rate:.1f} s (English {seconds.get(r['wav'].lower(), '?')} s)", flush=True)
    print("seconds:", round(time.time() - t0, 1), "max VRAM GB:", round(torch.cuda.max_memory_allocated() / 2**30, 2))


if __name__ == "__main__":
    main(*sys.argv[1:])
