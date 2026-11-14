# fs2-zh

Chinese voice (and later text) mods for FreeSpace 2, for FreeSpace Open with the voice language option (fs2open PR #1). Each variant is a separate Knossos mod:

| Folder | Mod | Language |
|---|---|---|
| `mods/cn` | `fs2-zh-voice-cn` | Mandarin, mainland (Simplified script in the line files) |

The tw (Taiwan Mandarin) and hk (Cantonese) voice mods and the text mods come later, each in its own folder.

## Files

- `lines/<mission>.csv`: the voice lines of one mission. `zh_cn` is the text that the TTS model speaks, so numbers and codes are written as they are spoken. The English text is not in git: `scripts/extract_en.py` reads it from your retail FreeSpace 2.
- `lines/glossary.md`: zh-CN terms, ranks and rules. `lines/aviation-terms.md`: mainland and Taiwan aviation terms.
- `scripts/vpx.py`: extracts files from a retail `.vp` archive.
- `scripts/extract_en.py`: writes the English lines and the retail voice files of one mission to `work/` (not in git).
- `scripts/gen_cn.py`: makes the cn voice files with IndexTTS-2.5.

To make the voice files of a mission:

```bash
python3 -I scripts/extract_en.py <FS2 folder with the .vp files> Training-1.fs2 work
cd <index-tts checkout>
.venv/bin/python <this repo>/scripts/gen_cn.py <this repo>/lines/training-1.csv <this repo>/work <this repo>/mods/cn/data/voice
```

The generated `.ogg` files are not in git.

## How each variant is voiced

- **cn**: IndexTTS-2.5. Each line copies the timbre of its speaker's reference line and the emotion of its own original line.
- **tw** (first version): the Taiwan accent comes first, so there is no emotion control. Copy the timbre of the original voice if the model can. If it cannot, use a default voice of the same sex as the speaker.

## License

- Code (`scripts/`): MIT, see `LICENSE`.
- Translations, glossaries, mod tables and the generated voice files: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
- Not covered: the English text and the retail voice files that the scripts read into `work/`. They belong to the owners of FreeSpace 2. The mods need a retail copy of FreeSpace 2 and contain none of its files.
