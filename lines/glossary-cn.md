# Glossary (zh-CN)

Draft terms for the Mandarin voice lines. Keep one term for one name in all missions.

Military register: in the main campaign, use the military terms of the target language (for zh-CN, the terms of the PLA and mainland military aviation), so that the lines give the military mood that the players want. The exception is a character who is not a professional pilot, or a civilian pilot: that character uses everyday words.
A star takes its popular Chinese name when it has one (Vega is 织女星), else its traditional Chinese star name (Capella is 五车二). Do not use a transliteration of the Western name.

| English | zh-CN | Note |
|---|---|---|
| 53rd Hammerheads | 第五十三锤头鲨中队 | Short form 第五十三中队 |
| Lieutenant Loukakis | 卢卡基斯上尉 | |
| Vega | 织女星 | Popular name (traditional name 织女一) |
| Capella | 五车二 | Traditional star name |
| Sol system | 太阳系 | |
| Myrmidon | 密尔米顿 | Fighter |
| GTF Ulysses | GTF 尤利西斯 | Prefix kept in Latin letters |
| GTD Bastion | GTD 堡垒号 | |
| SD Lucifer | SD 路西法号 | |
| GTD Aquitaine | GTD 阿基坦号 | |
| Hecate | 赫卡忒级 | Destroyer class |
| Terran-Vasudan | 人类与瓦苏丹 | |
| Great War | 大战 | |
| Subach HL-7 | 苏巴赫 HL-7 | Laser |
| Tempest | 风暴 | Dumb-fire rocket |
| Rockeye | 石眼 | Heat-seeking missile; mainland name of the real Mk 20 Rockeye |
| HUD | 平显 | Short form of 平视显示器, the mainland aviation term |
| afterburner | 加力 | Spoken form of 加力燃烧室 |
| Drone 01 | 一号靶机 | |
| subspace drive | 亚空间发动机 | |
| tech room | 技术室 | |
| space superiority fighter, squadron | 制天战斗机, 制天中队 | After 制空 (air superiority). Not checked: whether PLA texts use 制天权 |
| jump node | 跳跃节点 | |
| Command | 司令部 | |
| 3rd Fleet, 4th Fleet | 第三舰队, 第四舰队 | |
| Terran | 人类 | |
| squadron leader | 中队长 | |
| GTVA | GTVA | Latin letters |
| training simulator module, TSM | 训练模拟器课程, TSM | Spoken as TSM 一零三C |
| target view | 目标窗口 | |
| target box (brackets) | 目标框 | |
| reticle | 准星 | |
| offscreen indicator | 屏幕外指示器 | |
| match speed | 同步速度 | |
| primary weapon | 主武器 | |
| dumb-fire | 无制导 | |
| heat-seeking | 热追踪 | |
| hull integrity | 舰体完整度 | For any ship, also a fighter |
| engine | 发动机 | Mainland aviation term, not 引擎 |
| wing (Alpha, Beta, Gamma, Delta, Epsilon) | 编队 (阿尔法, 贝塔, 伽马, 德尔塔, 艾普西隆) | Beta wing is 贝塔编队. Greek letters are transliterated |
| sir | 长官 | |
| pilot (as an address) | 飞行员 | |
| Terran (Vasudan speech to the player) | 人类 | Personas 6 and 7 |
| Roger that, I copy, Acknowledged | 收到 | Affirmative is 明白 |
| Negative | 否定 | |
| By your command | 遵命 (persona 6), 谨遵您的命令 (persona 7) | |
| bandit, hostiles | 敌机 | |
| reinforcements | 增援 | |
| on station, in position | 就位 | |
| standing by | 待命 | |
| check six, on your six | 注意后方, 六点钟 | |
| evasive action | 规避 | |
| break (to attack) | 脱离队形 | |
| return to base | 返航 | |
| support ship | 支援舰 | |
| rearm | 补充弹药 | |
| secondary weapon, secondary banks | 副武器 | |
| ordnance | 弹药 | |
| subsystem | 子系统 | |
| disable (a ship) | 瘫痪 | Disable: shoot the engines |
| disarm (a ship) | 解除武装 | Disarm: shoot the weapons |
| IFF | 敌我识别, 敌我识别器 | |
| jump signature | 跃迁信号 | |
| jump drive | 亚空间发动机 | Same as subspace drive |
| hull failure | 舰体解体 | |
| AWACS | 预警机 | Mainland short form of 空中预警机 |
| fighter cover | 战斗机掩护 | |
| Mayday | 求救 | Not checked: a PLA pilot can say Mayday |
| court martial | 军事法庭 | |
| traitor | 叛徒 | |
| Emperor | 皇帝 | |

## Names

The pattern of Chinese game localizations (EVE Online, Star Citizen, Star Wars: Squadrons, Stellaris, 无尽的拉格朗日):

- A name made of a common word is translated by meaning: Hammerheads is 锤头鲨, Bastion is 堡垒号.
- A name from myth, a person or a place is transliterated: Myrmidon is 密尔米顿, Lucifer is 路西法号, Aquitaine is 阿基坦号.
- A class takes 级 (赫卡忒级), one ship takes 号 (堡垒号). A model code and its letters stay in Latin letters (GTF, GTD, SD).

The HUD shows ship class names from `ships.tbl`. The text mod (planned) will translate `ships.tbl` with this glossary, so that the voice and the HUD use the same names. A player with only the voice mod sees the English names on the HUD.

## Spoken text

The zh_cn column is the text that the TTS model speaks, so it is written as it is spoken:

- Numbers are Chinese numerals: 第五十三, 三十六小时, 一百二十五米, 两百米. A year is read digit by digit: 二三三五年.
- A code is spoken as the English voice says it: TSM-103c is TSM 一零三C, HL-7 is HL七. No hyphen, because a TTS model can read it as 减 or 杠.
- A class name takes 级 (赫卡忒级), a ship name takes 号 (堡垒号), a fighter type takes neither (密尔米顿).

To fix the reading of a polyphonic character, mark its pinyin with the IndexTTS-2.5 syntax `<字|PINYIN>`, for example `<重|CHONG2>玩`. The text mod (planned) will remove the marks. Valid pinyin is in `checkpoints/pinyin.vocab` of IndexTTS.

Known misreadings, left as they are: IndexTTS sometimes says 堡垒号 as 堡里号 (Training 1, 2026-11-14).

Fixed with a mark: IndexTTS reads 伽马 as jiā mǎ (the ASR heard 加码). The mainland reading is gā mǎ, so write `<伽|GA1>马` (messages, 2026-11-15).

## Ranks

FreeSpace 2 uses US Navy officer ranks (the retail list in fs2open `code/stats/scoring.cpp`, debug command `rank`). The Chinese names follow zh.wikipedia 美国海军军官军衔 (zh-cn).

| English | zh-CN | Note |
|---|---|---|
| Ensign | 少尉 | O-1 |
| Lieutenant Junior Grade | 中尉 | O-2 |
| Lieutenant | 上尉 | O-3 |
| Lieutenant Commander | 少校 | O-4 |
| Commander | 中校 | O-5 |
| Captain | 上校 | O-6 |
| Commodore | 准将 | Not in the source table; 准将 is the rank of the same grade |
| Rear Admiral | 少将 | O-8 |
| Vice Admiral | 中将 | O-9 |
| Admiral | 上将 | O-10 |

instructor: 教员. Recent reports (2023-2026: 解放军报, 央视, 中国航空报) use 教员 for the post of a flight instructor. 教官 also occurs, mostly as a title for a named person, and for a drill instructor.
