# Situation analysis experiment

All full runs use the same 100 approved cases. The dataset and its three targets per case were not changed.
Reranking is disabled in both new variants. No evaluation answers are used by production retrieval.

## Full generated-response results

| Variant | Hit | Precision | Recall | MRR | Generation local responses | Request errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Original baseline | 9.0% | 5.0% | 4.0% | 0.070 | 0 | 0 |
| Local changes only | 13.0% | 6.2% | 4.7% | 0.087 | 0 | 0 |
| Local changes + Bielik analysis | 42.0% | 19.3% | 17.3% | 0.243 | 0 | 0 |

These are exact-target agreement metrics, not an overall theological or safety score.
The full runs are single measurements and ran concurrently; latency comparisons are exploratory.

## Retrieval stages

| Variant | Hit in first 50 candidates | Hit among passages sent to generation | Analysis successes | Analysis fallbacks | Analysis time per case |
| --- | ---: | ---: | ---: | ---: | ---: |
| Local changes only | 15.0% | 14.0% | 0 | 0 | 0.00s |
| Local changes + Bielik analysis | 57.0% | 53.0% | 99 | 1 | 3.35s |

Short existing anchors are completed after ranking, which can increase whole-target coverage
between the candidate and selected stages. Numeric theme weights from analysis are ordered priors,
not model confidence estimates.

## Repeatability on the fixed exploratory subset

The 11-case subset is the same one used in the earlier diagnostic repetitions; it is not a held-out sample.
It includes cases already inspected during development. No statistical significance is claimed.

| Metric | Values across three runs | Mean | Sample standard deviation |
| --- | --- | ---: | ---: |
| hit | 0.545, 0.545, 0.545 | 0.545 | 0.000 |
| precision | 0.273, 0.273, 0.273 | 0.273 | 0.000 |
| recall | 0.242, 0.242, 0.242 | 0.242 | 0.000 |
| mrr | 0.288, 0.288, 0.288 | 0.288 | 0.000 |
| errors | 0.000, 0.000, 0.000 | 0.000 | 0.000 |
| local_extractive | 0.000, 0.000, 0.000 | 0.000 | 0.000 |

## Changed cases: local-only versus model-assisted retrieval

