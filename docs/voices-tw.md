# Voices for the tw mod

The tw (Taiwan Mandarin) voice files are made with CosyVoice 3 (Fun-CosyVoice3-0.5B-2512, Apache-2.0), with Taiwan Mandarin reference voices from Common Voice. In the first version (Training 1), the Taiwan accent came first, and there was no emotion control. The built-in messages use the instruct mode of CosyVoice for one style: a frightened cry for the `_Death` lines of human pilots (`STYLE` in `scripts/gen_tw.py`).

## Why the original voices are not copied

A test on 2026-11-14 used the retail English voice files as the BreezyVoice reference. The Mandarin output had the timbre of the original speakers, but it also had English prosody and vowels: it sounded like a Taiwanese American. The speech recognizer heard English words in it ("And by Ned", "Meermi"). For this reason, the tw mod uses Taiwan Mandarin reference voices from Common Voice.

The built-in BreezyVoice speaker `中文男` was also tested. It spoke too slowly: 30.5 s for a line that is 18.2 s in English.

## Why CosyVoice 3

On 2026-11-14 the project owner compared the same four lines (TR1_CB_04, TR1_MB_01, DTM_IN_19, DTM_IN_29), made with the same three Common Voice reference voices, at the loudness of the retail lines:

| Model | Result |
|---|---|
| BreezyVoice (MediaTek, Apache-2.0) | Taiwan accent, but less clear and slow |
| IndexTTS-2.5 | Clear, but a mainland accent appears |
| CosyVoice 3, Traditional script input | Less fluent |
| CosyVoice 3, Simplified script input | The best: more fluent than BreezyVoice, with the Taiwan accent of the reference |
| BlueMagpie-TTS (OpenFormosa), reference clip and speaker vector | Reference clip is better than speaker vector, but not as good as CosyVoice 3. Its weights do not allow the distribution of generated speech, so it was a reference only |

So `scripts/gen_tw.py` converts each line to Simplified script (OpenCC `t2s`) before CosyVoice reads it. The line in the CSV stays in Traditional script. A bopomofo mark `字[:ㄗㄞ3]` in the CSV becomes the CosyVoice pinyin mark `[z][ǎi]`.

## The source of the reference voices

