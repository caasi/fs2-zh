# Voices for the tw mod

The tw (Taiwan Mandarin) voice files are made with CosyVoice 3 (Fun-CosyVoice3-0.5B-2512, Apache-2.0), with Taiwan Mandarin reference voices from Common Voice. In the first version, the Taiwan accent comes first, and there is no emotion control.

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

New speakers come with the campaign. The first mission (`SM1-01.fs2`) needs more voices, for example a ship captain. Select them with the same steps when that mission is voiced.