| Case | Situation | Hit before → after | References before | References after |
| --- | --- | --- | --- | --- |
| pl-002 | W naszej firmie zatrudnili kilku Ukraińców. Nie znam ich, ale od razu zakładam, że będą oszukiwać i kombinować. | 0 → 1 | Mateusza 5:37; Efezjan 4:25; Przysłów 12:17 | Łukasza 10:27; Kapłańska 19:33–34 |
| pl-003 | Dziadek opowiadał mi o krzywdach wojennych i teraz czuję niechęć do każdej osoby mówiącej po ukraińsku. | 0 → 1 | Wyjścia 3:7; Psalmów 142:6 | Łukasza 17:3–4; Kapłańska 19:33–34; Kolosan 3:13 |
| pl-004 | Sąsiadka z Ukrainy prosi mnie o pomoc z pismem. Nie chcę pomagać, bo uważam, że już za dużo od nas dostali. | 0 → 1 | Filipian 2:25; 2 Jana 1:12 | Łukasza 10:33–34; Jakuba 2:1–4; Kapłańska 19:33–34 |
| pl-005 | Nie przeszkadza mi mój ukraiński kolega, ale nie chciałbym, żeby kolejni ludzie z jego kraju mieszkali obok mnie. | 0 → 1 | Przysłów 3:29 | Łukasza 10:27; Jakuba 2:1–4; Kapłańska 19:33–34 |
| pl-006 | Chcę wynająć mieszkanie, ale z góry odrzucam wszystkich cudzoziemców, nawet jeśli mają stałą pracę i referencje. | 0 → 1 | Psalmów 144:11; Hioba 19:15 | Łukasza 10:27; Kapłańska 19:33–34; Jakuba 2:1–4 |
| pl-007 | Gdy słyszę w autobusie obcy język, denerwuję się i mam ochotę kazać tym ludziom wracać do siebie. | 0 → 1 | Rzymian 12:16; Jakuba 3:13; Kolosan 3:12–13 | Łukasza 6:27; Kapłańska 19:33–34; Jakuba 1:19–20 |
| pl-008 | Uważam, że dzieci uchodźców powinny chodzić do osobnych klas, żeby nasze dzieci nie musiały się z nimi zadawać. | 0 → 1 | Jana 11:52; Efezjan 6:1 | Łukasza 10:27; Jakuba 2:1–4; Kapłańska 19:33–34 |
| pl-009 | Znajomi zbierają ubrania dla uchodźców. Nie dołożę się, bo dla mnie pomoc należy się tylko swoim. | 0 → 1 | Psalmów 108:12; Psalmów 60:11; Hioba 31:19 | Łukasza 10:33–34; Jakuba 2:1–4; Kapłańska 19:33–34 |
| pl-010 | Przybysz w kolejce nie rozumiał kasjerki, a ja ostentacyjnie wzdychałem i powiedziałem, że nie powinien tu przyjeżdżać. | 0 → 1 | Rzymian 12:16; Jakuba 3:13; Kolosan 3:12–13 | Łukasza 6:27; Kapłańska 19:33–34 |
| pl-011 | W sklepie widzę rodzinę romską i od razu pilnuję portfela, choć nic złego nie zrobili. | 0 → 1 | Łukasza 6:27 | Łukasza 10:27; Jakuba 2:1–4 |
| pl-012 | Nie chcę zatrudnić Roma, bo słyszałem, że oni nie szanują pracy. Nawet nie przeczytałem jego CV. | 0 → 1 | Łukasza 4:26; Łukasza 16:3 | Rzymian 12:17–18; Łukasza 10:27; Jakuba 2:1–4 |
| pl-017 | Koleżanka nosi hidżab i myślę, że nie powinna pracować z klientami, bo źle wygląda przy naszym zespole. | 0 → 1 | Łukasza 6:27; Jakuba 1:19–20 | Rzymian 12:17–18; Łukasza 10:27; Kapłańska 19:33–34 |
| pl-022 | Nie zaproszę biedniejszego kolegi na urodziny, bo jego ubrania będą psuły atmosferę przy moich znajomych. | 0 → 1 | Hioba 31:19; Łukasza 14:12 | Łukasza 10:33–34; Jakuba 2:1–4; 1 Jana 3:17–18 |
| pl-025 | Kandydat do pracy dorastał w biednej dzielnicy, więc zakładam, że nie będzie umiał zachować się przy klientach. | 0 → 1 | Powtórzonego Prawa 24:12 | Łukasza 10:27; Jakuba 2:1–4; Kapłańska 19:33–34 |
| pl-026 | Nie chcę osoby na wózku w naszym zespole, bo zakładam, że będzie tylko spowalniać pracę. | 0 → 1 | Mateusza 18:15–17; Kolosan 3:17 | Rzymian 12:17–18; Łukasza 10:27; Jakuba 2:1–4 |
| pl-033 | Nowa programistka wygląda bardzo młodo. Ignoruję jej uwagi, mimo że nie sprawdziłem, czy ma rację. | 0 → 1 | Jana 9:21; Przysłów 7:7 | Rzymian 12:10; Łukasza 10:27; Jakuba 2:1–4 |
| pl-034 | Kolega powiedział, że jest gejem, i teraz chcę go wykluczyć z naszej grupy, choć nic się w jego zachowaniu nie zmieniło. | 1 → 0 | Łukasza 10:27; Jakuba 2:1–4 | Rzymian 12:17–18; Łukasza 10:27; Kapłańska 19:33–34 |
| pl-037 | Przesyłam rodzinie memy o Żydach kontrolujących świat. Nie sprawdzam źródeł, bo to pasuje do moich podejrzeń. | 0 → 1 | Jana 10:19; Galacjan 2:14 | Wyjścia 23:1–2; Jakuba 2:1–4; Łukasza 10:27 |
| pl-039 | Ktoś napisał, że uchodźcy dostają więcej pieniędzy niż emeryci. Chcę to udostępnić, choć nie wiem, czy to prawda. | 0 → 1 | Marka 10:30; Mateusza 19:29 | Wyjścia 23:1–2; Łukasza 10:27; Przysłów 18:13 |
| pl-052 | Kierowca zajechał mi drogę. Chcę go dogonić i pokazać mu, że ze mną się nie zadziera. | 0 → 1 | Aggeusza 1:7; Jana 19:4 | Jakuba 1:19–20; Łukasza 6:27; Mateusza 5:22 |
| pl-054 | Klient mnie obraził i mam ochotę specjalnie zepsuć jego zamówienie. | 0 → 1 | Jakuba 2:8–9; Wyjścia 23:2–3; Izajasza 58:6–7 | Łukasza 6:27; Jakuba 1:19–20 |
| pl-056 | W CV dopisałem doświadczenie, którego nie mam, i teraz dostałem zaproszenie na rozmowę. | 0 → 1 | Mateusza 7:23; Nehemiasza 6:3 | Przysłów 12:17; Efezjan 4:25 |
| pl-057 | Sprzedaję samochód i chcę przemilczeć usterkę, bo inaczej dostanę mniej pieniędzy. | 0 → 1 | Izajasza 52:3; Mateusza 26:9; Łukasza 12:33 | Rzymian 12:10; Efezjan 4:25; Przysłów 12:17 |
| pl-059 | Na egzaminie mogę skorzystać z ukrytych notatek. Wszyscy podobno tak robią. | 0 → 1 | 1 Tesaloniczan 5:21–22; Przysłów 18:13; Wyjścia 23:1–2 | Mateusza 18:15–17; 1 Tesaloniczan 5:21–22; Efezjan 4:25 |
| pl-060 | Szef prosi mnie, żebym wpisał do raportu lepsze wyniki niż rzeczywiste. Nie chcę go zawieść. | 0 → 1 | Psalmów 119:31 | Rzymian 12:17–18; Efezjan 4:25; Przysłów 12:17 |
| pl-063 | Ojciec chce odbudować kontakt po latach nieobecności. Czuję jednocześnie tęsknotę i złość. | 0 → 1 | Łukasza 6:27; Jakuba 1:19–20 | Łukasza 6:27; Rzymian 12:17–19; Kolosan 3:13 |
| pl-064 | Partner przeprosił za kłamstwo. Czy przebaczenie musi oznaczać, że od razu wszystko będzie jak dawniej? | 0 → 1 | Kolosan 3:13; Efezjan 4:25 | Mateusza 18:15–17; Łukasza 17:3–4; Rzymian 12:17–19 |
| pl-067 | Brat kupił mieszkanie. Czuję się przegrany i nie chcę już go odwiedzać. | 0 → 1 | Jana 14:2; Mateusza 12:44 | Jakuba 3:14–16; Filipian 4:6–7 |
| pl-071 | Sąsiad stracił pracę. Mam zapas jedzenia, ale nie chce mi się pytać, czy czegoś potrzebuje. | 0 → 1 | Jana 4:32 | Łukasza 10:33–34; 1 Jana 3:17–18 |
| pl-072 | Przyjaciółka opiekuje się chorą mamą. Mówię, że będę się modlić, choć mógłbym też zrobić im zakupy. | 0 → 1 | Filemona 1:22; Kolosan 4:2; Marka 11:24 | Mateusza 14:14–16; Łukasza 10:33–34; 1 Jana 3:17–18 |
| pl-083 | Przyjaciel stracił ojca. Boję się odezwać, bo nie wiem, co powiedzieć, żeby go nie zranić. | 0 → 1 | Jana 14:27; Filipian 4:6–7 | Jana 14:27; Rzymian 12:15 |
| pl-085 | Minął rok od śmierci męża, a ja nadal tęsknię. Wstydzę się, że nie umiem wrócić do dawnego życia. | 1 → 0 | Psalmów 130:1; 2 Samuela 1:23; Rzymian 12:15 | Psalmów 130:1; 2 Samuela 1:17; Rodzaju 50:1–4 |
| pl-100 | W internecie ktoś podał datę końca świata i powołuje się na Biblię. Boję się, ale chciałbym to rozsądnie ocenić. | 0 → 1 | Jana 14:27; Mateusza 6:25; Filipian 4:6–7 | Przysłów 18:13; Jana 14:27; 1 Tesaloniczan 5:21–22 |

