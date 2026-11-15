"""Checks of the text that gen_tw.py gives to CosyVoice.  Run: python -I scripts/test_gen_tw.py (needs opencc)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_tw as g

assert g.pinyin_mark("ㄗㄞ3") == "[z][ǎi]"
assert g.pinyin_mark("ㄔㄨㄥ2") == "[ch][óng]"
assert g.pinyin_mark("ㄐㄧ3") == "[j][ǐ]"
assert g.pinyin_mark("ㄉㄧㄡ1") == "[d][iū]"
assert g.tts_text("請選擇重[:ㄔㄨㄥ2]玩任務選項。") == "请选择[ch][óng]玩任务选项。"
# a character of TW_READINGS gets the Taiwan reading, also next to a hand mark
assert g.tts_text("攻擊目標。") == "攻[j][í]目标。"
assert g.tts_text("重[:ㄔㄨㄥ2]新攻擊") == "[ch][óng]新攻[j][í]"
try:  # the model drops a neutral-tone syllable (DTM_IN_24, 2026-11-15), so the mark is refused
    g.pinyin_mark("ㄓㄜ5")
    raise AssertionError("a neutral-tone mark must be refused")
except ValueError:
    pass
assert g.tts_text("敵我識別") == "敌我[sh][ì]别"
# the start is cut at the first sound, also when one loud sample comes before a quiet gap
import numpy as np
x = np.concatenate([[0.9], np.full(3999, 1e-4), np.full(8000, 0.3)]).astype("float32")
assert abs(len(g.lead_trim(x, 16000)) - (8000 + 320)) <= 160
# the last pause before the limit, not a later one
sr = 1000
y = np.concatenate([np.full(300, 0.3), np.zeros(100), np.full(300, 0.3), np.zeros(100), np.full(300, 0.3)]).astype("float32")
assert abs(g.last_pause(y, sr, 650) - 350) <= 20
assert 700 <= g.last_pause(y, sr, 760) < 760  # the part of a pause before the limit counts
assert g.last_pause(y, sr, 300) is None
# a layer that already fits is not changed
assert len(g.fit_vasudan(y, sr, 2000)) == len(y)
assert g.vasudan_text("Hold your fire now, wing pilot", "x").count(" ") == 2  # 6 English words, 3 made-up words
assert g.vasudan_text("Formidable!", "x").count(" ") == 2  # at least 3 made-up words
assert g.pinyin_mark("ㄐㄩ2") == "[j][ú]"  # ü is u after j, q, x
assert len(g.lead_trim(np.zeros(100, dtype="float32"), 24000)) == 100  # shorter than a frame: unchanged
assert g.last_pause(np.zeros(100, dtype="float32"), 24000, 50) is None
# a layer a little too long is only made faster; a much longer one is also cut, with a fade to silence
sr = 24000
tone = (0.3 * np.sin(np.arange(int(sr * 2.0)) * 2 * np.pi * 220 / sr)).astype("float32")
faster = g.fit_vasudan(tone, sr, int(sr * 1.8))
assert int(sr * 1.5) <= len(faster) <= int(sr * 1.8)
cut = g.fit_vasudan(tone, sr, int(sr * 1.0))
assert len(cut) <= int(sr * 1.0) and abs(float(cut[-1])) < 1e-3
# a pause in the first half is not used as the cut point
gap = tone.copy(); gap[int(sr * 0.2):int(sr * 0.3)] = 0
assert len(g.fit_vasudan(gap, sr, int(sr * 1.0))) > int(sr * 0.5)
print("ok")
