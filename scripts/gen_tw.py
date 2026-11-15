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
import csv, os, re, subprocess, sys, time
import soundfile as sf, torch
from opencc import OpenCC

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vasudan import VASUDAN, VASUDAN_VOICE, vasudan_mix, vasudan_text  # noqa: E402

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

# The Vasudan layer and its mix are shared with gen_cn.py (vasudan.py).
# The translator is a Taiwan speaker made to sound like a speech synthesizer of the 2000s: telephone band,
# 8 kHz and 6 bits, and a 70 Hz modulation for a metallic tone. The built-in CosyVoice voices had a mainland
# accent; the project owner chose this "strong" version from three (2026-11-15).
TRANSLATOR_EFFECT = ("highpass=f=300,lowpass=f=3400,aresample=8000,acrusher=bits=6:mode=lin:mix=0.7,"
                     "aresample={sr},aeval=val(0)*(0.55+0.45*sin(2*PI*70*t)):c=same,volume=1.6")

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
            vasudan_mix(audio, vasudan, model.sample_rate, out, TRANSLATOR_EFFECT)
        else:
            sf.write(out, audio, model.sample_rate, format="OGG", subtype="VORBIS")
        print(f"{base}: {len(audio) / model.sample_rate:.1f} s (English {seconds.get(r['wav'].lower(), '?')} s)", flush=True)
    print("seconds:", round(time.time() - t0, 1), "max VRAM GB:", round(torch.cuda.max_memory_allocated() / 2**30, 2))


if __name__ == "__main__":
    main(*sys.argv[1:])