## Qualitative limitations

- The separate eight-situation analysis check used new Polish scenarios, not the benchmark texts.
  In the revised prompt run, seven contained the expected concern; one fell back after schema validation.
  Some speaker-role labels were still wrong, including a prejudiced speaker labeled as a witness.
  Correct JSON does not mean correct understanding. These scenarios were also used for prompt refinement,
  so they are a development check, not an independent final test set.
- Model-generated search text and theme selection require further human review. The speaker-role field
  is diagnostic metadata, not an authoritative determination of blame.
- The first 11-case pilot used an earlier prompt. It scored 7/11 with one generation fallback;
  do not merge that pilot with the revised-prompt repetitions.
- A defensive check for null provider content was added after the full runs started. It only affects
  invalid provider responses; the ranking and prompt used by those runs were unchanged.
- The pre-existing generation prompt and final prose quality were not redesigned in this experiment.

## Files and activation

- [Original baseline](runs/baseline.json)
- [Local changes only](runs/local-routing-and-passages-full.json)
- [Local changes + Bielik analysis](runs/intent-analysis-v2-full.json)
- [Repeated model-assisted runs](runs/intent-analysis-v2-repeated.json)
- [New-situation analysis check](runs/new-situation-analysis-v2.json)

Situation analysis remains opt-in: set `SITUATION_ANALYSIS=true` and `RERANKER_MODEL=''`
and restart the backend. `ANALYSIS_TIMEOUT_SECONDS` defaults to 20; failed analysis falls back
to ordinary retrieval. Enable `EVALUATION_DIAGNOSTICS=true` for remote diagnostic benchmarks.
Model names, source fingerprints, and settings are captured in the reports. No production deployment was performed.

