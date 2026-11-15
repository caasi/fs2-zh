# fs2-zh

Chinese voice mods for FreeSpace 2. Text mods come later. The mods need FreeSpace Open with the voice language option of [fs2open PR #1](https://github.com/caasi/fs2open.github.com/pull/1). A release build of FreeSpace Open does not have this option yet.

Each language variant is a separate Knossos mod:

| Folder | Mod | Language |
|---|---|---|
| `mods/cn` | `fs2-zh-voice-cn` | Mandarin, mainland China (Simplified script in the line files) |

The tw (Taiwan Mandarin) and hk (Cantonese) voice mods come later, each in its own folder.

Status: work in progress. Training 1 and the built-in messages (`messages.tbl`: wingmen, Terran Command, support ships, AWACS) have Chinese voice lines. The repo does not contain the voice files. To use the mod, make the voice files with the steps below.

## Files

- `lines/<mission>.csv`: the voice lines of one mission. `lines/messages.csv`: the built-in messages of `messages.tbl`, which all missions share. `zh_cn` is the text that the TTS model speaks, so numbers and codes are written as they are spoken.
- `lines/glossary-cn.md`: zh-CN terms, ranks and rules. `lines/glossary-tw.md`: zh-TW terms of the ROC Armed Forces. `lines/aviation-terms.md`: mainland and Taiwan aviation terms.
- `mods/cn`, `mods/tw`: the Knossos mods. `data/tables/zh-cn-lcl.tbm` adds the language `Chinese (CN)`, and `zh-tw-lcl.tbm` adds `Chinese (TW)`. Each table has its own file name, so that the engine reads both when both mods are on.
- `scripts/vpx.py`: reads a retail `.vp` archive.
- `scripts/extract_en.py`: writes the English lines, their lengths and the retail voice files of one mission to `work/`.
- `scripts/gen_cn.py`: makes the cn voice files with IndexTTS-2.5.
- `scripts/gen_tw.py`: makes the tw voice files with CosyVoice 3. `scripts/test_gen_tw.py` checks the text it gives to the model.
- `scripts/match_loudness.py`: sets the loudness of each generated file to the loudness of its retail line.

The English text, the retail voice files and the generated `.ogg` files are not in git.

## Make the voice files

You need:

- A retail copy of FreeSpace 2 (the folder with the `.vp` files).
- `python3`, `ffmpeg` and `ffprobe`.
- A checkout of [IndexTTS](https://github.com/index-tts/index-tts) with the IndexTTS-2.5 checkpoints, and an NVIDIA GPU with CUDA.

Do these steps from the root of this repo:

```bash
python3 -I scripts/extract_en.py <FS2 folder> Training-1.fs2 "$PWD/work"
python3 -I scripts/extract_en.py <FS2 folder> messages.tbl "$PWD/work"
cd <index-tts checkout>
.venv/bin/python <this repo>/scripts/gen_cn.py <this repo>/lines/training-1.csv <this repo>/work <this repo>/mods/cn/data/voice
.venv/bin/python <this repo>/scripts/gen_cn.py <this repo>/lines/messages.csv <this repo>/work <this repo>/mods/cn/data/voice
```

If `gen_cn.py` prints `CUT` for a line, listen to it: the line can end in the middle of a word. Give the file name as the last argument to make it again.

Then set the loudness of the new files to the loudness of the retail lines. The TTS models do not do this: the cn output was 0 to 5 dB above the retail lines, and the tw output was 6 to 18 dB below them.

```bash
python3 -I <this repo>/scripts/match_loudness.py <this repo>/work <this repo>/mods/cn/data/voice cn
```

## Install the mod in Knossos

1. Make a link to `mods/cn` in the Knossos library: `<library>/FreespaceOpen/fs2-zh-voice-cn/fs2-zh-voice-cn-0.1.0`.
2. Start Knossos again. The mod "FS2 Chinese Voice (CN)" shows in the list.
3. Set the FSO build of the mod to a build with the voice language option.
4. Play the mod. In the game, open the options (F2), then the in-game options (F3). Set Audio, Voice Language to `Chinese (CN)`.

## How each variant is voiced

- **cn**: IndexTTS-2.5. Each line copies the timbre of its speaker's reference line and the emotion of its own original line. The exceptions are in `scripts/gen_cn.py`: `EMO_REF` gives a line another emotion reference, and `RETAIL_VOICE` lines keep the retail voice.
- **tw** (first version): CosyVoice 3, with Taiwan Mandarin reference voices from Common Voice, and the line in Simplified script as the input. The Taiwan accent comes first, so there is no emotion control. See `docs/voices-tw.md`.

## License

- Code (`scripts/`): MIT, see `LICENSE`.
- The Chinese lines, the glossaries and the mod files (`lines/`, `mods/`): [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). The license covers only the work of this project.
- The Chinese lines are translations of the FreeSpace 2 script. The rights in the original script belong to the owners of FreeSpace 2.
- The generated voice files are made with the retail voice files of FreeSpace 2 as the reference. The IndexTTS model has its own license: [LICENSE](https://github.com/index-tts/index-tts/blob/main/LICENSE). This repo does not distribute voice files.
- The values for German, French and Polish in the `*-lcl.tbm` tables are the built-in values of FreeSpace Open.
- The quotes from dictionaries and news in `lines/glossary-tw.md` and `lines/aviation-terms.md` keep the rights of their owners.
- Not covered: the English text and the retail voice files that the scripts read into `work/`. The mods need a retail copy of FreeSpace 2 and contain none of its files.
