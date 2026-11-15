"""Make the zh-CN voice files of one mission with IndexTTS-2.5.

usage (from the index-tts checkout, which holds checkpoints/):
  .venv/bin/python <repo>/scripts/gen_cn.py <lines.csv> <work dir> <mod data/voice dir> [wav ...]

<work dir> holds the output of extract_en.py: the retail voice files in voice/,
and <file>.en.csv with the folder and the English length of each line. Each line copies the timbre of its speaker's
reference line and the emotion of its own original line. Output is
<name>-cn.ogg in the voice folder that the engine reads for that prefix.
"""
import csv, os, sys, time
import numpy as np, soundfile as sf, torch
from indextts.infer_v2_5 import IndexTTS2

# One long, calm line per speaker gives a steadier timbre than a 1 s line such as "Good job."
# The messages.tbl speakers were chosen without listening: among the longest files of the speaker,
# the one with a calm text (not a shout) and a steady level (low spread of the 50 ms RMS).
SPEAKER_REF = {"loukakis": "TR1_CB_01.wav", "briefing": "TR1_MB_01.wav", "instructor": "DTM_IN_01.wav",
               "terran_command": "TC_strayfinal.wav", "persona1": "1_backup.wav", "persona2": "2_Stray.wav",
               "persona3": "3_Delta.wav", "persona4": "4_no.wav", "persona5": "5_Disarm.wav",
               "persona6": "6_backup.wav", "persona7": "7_backup.wav", "support": "S_onway.wav",
               "vasudan_support": "VS_onway2.wav", "awacs": "Awacs75.wav", "vasudan_awacs": "Vawacs25.wav"}



def tts_text(zh):
    # In IndexTTS-2.5 output the pause at "，" sounds longer than the pause at "。", so "马上，长官。" sounds
    # broken in two (user listening test, 2026-11-15). The subtitle text keeps the comma; only the TTS input drops it.
    return zh.replace("，长官", "长官")


# A cry with no words keeps the retail voice: the engine plays <name>.wav when <name>-cn.ogg does not exist.
RETAIL_VOICE = {"2_Death.wav"}


def tail_drop_db(d, sr):
    """How far the last 60 ms is below the loudest 20 ms frame, in dB."""
    d = d if d.ndim == 1 else d.mean(axis=1)
    h = int(sr * 0.02)
    db = 20 * np.log10(np.sqrt(np.mean(d[: len(d) // h * h].reshape(-1, h) ** 2, axis=1)) + 1e-9)
    return db.max() - db[-3:].mean()


# IndexTTS can sample the stop token too early, so a line ends in the middle of a word
# (index-tts#247, #488, #523, #633). Ten retail lines that were checked end 14 dB or more below their
# peak; a cut line ends within a few dB of it. Sampling is random, so a new try usually ends correctly.
# A short shout can end loud and still be whole (1_Death "不要！" ends 2 dB down), so CUT asks for a listen.
MIN_TAIL_DROP_DB, TRIES = 15, 4

lines_csv, work, voice_out, *only = sys.argv[1:]
orig = os.path.join(work, "voice")
seconds, folder_of = {}, {}
for en_csv in os.listdir(work):
    if en_csv.endswith(".en.csv"):
        for e in csv.DictReader(open(os.path.join(work, en_csv), encoding="utf-8")):
            seconds[e["wav"].lower()], folder_of[e["wav"].lower()] = e["seconds"], e["folder"]
rows = [r for r in csv.DictReader(open(lines_csv, encoding="utf-8")) if not only or r["wav"] in only]
tts = IndexTTS2(cfg_path="checkpoints/config.yaml", model_dir="checkpoints", use_bf16=True)
t0, done = time.time(), set()
for r in rows:
    base = r["wav"][:-4]
    # messages.tbl gives some files two texts; the first row is the one the retail file says
    if base in done or r["wav"] in RETAIL_VOICE:
        continue
    done.add(base)
    folder = os.path.join(voice_out, folder_of[r["wav"].lower()])  # the folder of the retail file
    os.makedirs(folder, exist_ok=True)
    tmp = os.path.join(folder, base + "-cn.tmp.wav")
    best = None
    for attempt in range(TRIES):
        tts.infer(spk_audio_prompt=os.path.join(orig, SPEAKER_REF[r["speaker"]]), emo_audio_prompt=os.path.join(orig, r["wav"]),
                  text=tts_text(r["zh_cn"]), lang="ZH", output_path=tmp, use_random=False)
        d, sr = sf.read(tmp)
        drop = tail_drop_db(d, sr)
        if best is None or drop > best[0]:
            best = (drop, d)
        if drop >= MIN_TAIL_DROP_DB:
            break
    drop, d = best
    sf.write(os.path.join(folder, base + "-cn.ogg"), d, sr, format="OGG", subtype="VORBIS")
    os.remove(tmp)
    cut = "" if drop >= MIN_TAIL_DROP_DB else ", CUT"
    print(f"{base}: {len(d) / sr:.1f} s (English {seconds.get(r['wav'].lower(), '?')} s), tail -{drop:.0f} dB, {attempt + 1} tries{cut}", flush=True)
print("seconds:", round(time.time() - t0, 1), "max VRAM GB:", round(torch.cuda.max_memory_allocated() / 2**30, 2))