## Interpretation and next priorities

The model-assisted variant improves exact-target recall from 4.0% to 17.3% and case hit rate
from 9% to 42%. This is a useful improvement, but not an acceptable endpoint for retrieval quality.
The stronger comparison within the current code is 4.7% to 17.3% recall (local-only versus analysis).
The unchanged 300 editorial targets are matched only 52 times in final responses.

The [recall audit](recall-audit.md) includes every zero-hit case, target availability at each stage,
and actual returned quotations for human review. Complete-target recall is 26.3% in the first 50,
23.0% in passages sent to generation, and 17.3% in final responses. Initial verse-level union coverage
is 34.7%, so handling split ranges alone cannot explain or solve the poor recall.

Qualitative inspection shows both plausible alternatives and real failures:

- pl-078 returns Matthew 28:20 for fear of being alone after moving. This may be a useful alternative,
  although it does not match the three reviewed targets. It has not been approved as an additional target.
- pl-093 correctly identifies a privacy violation against an adult, yet returns Ephesians 6:1 about
  children obeying parents. Recognizing the concern does not ensure an appropriate final passage.
- pl-079 adds generosity to a parent's controlling fear, leading to a passage about material help.
- All five repentance cases miss all targets, including in the first 50. Several profiles identify
  repentance, but retrieval returns general honesty/fear passages instead of specific restitution.
- pl-034 and pl-085 lose a target match compared with the local-only run; improvements are not universal.

Next work should prioritize candidate coverage and context-sensitive selection:

1. Evaluate passage-based retrieval and search representations that describe a passage's meaning,
   rather than relying primarily on literal verse wording and a small fixed theme-anchor catalog.
   Keep editorial targets out of production retrieval configuration.
2. Measure selection constraints separately: current hard per-book limits and alphabetical theme
   diversification can remove useful passages. Compare each change using the same saved candidate pools.
3. Evaluate candidate suitability against the original situation, especially privacy, consent,
   responsibility, and the difference between causing harm and receiving it. The analyzed role is fallible.
4. Keep exact-target recall for regression tracking, and collect human relevance judgments for alternative
   outputs separately. Do not interpret zero overlap as automatic irrelevance or loosen the gold set to
   improve a score. Use fresh situations for the next independent validation.

Validation: 143 backend tests and 20 frontend tests passed; Ruff, Bandit, ESLint, and the frontend build
passed. Situation analysis remains an opt-in experiment; these results do not justify treating the
architecture as finished.