- Dataset: [Common Voice Scripted Speech 27.0 - Chinese (Taiwan)](https://mozilladatacollective.com/datasets/cmu5wkw5i00c6o107jnm3t51u), released 2026-09-17 on the Mozilla Data Collective.
- License: [CC0 1.0](https://spdx.org/licenses/CC0-1.0.html).
- Forbidden usages of the dataset, word for word: "It is forbidden to attempt to determine the identity of speakers in the Common Voice datasets. It is forbidden to re-host or re-share this dataset."

This project obeys both rules:

- The speakers are selected only by the dataset metadata and by listening. No attempt is made to find out who they are.
- The dataset and its clips are not in this repo and are not distributed. Only the generated voice files use the reference voices.

The generated tw voice files are synthetic speech. Their speaker references come from Common Voice. The mod description and this repo say so.

## The roles

The three speakers of Training 1 are male in the retail game. The median pitch of each speaker was measured on the retail voice files.

| Role | Retail pitch | Reference voice |
|---|---|---|
| Loukakis (squadron leader, Lieutenant) | about 105 Hz | Thirties to forties. Low voice. Calm and warm. |
| Briefing and debriefing (Command) | about 103 Hz | Forties to fifties. Low voice. Clear, formal, like a news reader. |
| Instructor | 116 to 125 Hz | Twenties to thirties. A brighter voice. Short, firm sentences. |

The three voices must be different in pitch and age, so that the player can tell who speaks.

## How the candidates are selected

The speed of BreezyVoice output follows the speed of the reference voice. A test on 2026-11-12 measured this:

| Reference voice | Characters per second | Output, characters per second |
|---|---|---|
| BreezyVoice `example.wav` (female) | 3.8 | 2.6 |
| VoxCPM2 reference voice | 4.7 | 4.9 |

Thus a fast reference voice is necessary. The selection has three steps:

1. Filter by the metadata: gender `male_masculine`, a place of birth in Taiwan (the `accents` field, for example `出生地：臺北市`), and the age group of the role.
2. Filter by measurement:
   - Speed: 4.5 characters per second or more.
   - Sound quality: a high signal-to-noise ratio, no echo.
   - Length: a clean clip of 10 to 20 s.
   - Pitch: near the retail pitch of the role.
3. Select by ear: each role gets 3 to 5 candidates. For each candidate, the listener hears the Common Voice clip and one game line made with it.

Common Voice clips are read aloud by volunteers. Few of them sound military. The selection therefore looks at the voice (pitch, age, speed, clarity). The lines and the generation give the military register.

## Selected voices

The candidates were heard by the project owner on 2026-11-14. The first four candidates for Loukakis were in their thirties and sounded too young, not calm enough for a military officer. The second four were in their forties, with a lower pitch. The ids are the first 10 characters of the Common Voice `client_id`, so that the generation can be done again. They are not used to identify anyone.

| Role | Common Voice speaker | Age group | Place of birth | Speech rate | Pitch |
|---|---|---|---|---|---|
| Briefing and debriefing | `47f5d1a312` | fourties | 花蓮縣 | 4.4 characters per second | about 97 Hz |
| Instructor | `49460f8c97` | twenties | 宜蘭縣 | 5.2 characters per second | about 130 Hz |
| Loukakis | `d070d9ecfc` | fourties | 新竹市 | 5.4 characters per second | about 84 Hz |

### The messages.tbl speakers

The 207 built-in messages (wingmen, Terran Command, support ships, AWACS) have 12 speakers. The project owner picked the voices on 2026-11-15 from 42 candidates, by the same steps as above, with two changes:

- The speech rate was measured on the clip length in `clip_durations.tsv`, which includes the silence around each sentence. On that scale the three Training 1 voices measure 2.1 to 3.1 characters per second, so the cut was 2.3.
- The project owner imagines the wingmen as young pilots, in their twenties.

| Speaker | Common Voice speaker | Age group | Place of birth | Pitch |
|---|---|---|---|---|
| persona1 | `557ebe984b` | twenties | 臺中市 | about 162 Hz |
| persona2 | `7296001402` | twenties | 臺中市 | about 216 Hz |
| persona3 | `7af1af1921` | twenties | 桃園市 | about 108 Hz |
| persona4 | `dee6c34e84` | twenties | 新北市 | about 102 Hz |
| persona5 | `ce175bd795` | twenties | 臺北市 | about 159 Hz |
| support | `9076596318` | thirties | 臺北市 | about 121 Hz |
| awacs | `c1a8a2007f` | thirties | 臺北市 | about 171 Hz |
| terran_command | `47f5d1a312` (the briefing voice) | fourties | 花蓮縣 | about 97 Hz |

The pitch is the median of four clips (librosa pYIN). persona2 is female in the tw mod.

The Vasudans speak through a machine translator. The tw mod gives the translator one male and one female voice, so persona6, vasudan_support and vasudan_awacs share one voice. The translator voices are Taiwan speakers, `b7e8c8f4be` for the male speakers and `4be53f68d4` for persona7, with an effect that makes them sound like a speech synthesizer of the 2000s (`TRANSLATOR_EFFECT` in `scripts/gen_tw.py`). The built-in CosyVoice voices 中文男 and 中文女 were tried first, but they have a mainland accent. A speaker-embedding comparison of the retail files (3D-Speaker CAM++) points the same way: persona6, vasudan_support and vasudan_awacs have a cosine similarity of 0.79 to 0.88 to each other, against 0.4 to 0.6 for most pairs of different speakers. The human support ship and AWACS have 0.45, so the retail game seems to use two actors for them.

The Vasudan layer under the translator is made up: about one word for every two English words of the line (at least three), built from the word parts of the Hard Light Productions Vasudan reference, read in the timbre of the retail line `6_backup.wav`, then 0.8 times lower in pitch and with an echo. The translator starts 0.5 s after the layer, and the layer ends at least 0.6 s before the end of the translator: a layer that is too long is made up to 1.25 times faster, then cut at a pause. `gen_tw.py` keeps both voices of each line in `<work dir>/vasudan-tw/`, so that a change of the mix needs no new run of the model.

`TW_READINGS` in `gen_tw.py` gives CosyVoice the Taiwan reading of a character whose mainland reading differs (擊 jí, 識 shì). The glossary (`lines/glossary-tw.md`) lists the words.

Two Common Voice speakers were first selected for the translator: `b7e8c8f4be` (male, fourties, about 97 Hz) and `80b0f99831` (female, twenties, about 185 Hz). The project owner keeps `80b0f99831` for a named female pilot of the campaign.

New speakers come with the campaign. The first mission (`SM1-01.fs2`) needs more voices, for example a ship captain. Select them with the same steps when that mission is voiced.
