"""Checks of the text that gen_tw.py gives to CosyVoice.  Run: python -I scripts/test_gen_tw.py (needs opencc)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_tw as g

assert g.pinyin_mark("ㄗㄞ3") == "[z][ǎi]"
assert g.pinyin_mark("ㄔㄨㄥ2") == "[ch][óng]"
assert g.pinyin_mark("ㄐㄧ3") == "[j][ǐ]"
assert g.pinyin_mark("ㄉㄧㄡ1") == "[d][iū]"
assert g.tts_text("請選擇重[:ㄔㄨㄥ2]玩任務選項。") == "请选择[ch][óng]玩任务选项。"
try:  # the model drops a neutral-tone syllable (DTM_IN_24, 2026-11-15), so the mark is refused
    g.pinyin_mark("ㄓㄜ5")
    raise AssertionError("a neutral-tone mark must be refused")
except ValueError:
    pass
print("ok")
