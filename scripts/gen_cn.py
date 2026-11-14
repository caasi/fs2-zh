"""Make the zh-CN voice files of one mission with IndexTTS-2.5.

usage (from the index-tts checkout, which holds checkpoints/):
  .venv/bin/python <repo>/scripts/gen_cn.py <lines.csv> <work dir> <mod data/voice dir> [wav ...]

<work dir> holds the output of extract_en.py: the retail voice files in voice/,
and <file>.en.csv with the folder and the English length of each line. Each line copies the timbre of its speaker's
reference line and the emotion of its own original line. Output is
<name>-cn.ogg in the voice folder that the engine reads for that prefix.
"""
import csv, os, sys, time
import soundfile as sf, torch
from indextts.infer_v2_5 import IndexTTS2

# One long, calm line per speaker gives a steadier timbre than a 1 s line such as "Good job."
SPEAKER_REF = {"loukakis": "TR1_CB_01.wav", "briefing": "TR1_MB_01.wav", "instructor": "DTM_IN_01.wav",
               "terran_command": "TC_Oops2.wav"}

lines_csv, work, voice_out, *only = sys.argv[1:]
orig = os.path.join(work, "voice")
seconds, folder_of = {}, {}
for en_csv in os.listdir(work):
    if en_csv.endswith(".en.csv"):
        for e in csv.DictReader(open(os.path.join(work, en_csv), encoding="utf-8")):
            seconds[e["wav"].lower()], folder_of[e["wav"].lower()] = e["seconds"], e["folder"]
rows = [r for r in csv.DictReader(open(lines_csv, encoding="utf-8")) if not only or r["wav"] in only]
tts = IndexTTS2(cfg_path="checkpoints/config.yaml", model_dir="checkpoints", use_bf16=True)
t0 = time.time()
for r in rows:
    base = r["wav"][:-4]
    folder = os.path.join(voice_out, folder_of[r["wav"].lower()])  # the folder of the retail file
    os.makedirs(folder, exist_ok=True)
    tmp = os.path.join(folder, base + "-cn.tmp.wav")
    tts.infer(spk_audio_prompt=os.path.join(orig, SPEAKER_REF[r["speaker"]]), emo_audio_prompt=os.path.join(orig, r["wav"]),
              text=r["zh_cn"], lang="ZH", output_path=tmp, use_random=False)
    d, sr = sf.read(tmp)
    sf.write(os.path.join(folder, base + "-cn.ogg"), d, sr, format="OGG", subtype="VORBIS")
    os.remove(tmp)
    print(f"{base}: {len(d) / sr:.1f} s (English {seconds.get(r['wav'].lower(), '?')} s)", flush=True)
print("seconds:", round(time.time() - t0, 1), "max VRAM GB:", round(torch.cuda.max_memory_allocated() / 2**30, 2))
