# Recall audit: Bielik situation analysis

The approved dataset is unchanged. This is an audit of retrieval losses, not a new relevance judgment.

## Target coverage

| Stage | Fully matched targets / 300 | Recall | Any target found / 100 cases |
| --- | ---: | ---: | ---: |
| before_rerank | 79 | 26.3% | 57 |
| selected | 69 | 23.0% | 53 |
| final | 52 | 17.3% | 42 |

The first-50 score requires one candidate to contain the complete target range. Its verse-level union coverage is 34.7%, versus 26.3% complete-target recall. Splitting ranges explains part of the loss, but not most of it. Final verse-level coverage is only 19.4%.

Selected passages can expand existing short anchors, so stages are not strictly nested.

## Categories

| Category | Cases | Final recall | Cases with a target |
| --- | ---: | ---: | ---: |
| gniew_i_zemsta | 5 | 33.3% | 5 |
| granice_i_szacunek | 5 | 0.0% | 0 |
| hojnosc_i_wspolczucie | 5 | 26.7% | 2 |
| lek_i_niepewnosc | 5 | 0.0% | 0 |
| przebaczenie | 5 | 26.7% | 3 |
| skrucha_i_odpowiedzialnosc | 5 | 0.0% | 0 |
| uczciwosc | 5 | 26.7% | 4 |
| uprzedzenia | 50 | 18.7% | 22 |
| wiara_i_rozeznanie | 5 | 6.7% | 1 |
| zaloba_i_samotnosc | 5 | 13.3% | 2 |
| zazdrosc_i_pycha | 5 | 26.7% | 3 |

## Cases with no final target match

A missing approved target is not automatically an irrelevant answer. Alternative passages below still need human review; none have been added to the gold set.

### pl-013: Czarnoskóry chłopak spotyka się z moją córką. Jest dla niej dobry, ale wstydzę się, co powie rodzina.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| James 2:1 | True | True |
| John 7:24 | False | False |
| Matthew 7:12 | False | False |

Returned passages:

- **Filipian 4:6–7**: [6] Nie troszczcie się o nic, ale we wszystkim przez modlitwę i prośbę z dziękczynieniem niech wasze pragnienia będą znane Bogu. [7] A pokój Boży, który przewyższa wszelkie zrozumienie, będzie strzegł waszych serc i myśli w Chrystusie Jezusie.
- **Łukasza 10:27**: [27] A on odpowiedział: Będziesz miłował Pana, swego Boga, całym swym sercem, całą swą duszą, z całej swojej siły i całym swym umysłem, a swego bliźniego jak samego siebie.
- **Jana 14:27**: [27] Pokój zostawiam wam, mój pokój daję wam; daję wam nie tak, jak daje świat. Niech się nie trwoży wasze serce ani się nie lęka.

### pl-014: Sąsiad ma inny kolor skóry i boję się go bardziej niż innych, chociaż zawsze jest wobec mnie uprzejmy.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| James 2:1 | True | True |
| John 7:24 | False | False |
| Matthew 7:12 | False | False |

Returned passages:

- **Jana 14:27**: [27] Pokój zostawiam wam, mój pokój daję wam; daję wam nie tak, jak daje świat. Niech się nie trwoży wasze serce ani się nie lęka.
- **Łukasza 10:27**: [27] A on odpowiedział: Będziesz miłował Pana, swego Boga, całym swym sercem, całą swą duszą, z całej swojej siły i całym swym umysłem, a swego bliźniego jak samego siebie.
- **Kapłańska 19:33–34**: [33] Jeśli przybysz będzie mieszkał z tobą w waszej ziemi, nie czyńcie mu krzywdy; [34] Przybysz, który gości u was, będzie jak jeden urodzony wśród was. Będziesz go miłować jak samego siebie, bo i wy byliście przybyszami w ziemi Egiptu. Ja jestem PAN, wasz Bóg.

### pl-015: Na treningu wolę wybierać do drużyny tylko ludzi wyglądających jak ja. Resztę traktuję jak obcych.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| James 2:1 | True | True |
| John 7:24 | False | False |
| Matthew 7:12 | False | False |

Returned passages:

- **Rzymian 12:17–19**: [17] Nikomu złem za zło nie odpłacajcie; starajcie się o to, co uczciwe wobec wszystkich ludzi. [18] Jeśli to możliwe, o ile to od was zależy, ze wszystkimi ludźmi żyjcie w pokoju. [19] Najmilsi, nie mścijcie się sami, ale pozostawcie miejsce gniewowi. Jest bowiem napisane: Zemsta do mnie należy, ja odpłacę – mówi Pan.
- **Łukasza 10:27**: [27] A on odpowiedział: Będziesz miłował Pana, swego Boga, całym swym sercem, całą swą duszą, z całej swojej siły i całym swym umysłem, a swego bliźniego jak samego siebie.
- **Kapłańska 19:33–34**: [33] Jeśli przybysz będzie mieszkał z tobą w waszej ziemi, nie czyńcie mu krzywdy; [34] Przybysz, który gości u was, będzie jak jeden urodzony wśród was. Będziesz go miłować jak samego siebie, bo i wy byliście przybyszami w ziemi Egiptu. Ja jestem PAN, wasz Bóg.

### pl-016: Nie chcę mieć muzułmanina za sąsiada. Nie znam żadnego osobiście, ale zakładam, że każdy jest niebezpieczny.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| Luke 6:31 | False | False |
| Romans 12:18 | False | False |
| 1 Peter 2:17 | False | False |

Returned passages:

- **Jana 14:27**: [27] Pokój zostawiam wam, mój pokój daję wam; daję wam nie tak, jak daje świat. Niech się nie trwoży wasze serce ani się nie lęka.
- **Jakuba 2:1–4**: [1] Bracia moi, niech wiara naszego Pana Jezusa Chrystusa, Pana chwały, będzie wolna od względu na osobę. [2] Gdyby bowiem na wasze zgromadzenie przyszedł człowiek ze złotym pierścieniem i we wspaniałej szacie i przyszedłby też ubogi w nędznym stroju; [3] A wy zwrócicie oczy na tego, który ma wspaniałą szatę i powiecie: Ty usiądź tu w zaszczytnym miejscu, do ubogiego zaś powiecie: Ty stań tam lub usiądź tu u mego podnóżka; [4] To czy nie czynicie różnicy między sobą i nie stajecie się sędziami o przewrotnych myślach?
- **Kapłańska 19:33–34**: [33] Jeśli przybysz będzie mieszkał z tobą w waszej ziemi, nie czyńcie mu krzywdy; [34] Przybysz, który gości u was, będzie jak jeden urodzony wśród was. Będziesz go miłować jak samego siebie, bo i wy byliście przybyszami w ziemi Egiptu. Ja jestem PAN, wasz Bóg.

### pl-018: Mój brat przestał wierzyć w Boga i teraz traktuję go tak, jakby nie mógł mieć żadnych zasad moralnych.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| Luke 6:31 | False | False |
| Romans 12:18 | False | False |
| 1 Peter 2:17 | True | False |

Returned passages:

- **Kolosan 3:12–13**: [12] Tak więc jako wybrani Boga, święci i umiłowani, przyodziejcie się w serdeczne miłosierdzie, dobroć, pokorę, łagodność, cierpliwość; [13] Znosząc jedni drugich i przebaczając sobie nawzajem, jeśli ktoś ma skargę przeciw drugiemu: jak i Chrystus przebaczył wam, tak i wy.
- **Łukasza 10:27**: [27] A on odpowiedział: Będziesz miłował Pana, swego Boga, całym swym sercem, całą swą duszą, z całej swojej siły i całym swym umysłem, a swego bliźniego jak samego siebie.
- **1 Jana 3:17–18**: [17] A kto miałby majętność tego świata i widziałby swego brata w potrzebie, a zamknąłby przed nim swoje serce, jakże może mieszkać w nim miłość Boga? [18] Moje dzieci, nie miłujmy słowem ani językiem, ale uczynkiem i prawdą.

### pl-019: Usłyszałem, że nowa rodzina jest żydowska. Od razu pomyślałem o spiskach i nie chcę z nimi rozmawiać.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| Luke 6:31 | False | False |
| Romans 12:18 | False | False |
| 1 Peter 2:17 | False | False |

Returned passages:

- **Łukasza 10:27**: [27] A on odpowiedział: Będziesz miłował Pana, swego Boga, całym swym sercem, całą swą duszą, z całej swojej siły i całym swym umysłem, a swego bliźniego jak samego siebie.
- **Kapłańska 19:33–34**: [33] Jeśli przybysz będzie mieszkał z tobą w waszej ziemi, nie czyńcie mu krzywdy; [34] Przybysz, który gości u was, będzie jak jeden urodzony wśród was. Będziesz go miłować jak samego siebie, bo i wy byliście przybyszami w ziemi Egiptu. Ja jestem PAN, wasz Bóg.
- **Jakuba 2:1–4**: [1] Bracia moi, niech wiara naszego Pana Jezusa Chrystusa, Pana chwały, będzie wolna od względu na osobę. [2] Gdyby bowiem na wasze zgromadzenie przyszedł człowiek ze złotym pierścieniem i we wspaniałej szacie i przyszedłby też ubogi w nędznym stroju; [3] A wy zwrócicie oczy na tego, który ma wspaniałą szatę i powiecie: Ty usiądź tu w zaszczytnym miejscu, do ubogiego zaś powiecie: Ty stań tam lub usiądź tu u mego podnóżka; [4] To czy nie czynicie różnicy między sobą i nie stajecie się sędziami o przewrotnych myślach?

### pl-020: Syn przyjaźni się z protestantem. Chcę mu tego zakazać, choć ten chłopak nigdy nikogo nie skrzywdził.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| Luke 6:31 | False | False |
| Romans 12:18 | True | False |
| 1 Peter 2:17 | False | False |

Returned passages:

- **Rzymian 12:10**: [10] Miłujcie się wzajemnie miłością braterską, wyprzedzając jedni drugich w okazywaniu szacunku.
- **Łukasza 10:27**: [27] A on odpowiedział: Będziesz miłował Pana, swego Boga, całym swym sercem, całą swą duszą, z całej swojej siły i całym swym umysłem, a swego bliźniego jak samego siebie.
- **Kapłańska 19:33–34**: [33] Jeśli przybysz będzie mieszkał z tobą w waszej ziemi, nie czyńcie mu krzywdy; [34] Przybysz, który gości u was, będzie jak jeden urodzony wśród was. Będziesz go miłować jak samego siebie, bo i wy byliście przybyszami w ziemi Egiptu. Ja jestem PAN, wasz Bóg.

### pl-021: Brzydzę się bezdomnymi pod dworcem. Wolałbym, żeby ich po prostu usunięto, żebym nie musiał na nich patrzeć.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| James 2:2-4 | False | True |
| Proverbs 22:2 | False | False |
| Proverbs 14:31 | False | False |

Returned passages:

- **Kolosan 3:12–13**: [12] Tak więc jako wybrani Boga, święci i umiłowani, przyodziejcie się w serdeczne miłosierdzie, dobroć, pokorę, łagodność, cierpliwość; [13] Znosząc jedni drugich i przebaczając sobie nawzajem, jeśli ktoś ma skargę przeciw drugiemu: jak i Chrystus przebaczył wam, tak i wy.
- **Łukasza 10:27**: [27] A on odpowiedział: Będziesz miłował Pana, swego Boga, całym swym sercem, całą swą duszą, z całej swojej siły i całym swym umysłem, a swego bliźniego jak samego siebie.
- **1 Jana 3:17–18**: [17] A kto miałby majętność tego świata i widziałby swego brata w potrzebie, a zamknąłby przed nim swoje serce, jakże może mieszkać w nim miłość Boga? [18] Moje dzieci, nie miłujmy słowem ani językiem, ale uczynkiem i prawdą.

### pl-027: Kolega mówi, że ma depresję. Od tej chwili nie traktuję poważnie żadnego jego pomysłu.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| John 7:24 | False | False |
| Proverbs 18:13 | False | False |
| James 2:1 | False | False |

Returned passages:

- **Mateusza 14:14–16**: [14] Gdy Jezus wyszedł z łodzi, zobaczył wielki tłum, ulitował się nad nimi i uzdrawiał ich chorych. [15] A gdy nastał wieczór, podeszli do niego jego uczniowie i powiedzieli: Miejsce to jest puste, a pora już późna. Odpraw tych ludzi, aby poszli do wiosek i kupili sobie żywności. [16] Lecz Jezus im odpowiedział: Nie muszą odchodzić, wy dajcie im jeść.
- **Łukasza 10:33**: Lecz pewien Samarytanin, będąc w podróży, zbliżył się do niego. A gdy go zobaczył, ulitował się nad nim.

### pl-028: Wolę, żeby dziecko z zespołem Downa nie uczestniczyło w klasowej wycieczce. Boję się, że będzie kłopot.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| Luke 14:13 | False | False |
| Romans 15:7 | False | False |
| James 2:1 | True | True |

Returned passages:

- **Jana 14:27**: [27] Pokój zostawiam wam, mój pokój daję wam; daję wam nie tak, jak daje świat. Niech się nie trwoży wasze serce ani się nie lęka.
- **Łukasza 10:27**: [27] A on odpowiedział: Będziesz miłował Pana, swego Boga, całym swym sercem, całą swą duszą, z całej swojej siły i całym swym umysłem, a swego bliźniego jak samego siebie.
- **Filipian 4:6–7**: [6] Nie troszczcie się o nic, ale we wszystkim przez modlitwę i prośbę z dziękczynieniem niech wasze pragnienia będą znane Bogu. [7] A pokój Boży, który przewyższa wszelkie zrozumienie, będzie strzegł waszych serc i myśli w Chrystusie Jezusie.

### pl-029: Gdy ktoś się jąka, kończę za niego zdania i nie daję mu zabierać głosu na spotkaniu.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| Job 13:17 | False | False |
| Proverbs 18:13 | False | False |
| Proverbs 17:27 | False | False |

Returned passages:

- **Mateusza 18:15–17**: [15] Jeśli twój brat zgrzeszy przeciwko tobie, idź, strofuj go sam na sam. Jeśli cię usłucha, pozyskałeś twego brata. [16] Jeśli zaś cię nie usłucha, weź ze sobą jeszcze jednego albo dwóch, aby na podstawie zeznania dwóch albo trzech świadków oparte było każde słowo. [17] Jeśli ich nie usłucha, powiedz kościołowi. A jeśli kościoła nie usłucha, niech będzie dla ciebie jak poganin i celnik.
- **Jakuba 2:8**: [8] A jeśli wypełniacie królewskie prawo zgodnie z Pismem: Będziesz miłował swego bliźniego jak samego siebie, dobrze czynicie.
- **Rzymian 12:10**: [10] Miłujcie się wzajemnie miłością braterską, wyprzedzając jedni drugich w okazywaniu szacunku.

### pl-030: Starsza sąsiadka chce dołączyć do naszego kursu. Śmieję się, że w jej wieku nauka nie ma już sensu.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| Leviticus 19:32 | False | False |
| John 7:24 | False | False |
| Psalms 92:12-15 | False | False |

Returned passages:

- **Łukasza 10:33–34**: [33] Lecz pewien Samarytanin, będąc w podróży, zbliżył się do niego. A gdy go zobaczył, ulitował się nad nim. [34] A podszedłszy, opatrzył mu rany, zalewając je oliwą i winem; potem wsadził go na swoje zwierzę, zawiózł do gospody i opiekował się nim.
- **Mateusza 6:19–21**: [19] Nie gromadźcie sobie skarbów na ziemi, gdzie mól i rdza niszczą i gdzie złodzieje włamują się i kradną; [20] Ale gromadźcie sobie skarby w niebie, gdzie ani mól, ani rdza nie niszczą i gdzie złodzieje nie włamują się i nie kradną. [21] Gdzie bowiem jest wasz skarb, tam będzie i wasze serce.
- **Jakuba 2:1–4**: [1] Bracia moi, niech wiara naszego Pana Jezusa Chrystusa, Pana chwały, będzie wolna od względu na osobę. [2] Gdyby bowiem na wasze zgromadzenie przyszedł człowiek ze złotym pierścieniem i we wspaniałej szacie i przyszedłby też ubogi w nędznym stroju; [3] A wy zwrócicie oczy na tego, który ma wspaniałą szatę i powiecie: Ty usiądź tu w zaszczytnym miejscu, do ubogiego zaś powiecie: Ty stań tam lub usiądź tu u mego podnóżka; [4] To czy nie czynicie różnicy między sobą i nie stajecie się sędziami o przewrotnych myślach?

### pl-031: Nie dam kobiecie awansu na kierownika, bo uważam, że kobiety są zbyt emocjonalne, chociaż ma najlepsze wyniki.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| James 2:1 | True | False |
| Genesis 1:27 | False | False |
| John 7:24 | True | False |

Returned passages:

- **Jakuba 2:8–9**: [8] A jeśli wypełniacie królewskie prawo zgodnie z Pismem: Będziesz miłował swego bliźniego jak samego siebie, dobrze czynicie. [9] Lecz jeśli macie wzgląd na osobę, popełniacie grzech i jesteście osądzeni przez prawo jako przestępcy.
- **Łukasza 10:27**: [27] A on odpowiedział: Będziesz miłował Pana, swego Boga, całym swym sercem, całą swą duszą, z całej swojej siły i całym swym umysłem, a swego bliźniego jak samego siebie.
- **Wyjścia 23:2–3**: [2] Nie idź za większością, aby wyrządzić zło, i nie zeznawaj w sprawie, ulegając zdaniu większości, by naginać sąd. [3] I nie okazuj przychylności ubogiemu w jego sprawie.

### pl-032: Mężczyzna zgłosił się do pracy w przedszkolu i od razu podejrzewam, że coś jest z nim nie tak.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| James 2:1 | True | True |
| Genesis 1:27 | False | False |
| John 7:24 | True | False |

Returned passages:

- **Jana 14:27**: [27] Pokój zostawiam wam, mój pokój daję wam; daję wam nie tak, jak daje świat. Niech się nie trwoży wasze serce ani się nie lęka.
- **Wyjścia 23:2–3**: [2] Nie idź za większością, aby wyrządzić zło, i nie zeznawaj w sprawie, ulegając zdaniu większości, by naginać sąd. [3] I nie okazuj przychylności ubogiemu w jego sprawie.
- **Kapłańska 19:33–34**: [33] Jeśli przybysz będzie mieszkał z tobą w waszej ziemi, nie czyńcie mu krzywdy; [34] Przybysz, który gości u was, będzie jak jeden urodzony wśród was. Będziesz go miłować jak samego siebie, bo i wy byliście przybyszami w ziemi Egiptu. Ja jestem PAN, wasz Bóg.

### pl-034: Kolega powiedział, że jest gejem, i teraz chcę go wykluczyć z naszej grupy, choć nic się w jego zachowaniu nie zmieniło.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| James 2:1 | True | True |
| Genesis 1:27 | False | False |
| John 7:24 | False | False |

Returned passages:

- **Rzymian 12:17–18**: [17] Nikomu złem za zło nie odpłacajcie; starajcie się o to, co uczciwe wobec wszystkich ludzi. [18] Jeśli to możliwe, o ile to od was zależy, ze wszystkimi ludźmi żyjcie w pokoju.
- **Łukasza 10:27**: [27] A on odpowiedział: Będziesz miłował Pana, swego Boga, całym swym sercem, całą swą duszą, z całej swojej siły i całym swym umysłem, a swego bliźniego jak samego siebie.
- **Kapłańska 19:33–34**: [33] Jeśli przybysz będzie mieszkał z tobą w waszej ziemi, nie czyńcie mu krzywdy; [34] Przybysz, który gości u was, będzie jak jeden urodzony wśród was. Będziesz go miłować jak samego siebie, bo i wy byliście przybyszami w ziemi Egiptu. Ja jestem PAN, wasz Bóg.

### pl-036: Widziałem filmik o przestępstwie imigranta i chcę napisać, że wszyscy imigranci są przestępcami.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| Exodus 23:1 | False | False |
| Proverbs 18:13 | False | False |
| John 7:24 | False | False |

Returned passages:

- **Jakuba 1:19–20**: [19] Tak więc, moi umiłowani bracia, niech każdy człowiek będzie skory do słuchania, nieskory do mówienia i nieskory do gniewu. [20] Gniew bowiem człowieka nie wykonuje sprawiedliwości Bożej.
- **Kapłańska 19:33–34**: [33] Jeśli przybysz będzie mieszkał z tobą w waszej ziemi, nie czyńcie mu krzywdy; [34] Przybysz, który gości u was, będzie jak jeden urodzony wśród was. Będziesz go miłować jak samego siebie, bo i wy byliście przybyszami w ziemi Egiptu. Ja jestem PAN, wasz Bóg.
- **Łukasza 10:27**: [27] A on odpowiedział: Będziesz miłował Pana, swego Boga, całym swym sercem, całą swą duszą, z całej swojej siły i całym swym umysłem, a swego bliźniego jak samego siebie.

### pl-038: Jeden cudzoziemiec mnie oszukał i teraz ostrzegam znajomych, żeby nigdy nie ufali nikomu z jego kraju.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| Exodus 23:1 | False | False |
| Proverbs 18:13 | False | False |
| John 7:24 | False | False |

Returned passages:

- **Mateusza 5:37**: [37] Ale wasza mowa niech będzie: Tak – tak, nie – nie. A co jest ponadto, pochodzi od złego.
- **Jakuba 2:1–4**: [1] Bracia moi, niech wiara naszego Pana Jezusa Chrystusa, Pana chwały, będzie wolna od względu na osobę. [2] Gdyby bowiem na wasze zgromadzenie przyszedł człowiek ze złotym pierścieniem i we wspaniałej szacie i przyszedłby też ubogi w nędznym stroju; [3] A wy zwrócicie oczy na tego, który ma wspaniałą szatę i powiecie: Ty usiądź tu w zaszczytnym miejscu, do ubogiego zaś powiecie: Ty stań tam lub usiądź tu u mego podnóżka; [4] To czy nie czynicie różnicy między sobą i nie stajecie się sędziami o przewrotnych myślach?
- **Kapłańska 19:33–34**: [33] Jeśli przybysz będzie mieszkał z tobą w waszej ziemi, nie czyńcie mu krzywdy; [34] Przybysz, który gości u was, będzie jak jeden urodzony wśród was. Będziesz go miłować jak samego siebie, bo i wy byliście przybyszami w ziemi Egiptu. Ja jestem PAN, wasz Bóg.

### pl-040: Uważam wszystkich wyborców przeciwnej partii za głupich i zepsutych. Nawet nie słucham, co mówią.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| Exodus 23:1 | False | False |
| Proverbs 18:13 | False | False |
| John 7:24 | False | False |

Returned passages:

- **Jakuba 1:19–20**: [19] Tak więc, moi umiłowani bracia, niech każdy człowiek będzie skory do słuchania, nieskory do mówienia i nieskory do gniewu. [20] Gniew bowiem człowieka nie wykonuje sprawiedliwości Bożej.
- **Łukasza 10:27**: [27] A on odpowiedział: Będziesz miłował Pana, swego Boga, całym swym sercem, całą swą duszą, z całej swojej siły i całym swym umysłem, a swego bliźniego jak samego siebie.
- **Mateusza 5:22**: [22] Lecz ja wam mówię: Każdy, kto się gniewa na swego brata bez przyczyny, podlega sądowi, a kto powie swemu bratu: Raka, podlega Radzie, a kto powie: Głupcze, podlega karze ognia piekielnego.

### pl-041: Koledzy w pracy wyśmiewają ukraiński akcent sprzątaczki. Milczę, bo boję się, że potem będą śmiać się ze mnie.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| Proverbs 31:8-9 | False | False |
| Isaiah 1:17 | False | False |
| Ephesians 4:29 | False | False |

Returned passages:

- **Jana 14:27**: [27] Pokój zostawiam wam, mój pokój daję wam; daję wam nie tak, jak daje świat. Niech się nie trwoży wasze serce ani się nie lęka.
- **Łukasza 10:27**: [27] A on odpowiedział: Będziesz miłował Pana, swego Boga, całym swym sercem, całą swą duszą, z całej swojej siły i całym swym umysłem, a swego bliźniego jak samego siebie.

### pl-042: Wujek przy stole opowiada rasistowskie dowcipy. Dzieci słuchają, a ja nie wiem, jak zareagować bez awantury.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| Proverbs 31:8-9 | False | False |
| Isaiah 1:17 | False | False |
| Ephesians 4:29 | False | False |

Returned passages:

- **Mateusza 18:15–17**: [15] Jeśli twój brat zgrzeszy przeciwko tobie, idź, strofuj go sam na sam. Jeśli cię usłucha, pozyskałeś twego brata. [16] Jeśli zaś cię nie usłucha, weź ze sobą jeszcze jednego albo dwóch, aby na podstawie zeznania dwóch albo trzech świadków oparte było każde słowo. [17] Jeśli ich nie usłucha, powiedz kościołowi. A jeśli kościoła nie usłucha, niech będzie dla ciebie jak poganin i celnik.
- **1 Jana 3:17–18**: [17] A kto miałby majętność tego świata i widziałby swego brata w potrzebie, a zamknąłby przed nim swoje serce, jakże może mieszkać w nim miłość Boga? [18] Moje dzieci, nie miłujmy słowem ani językiem, ale uczynkiem i prawdą.
- **Kapłańska 19:33–34**: [33] Jeśli przybysz będzie mieszkał z tobą w waszej ziemi, nie czyńcie mu krzywdy; [34] Przybysz, który gości u was, będzie jak jeden urodzony wśród was. Będziesz go miłować jak samego siebie, bo i wy byliście przybyszami w ziemi Egiptu. Ja jestem PAN, wasz Bóg.

### pl-043: W klasowej grupie rodzice obrażają romskie dziecko. Chcę je obronić, ale zależy mi na dobrych relacjach z grupą.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| Proverbs 31:8-9 | False | False |
| Isaiah 1:17 | False | False |
| Ephesians 4:29 | False | False |

Returned passages:

- **Rzymian 12:17–18**: [17] Nikomu złem za zło nie odpłacajcie; starajcie się o to, co uczciwe wobec wszystkich ludzi. [18] Jeśli to możliwe, o ile to od was zależy, ze wszystkimi ludźmi żyjcie w pokoju.
- **Łukasza 10:33–34**: [33] Lecz pewien Samarytanin, będąc w podróży, zbliżył się do niego. A gdy go zobaczył, ulitował się nad nim. [34] A podszedłszy, opatrzył mu rany, zalewając je oliwą i winem; potem wsadził go na swoje zwierzę, zawiózł do gospody i opiekował się nim.
- **Jakuba 2:1–4**: [1] Bracia moi, niech wiara naszego Pana Jezusa Chrystusa, Pana chwały, będzie wolna od względu na osobę. [2] Gdyby bowiem na wasze zgromadzenie przyszedł człowiek ze złotym pierścieniem i we wspaniałej szacie i przyszedłby też ubogi w nędznym stroju; [3] A wy zwrócicie oczy na tego, który ma wspaniałą szatę i powiecie: Ty usiądź tu w zaszczytnym miejscu, do ubogiego zaś powiecie: Ty stań tam lub usiądź tu u mego podnóżka; [4] To czy nie czynicie różnicy między sobą i nie stajecie się sędziami o przewrotnych myślach?

### pl-044: Szef każe mi odrzucać kandydatów z obco brzmiącymi nazwiskami. Czuję, że to krzywdzące, ale boję się sprzeciwić.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| Proverbs 31:8-9 | False | False |
| Isaiah 1:17 | False | False |
| Ephesians 4:29 | False | False |

Returned passages:

- **Łukasza 10:27**: [27] A on odpowiedział: Będziesz miłował Pana, swego Boga, całym swym sercem, całą swą duszą, z całej swojej siły i całym swym umysłem, a swego bliźniego jak samego siebie.
- **Jakuba 2:1–4**: [1] Bracia moi, niech wiara naszego Pana Jezusa Chrystusa, Pana chwały, będzie wolna od względu na osobę. [2] Gdyby bowiem na wasze zgromadzenie przyszedł człowiek ze złotym pierścieniem i we wspaniałej szacie i przyszedłby też ubogi w nędznym stroju; [3] A wy zwrócicie oczy na tego, który ma wspaniałą szatę i powiecie: Ty usiądź tu w zaszczytnym miejscu, do ubogiego zaś powiecie: Ty stań tam lub usiądź tu u mego podnóżka; [4] To czy nie czynicie różnicy między sobą i nie stajecie się sędziami o przewrotnych myślach?
- **Kapłańska 19:33–34**: [33] Jeśli przybysz będzie mieszkał z tobą w waszej ziemi, nie czyńcie mu krzywdy; [34] Przybysz, który gości u was, będzie jak jeden urodzony wśród was. Będziesz go miłować jak samego siebie, bo i wy byliście przybyszami w ziemi Egiptu. Ja jestem PAN, wasz Bóg.

### pl-045: Znajomi naśladują niepełnosprawnego kolegę. Śmiałem się z nimi, żeby nie wyjść na sztywniaka, a teraz mam wyrzuty sumienia.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| Proverbs 31:8-9 | False | False |
| Isaiah 1:17 | True | False |
| Ephesians 4:29 | False | False |

Returned passages:

- **Łukasza 10:33–34**: [33] Lecz pewien Samarytanin, będąc w podróży, zbliżył się do niego. A gdy go zobaczył, ulitował się nad nim. [34] A podszedłszy, opatrzył mu rany, zalewając je oliwą i winem; potem wsadził go na swoje zwierzę, zawiózł do gospody i opiekował się nim.
- **1 Jana 3:17–18**: [17] A kto miałby majętność tego świata i widziałby swego brata w potrzebie, a zamknąłby przed nim swoje serce, jakże może mieszkać w nim miłość Boga? [18] Moje dzieci, nie miłujmy słowem ani językiem, ale uczynkiem i prawdą.

### pl-046: Jestem Ukrainką i kolega mówi mi, że odpowiadam za zbrodnie ludzi, których nigdy nie znałam. Czuję się upokorzona.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| Genesis 1:27 | False | False |
| Psalms 34:18 | False | False |
| Romans 12:21 | False | False |

Returned passages:

- **Łukasza 10:27**: [27] A on odpowiedział: Będziesz miłował Pana, swego Boga, całym swym sercem, całą swą duszą, z całej swojej siły i całym swym umysłem, a swego bliźniego jak samego siebie.
- **Jakuba 2:1–4**: [1] Bracia moi, niech wiara naszego Pana Jezusa Chrystusa, Pana chwały, będzie wolna od względu na osobę. [2] Gdyby bowiem na wasze zgromadzenie przyszedł człowiek ze złotym pierścieniem i we wspaniałej szacie i przyszedłby też ubogi w nędznym stroju; [3] A wy zwrócicie oczy na tego, który ma wspaniałą szatę i powiecie: Ty usiądź tu w zaszczytnym miejscu, do ubogiego zaś powiecie: Ty stań tam lub usiądź tu u mego podnóżka; [4] To czy nie czynicie różnicy między sobą i nie stajecie się sędziami o przewrotnych myślach?
- **Kapłańska 19:33–34**: [33] Jeśli przybysz będzie mieszkał z tobą w waszej ziemi, nie czyńcie mu krzywdy; [34] Przybysz, który gości u was, będzie jak jeden urodzony wśród was. Będziesz go miłować jak samego siebie, bo i wy byliście przybyszami w ziemi Egiptu. Ja jestem PAN, wasz Bóg.

### pl-047: W szkole śmieją się z mojego koloru skóry. Zaczynam myśleć, że jestem gorszy od innych.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| Genesis 1:27 | False | False |
| Psalms 34:18 | False | False |
| Romans 12:21 | False | False |

Returned passages:

- **Kapłańska 19:33–34**: [33] Jeśli przybysz będzie mieszkał z tobą w waszej ziemi, nie czyńcie mu krzywdy; [34] Przybysz, który gości u was, będzie jak jeden urodzony wśród was. Będziesz go miłować jak samego siebie, bo i wy byliście przybyszami w ziemi Egiptu. Ja jestem PAN, wasz Bóg.
- **Jakuba 2:1–4**: [1] Bracia moi, niech wiara naszego Pana Jezusa Chrystusa, Pana chwały, będzie wolna od względu na osobę. [2] Gdyby bowiem na wasze zgromadzenie przyszedł człowiek ze złotym pierścieniem i we wspaniałej szacie i przyszedłby też ubogi w nędznym stroju; [3] A wy zwrócicie oczy na tego, który ma wspaniałą szatę i powiecie: Ty usiądź tu w zaszczytnym miejscu, do ubogiego zaś powiecie: Ty stań tam lub usiądź tu u mego podnóżka; [4] To czy nie czynicie różnicy między sobą i nie stajecie się sędziami o przewrotnych myślach?
- **Łukasza 10:27**: [27] A on odpowiedział: Będziesz miłował Pana, swego Boga, całym swym sercem, całą swą duszą, z całej swojej siły i całym swym umysłem, a swego bliźniego jak samego siebie.

### pl-048: Rodzina obraża mojego męża, bo pochodzi z innego kraju. Chcę go bronić, ale jestem zmęczona ciągłą walką.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| Genesis 1:27 | False | False |
| Psalms 34:18 | False | False |
| Romans 12:21 | True | False |

Returned passages:

- **Łukasza 10:33–34**: [33] Lecz pewien Samarytanin, będąc w podróży, zbliżył się do niego. A gdy go zobaczył, ulitował się nad nim. [34] A podszedłszy, opatrzył mu rany, zalewając je oliwą i winem; potem wsadził go na swoje zwierzę, zawiózł do gospody i opiekował się nim.
- **Kapłańska 19:33–34**: [33] Jeśli przybysz będzie mieszkał z tobą w waszej ziemi, nie czyńcie mu krzywdy; [34] Przybysz, który gości u was, będzie jak jeden urodzony wśród was. Będziesz go miłować jak samego siebie, bo i wy byliście przybyszami w ziemi Egiptu. Ja jestem PAN, wasz Bóg.
- **Rzymian 12:17–19**: [17] Nikomu złem za zło nie odpłacajcie; starajcie się o to, co uczciwe wobec wszystkich ludzi. [18] Jeśli to możliwe, o ile to od was zależy, ze wszystkimi ludźmi żyjcie w pokoju. [19] Najmilsi, nie mścijcie się sami, ale pozostawcie miejsce gniewowi. Jest bowiem napisane: Zemsta do mnie należy, ja odpłacę – mówi Pan.

### pl-049: Jestem niewierzący, a wierzący znajomi nazywają mnie człowiekiem bez sumienia. Bardzo mnie to boli.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| Genesis 1:27 | False | False |
| Psalms 34:18 | False | False |
| Romans 12:21 | False | False |

Returned passages:

- **Łukasza 10:33–34**: [33] Lecz pewien Samarytanin, będąc w podróży, zbliżył się do niego. A gdy go zobaczył, ulitował się nad nim. [34] A podszedłszy, opatrzył mu rany, zalewając je oliwą i winem; potem wsadził go na swoje zwierzę, zawiózł do gospody i opiekował się nim.
- **Jakuba 2:1–4**: [1] Bracia moi, niech wiara naszego Pana Jezusa Chrystusa, Pana chwały, będzie wolna od względu na osobę. [2] Gdyby bowiem na wasze zgromadzenie przyszedł człowiek ze złotym pierścieniem i we wspaniałej szacie i przyszedłby też ubogi w nędznym stroju; [3] A wy zwrócicie oczy na tego, który ma wspaniałą szatę i powiecie: Ty usiądź tu w zaszczytnym miejscu, do ubogiego zaś powiecie: Ty stań tam lub usiądź tu u mego podnóżka; [4] To czy nie czynicie różnicy między sobą i nie stajecie się sędziami o przewrotnych myślach?
- **1 Jana 3:17–18**: [17] A kto miałby majętność tego świata i widziałby swego brata w potrzebie, a zamknąłby przed nim swoje serce, jakże może mieszkać w nim miłość Boga? [18] Moje dzieci, nie miłujmy słowem ani językiem, ale uczynkiem i prawdą.

### pl-050: Przez mój akcent ludzie traktują mnie jak głupią. Mam ochotę odpłacić im taką samą pogardą.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| 1 Peter 3:9 | False | False |
| John 7:24 | False | False |
| Romans 12:21 | False | False |

Returned passages:

- **Łukasza 6:27**: [27] Lecz mówię wam, którzy słuchacie: Miłujcie waszych nieprzyjaciół, dobrze czyńcie tym, którzy was nienawidzą.
- **Kolosan 3:13**: [13] Znosząc jedni drugich i przebaczając sobie nawzajem, jeśli ktoś ma skargę przeciw drugiemu: jak i Chrystus przebaczył wam, tak i wy.
- **Mateusza 5:22**: [22] Lecz ja wam mówię: Każdy, kto się gniewa na swego brata bez przyczyny, podlega sądowi, a kto powie swemu bratu: Raka, podlega Radzie, a kto powie: Głupcze, podlega karze ognia piekielnego.

### pl-058: Kasjerka wydała mi za dużo reszty. Zauważyłem to od razu, ale nie chcę oddawać.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| Ephesians 4:25 | True | True |
| Proverbs 11:1 | False | False |
| Luke 16:10 | False | False |

Returned passages:

- **Przysłów 12:17**: [17] Kto mówi prawdę, wyraża sprawiedliwość, ale fałszywy świadek – oszustwo.
- **Jakuba 2:8–9**: [8] A jeśli wypełniacie królewskie prawo zgodnie z Pismem: Będziesz miłował swego bliźniego jak samego siebie, dobrze czynicie. [9] Lecz jeśli macie wzgląd na osobę, popełniacie grzech i jesteście osądzeni przez prawo jako przestępcy.
- **Mateusza 5:37**: [37] Ale wasza mowa niech będzie: Tak – tak, nie – nie. A co jest ponadto, pochodzi od złego.

### pl-062: Siostra oddała pożyczone pieniądze po roku. Nadal wypominam jej to przy każdym spotkaniu.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| Ephesians 4:32 | True | False |
| Luke 17:3-4 | False | False |
| Romans 12:18 | False | False |

Returned passages:

- **Łukasza 6:27**: [27] Lecz mówię wam, którzy słuchacie: Miłujcie waszych nieprzyjaciół, dobrze czyńcie tym, którzy was nienawidzą.
- **Kolosan 3:13**: [13] Znosząc jedni drugich i przebaczając sobie nawzajem, jeśli ktoś ma skargę przeciw drugiemu: jak i Chrystus przebaczył wam, tak i wy.
- **Jakuba 1:19–20**: [19] Tak więc, moi umiłowani bracia, niech każdy człowiek będzie skory do słuchania, nieskory do mówienia i nieskory do gniewu. [20] Gniew bowiem człowieka nie wykonuje sprawiedliwości Bożej.

### pl-065: Koleżanka skrzywdziła mnie i nie widzi problemu. Nie chcę żyć nienawiścią, ale potrzebuję dystansu.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| Ephesians 4:32 | True | False |
| Luke 17:3-4 | False | True |
| Romans 12:18 | True | True |

Returned passages:

- **Mateusza 18:15–17**: [15] Jeśli twój brat zgrzeszy przeciwko tobie, idź, strofuj go sam na sam. Jeśli cię usłucha, pozyskałeś twego brata. [16] Jeśli zaś cię nie usłucha, weź ze sobą jeszcze jednego albo dwóch, aby na podstawie zeznania dwóch albo trzech świadków oparte było każde słowo. [17] Jeśli ich nie usłucha, powiedz kościołowi. A jeśli kościoła nie usłucha, niech będzie dla ciebie jak poganin i celnik.
- **Kolosan 3:13**: [13] Znosząc jedni drugich i przebaczając sobie nawzajem, jeśli ktoś ma skargę przeciw drugiemu: jak i Chrystus przebaczył wam, tak i wy.

### pl-068: Ktoś inny dostał podziękowania za nasz projekt. Mam ochotę sabotować jego dalszą pracę.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| James 3:16 | False | False |
| Philippians 2:3 | True | False |
| Romans 12:15 | False | False |

Returned passages:

- **Łukasza 6:27**: [27] Lecz mówię wam, którzy słuchacie: Miłujcie waszych nieprzyjaciół, dobrze czyńcie tym, którzy was nienawidzą.
- **Mateusza 5:37**: [37] Ale wasza mowa niech będzie: Tak – tak, nie – nie. A co jest ponadto, pochodzi od złego.
- **Jakuba 1:19–20**: [19] Tak więc, moi umiłowani bracia, niech każdy człowiek będzie skory do słuchania, nieskory do mówienia i nieskory do gniewu. [20] Gniew bowiem człowieka nie wykonuje sprawiedliwości Bożej.

### pl-069: Uważam się za najbardziej pobożną osobę w rodzinie i z góry traktuję wszystkich, którzy rzadziej chodzą do kościoła.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| Luke 18:9-14 | False | False |
| Philippians 2:3 | False | False |
| James 4:6 | False | False |

Returned passages:

- **Jakuba 2:1–4**: [1] Bracia moi, niech wiara naszego Pana Jezusa Chrystusa, Pana chwały, będzie wolna od względu na osobę. [2] Gdyby bowiem na wasze zgromadzenie przyszedł człowiek ze złotym pierścieniem i we wspaniałej szacie i przyszedłby też ubogi w nędznym stroju; [3] A wy zwrócicie oczy na tego, który ma wspaniałą szatę i powiecie: Ty usiądź tu w zaszczytnym miejscu, do ubogiego zaś powiecie: Ty stań tam lub usiądź tu u mego podnóżka; [4] To czy nie czynicie różnicy między sobą i nie stajecie się sędziami o przewrotnych myślach?
- **Łukasza 10:27**: [27] A on odpowiedział: Będziesz miłował Pana, swego Boga, całym swym sercem, całą swą duszą, z całej swojej siły i całym swym umysłem, a swego bliźniego jak samego siebie.

### pl-073: W parafii naciskają na większą składkę, a ja ledwo opłacam rachunki i czuję się winny.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| 2 Corinthians 8:12 | False | False |
| 2 Corinthians 8:13 | False | False |
| 2 Corinthians 9:7 | False | False |

Returned passages:

- **Rzymian 12:17–18**: [17] Nikomu złem za zło nie odpłacajcie; starajcie się o to, co uczciwe wobec wszystkich ludzi. [18] Jeśli to możliwe, o ile to od was zależy, ze wszystkimi ludźmi żyjcie w pokoju.
- **Mateusza 6:34**: [34] Dlatego nie troszczcie się o dzień jutrzejszy, gdyż dzień jutrzejszy sam się zatroszczy o swoje potrzeby. Dosyć ma dzień swego utrapienia.
- **1 Jana 3:17–18**: [17] A kto miałby majętność tego świata i widziałby swego brata w potrzebie, a zamknąłby przed nim swoje serce, jakże może mieszkać w nim miłość Boga? [18] Moje dzieci, nie miłujmy słowem ani językiem, ale uczynkiem i prawdą.

### pl-074: Pomagam znajomemu, ale zaczynam oczekiwać publicznych podziękowań za każdy drobiazg.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| Matthew 6:1-4 | False | False |
| 1 Corinthians 13:4-5 | False | False |
| 2 Corinthians 9:7 | True | False |

Returned passages:

- **Łukasza 10:33–34**: [33] Lecz pewien Samarytanin, będąc w podróży, zbliżył się do niego. A gdy go zobaczył, ulitował się nad nim. [34] A podszedłszy, opatrzył mu rany, zalewając je oliwą i winem; potem wsadził go na swoje zwierzę, zawiózł do gospody i opiekował się nim.
- **Mateusza 6:19–21**: [19] Nie gromadźcie sobie skarbów na ziemi, gdzie mól i rdza niszczą i gdzie złodzieje włamują się i kradną; [20] Ale gromadźcie sobie skarby w niebie, gdzie ani mól, ani rdza nie niszczą i gdzie złodzieje nie włamują się i nie kradną. [21] Gdzie bowiem jest wasz skarb, tam będzie i wasze serce.

### pl-075: Widzę samotnego człowieka na osiedlowym spotkaniu i udaję, że go nie zauważam, bo wolę spędzać czas ze znajomymi.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| Hebrews 13:2 | False | False |
| Luke 14:12-13 | False | False |
| Romans 15:7 | False | False |

Returned passages:

- **Łukasza 10:33**: Lecz pewien Samarytanin, będąc w podróży, zbliżył się do niego. A gdy go zobaczył, ulitował się nad nim.
- **Kolosan 3:12–13**: [12] Tak więc jako wybrani Boga, święci i umiłowani, przyodziejcie się w serdeczne miłosierdzie, dobroć, pokorę, łagodność, cierpliwość; [13] Znosząc jedni drugich i przebaczając sobie nawzajem, jeśli ktoś ma skargę przeciw drugiemu: jak i Chrystus przebaczył wam, tak i wy.

### pl-076: Firma zapowiada zwolnienia. Ciągle wyobrażam sobie, że stracę pracę i wszystko się rozpadnie.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| Matthew 6:26 | False | False |
| Psalms 46:1-2 | False | False |
| 1 Peter 5:7 | False | False |

Returned passages:

- **Filipian 4:6–7**: [6] Nie troszczcie się o nic, ale we wszystkim przez modlitwę i prośbę z dziękczynieniem niech wasze pragnienia będą znane Bogu. [7] A pokój Boży, który przewyższa wszelkie zrozumienie, będzie strzegł waszych serc i myśli w Chrystusie Jezusie.
- **Rzymian 12:12**: [12] Radujący się w nadziei, cierpliwi w ucisku, nieustający w modlitwie;
- **Mateusza 6:27**: [27] I któż z was, martwiąc się, może dodać do swego wzrostu jeden łokieć?

### pl-077: Czekam na ważną odpowiedź i co kilka minut sprawdzam telefon. Nie umiem skupić się na dzisiejszym dniu.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| Psalms 131:2 | False | False |
| Matthew 6:27 | True | False |
| Psalms 94:19 | False | False |

Returned passages:

- **Jana 14:27**: [27] Pokój zostawiam wam, mój pokój daję wam; daję wam nie tak, jak daje świat. Niech się nie trwoży wasze serce ani się nie lęka.
- **Filipian 4:6–7**: [6] Nie troszczcie się o nic, ale we wszystkim przez modlitwę i prośbę z dziękczynieniem niech wasze pragnienia będą znane Bogu. [7] A pokój Boży, który przewyższa wszelkie zrozumienie, będzie strzegł waszych serc i myśli w Chrystusie Jezusie.
- **Mateusza 6:25**: [25] Dlatego mówię wam: Nie troszczcie się o wasze życie, co będziecie jeść albo co będziecie pić, ani o wasze ciało, w co będziecie się ubierać. Czyż życie nie jest czymś więcej niż pokarm, a ciało niż ubranie?

### pl-078: Mam przeprowadzić się do nowego miasta. Boję się, że sobie nie poradzę i zostanę zupełnie sam.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| Psalms 23:4 | True | False |
| Psalms 121:1-2 | False | False |
| Psalms 139:9-10 | False | False |

Returned passages:

- **Jana 14:27**: [27] Pokój zostawiam wam, mój pokój daję wam; daję wam nie tak, jak daje świat. Niech się nie trwoży wasze serce ani się nie lęka.
- **Mateusza 28:20**: [20] Ucząc je przestrzegać wszystkiego, co wam przykazałem. A oto ja jestem z wami przez wszystkie dni aż do końca świata. Amen.
- **Filipian 4:6–7**: [6] Nie troszczcie się o nic, ale we wszystkim przez modlitwę i prośbę z dziękczynieniem niech wasze pragnienia będą znane Bogu. [7] A pokój Boży, który przewyższa wszelkie zrozumienie, będzie strzegł waszych serc i myśli w Chrystusie Jezusie.

### pl-079: Moje dorosłe dziecko wyjeżdża za granicę. Chcę kontrolować każdy jego krok, bo tak bardzo się boję.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| Proverbs 3:5-6 | False | False |
| Galatians 6:4-5 | False | False |
| Psalms 121:7-8 | False | False |

Returned passages:

- **Filipian 4:6–7**: [6] Nie troszczcie się o nic, ale we wszystkim przez modlitwę i prośbę z dziękczynieniem niech wasze pragnienia będą znane Bogu. [7] A pokój Boży, który przewyższa wszelkie zrozumienie, będzie strzegł waszych serc i myśli w Chrystusie Jezusie.
- **Jana 14:27**: [27] Pokój zostawiam wam, mój pokój daję wam; daję wam nie tak, jak daje świat. Niech się nie trwoży wasze serce ani się nie lęka.
- **1 Jana 3:17–18**: [17] A kto miałby majętność tego świata i widziałby swego brata w potrzebie, a zamknąłby przed nim swoje serce, jakże może mieszkać w nim miłość Boga? [18] Moje dzieci, nie miłujmy słowem ani językiem, ale uczynkiem i prawdą.

### pl-080: Jutro mam rozmowę o pracę i w głowie słyszę tylko, że na pewno poniosę porażkę.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| Ecclesiastes 11:6 | False | False |
| Psalms 27:1 | False | False |
| Philippians 4:11-13 | False | False |

Returned passages:

- **Jana 14:27**: [27] Pokój zostawiam wam, mój pokój daję wam; daję wam nie tak, jak daje świat. Niech się nie trwoży wasze serce ani się nie lęka.
- **Filipian 4:6–7**: [6] Nie troszczcie się o nic, ale we wszystkim przez modlitwę i prośbę z dziękczynieniem niech wasze pragnienia będą znane Bogu. [7] A pokój Boży, który przewyższa wszelkie zrozumienie, będzie strzegł waszych serc i myśli w Chrystusie Jezusie.
- **Mateusza 6:25**: [25] Dlatego mówię wam: Nie troszczcie się o wasze życie, co będziecie jeść albo co będziecie pić, ani o wasze ciało, w co będziecie się ubierać. Czyż życie nie jest czymś więcej niż pokarm, a ciało niż ubranie?

### pl-082: Po rozwodzie znajomi przestali mnie zapraszać. Weekendy są dla mnie najtrudniejsze.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| Proverbs 17:17 | False | False |
| Psalms 25:16 | False | False |
| Romans 15:7 | False | False |

Returned passages:

- **Rzymian 12:15**: [15] Radujcie się z tymi, którzy się radują, a płaczcie z tymi, którzy płaczą.
- **Mateusza 28:20**: [20] Ucząc je przestrzegać wszystkiego, co wam przykazałem. A oto ja jestem z wami przez wszystkie dni aż do końca świata. Amen.

### pl-084: Przeprowadziłam się i nikogo tu nie znam. Nawet w tłumie czuję się niewidzialna.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| Psalms 139:9-10 | False | False |
| Isaiah 41:10 | False | False |
| Isaiah 49:15-16 | False | False |

Returned passages:

- **Mateusza 28:20**: [20] Ucząc je przestrzegać wszystkiego, co wam przykazałem. A oto ja jestem z wami przez wszystkie dni aż do końca świata. Amen.
- **Łukasza 10:27**: [27] A on odpowiedział: Będziesz miłował Pana, swego Boga, całym swym sercem, całą swą duszą, z całej swojej siły i całym swym umysłem, a swego bliźniego jak samego siebie.
- **Psalmów 22:1–2**: [1] Boże mój, Boże mój, czemu mnie opuściłeś? Czemu jesteś tak daleki od wybawienia mnie, od słów mego jęku? [2] Boże mój, wołam we dnie, a nie odzywasz się do mnie; w nocy, a nie mogę się uspokoić.

### pl-085: Minął rok od śmierci męża, a ja nadal tęsknię. Wstydzę się, że nie umiem wrócić do dawnego życia.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| John 11:33-36 | False | False |
| Ecclesiastes 3:4 | False | False |
| Romans 12:15 | True | True |

Returned passages:

- **Psalmów 130:1**: Z głębokości wołam do ciebie, PANIE.
- **2 Samuela 1:17**: Wtedy Dawid podniósł lament nad Saulem i jego synem Jonatanem;
- **Rodzaju 50:1–4**: [1] Wtedy Józef przypadł do twarzy swego ojca i płakał nad nim, i całował go. [2] Potem Józef rozkazał swoim sługom, lekarzom, aby zabalsamowali jego ojca. I lekarze zabalsamowali Izraela. [3] I minęło czterdzieści dni, bo tyle trwa balsamowanie. Egipcjanie opłakiwali go przez siedemdziesiąt dni. [4] Po upływie dni żałoby Józef powiedział do domowników faraona: Jeśli znalazłem teraz łaskę w waszych oczach, powiedzcie, proszę, do uszu faraona:

### pl-086: Rozpuściłem plotkę o koledze i teraz stracił zaufanie zespołu. Samo przepraszam wydaje mi się za mało.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| Luke 19:8 | False | False |
| Proverbs 28:13 | False | False |
| Matthew 5:23-24 | False | False |

Returned passages:

- **Kolosan 3:13**: [13] Znosząc jedni drugich i przebaczając sobie nawzajem, jeśli ktoś ma skargę przeciw drugiemu: jak i Chrystus przebaczył wam, tak i wy.
- **Przysłów 12:17**: [17] Kto mówi prawdę, wyraża sprawiedliwość, ale fałszywy świadek – oszustwo.
- **Efezjan 4:25**: [25] Dlatego odrzuciwszy kłamstwo, niech każdy mówi prawdę swojemu bliźniemu, bo jesteśmy członkami jedni drugich.

### pl-087: Pożyczyłam od siostry pieniądze i udaję, że nie pamiętam, bo wstydzę się przyznać, że je wydałam.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| Luke 19:8 | False | False |
| Proverbs 28:13 | False | False |
| Matthew 5:23-24 | False | False |

Returned passages:

- **Efezjan 4:25**: [25] Dlatego odrzuciwszy kłamstwo, niech każdy mówi prawdę swojemu bliźniemu, bo jesteśmy członkami jedni drugich.
- **Przysłów 12:17**: [17] Kto mówi prawdę, wyraża sprawiedliwość, ale fałszywy świadek – oszustwo.
- **Jana 14:27**: [27] Pokój zostawiam wam, mój pokój daję wam; daję wam nie tak, jak daje świat. Niech się nie trwoży wasze serce ani się nie lęka.

### pl-088: Popełniłem błąd w pracy, ale winę zrzucono na nowego pracownika. Do tej pory milczałem.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| Luke 19:8 | False | False |
| Proverbs 28:13 | False | False |
| Matthew 5:23-24 | False | False |

Returned passages:

- **Rzymian 12:17–18**: [17] Nikomu złem za zło nie odpłacajcie; starajcie się o to, co uczciwe wobec wszystkich ludzi. [18] Jeśli to możliwe, o ile to od was zależy, ze wszystkimi ludźmi żyjcie w pokoju.
- **Przysłów 12:17**: [17] Kto mówi prawdę, wyraża sprawiedliwość, ale fałszywy świadek – oszustwo.
- **Wyjścia 23:2–3**: [2] Nie idź za większością, aby wyrządzić zło, i nie zeznawaj w sprawie, ulegając zdaniu większości, by naginać sąd. [3] I nie okazuj przychylności ubogiemu w jego sprawie.

### pl-089: Obiecałem dziecku wspólny dzień i znowu wybrałem pracę. Nie chcę kolejny raz kończyć na pustych przeprosinach.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| Luke 19:8 | False | False |
| Proverbs 28:13 | False | False |
| Matthew 5:23-24 | False | False |

Returned passages:

- **Rzymian 12:10**: [10] Miłujcie się wzajemnie miłością braterską, wyprzedzając jedni drugich w okazywaniu szacunku.
- **Łukasza 10:33**: Lecz pewien Samarytanin, będąc w podróży, zbliżył się do niego. A gdy go zobaczył, ulitował się nad nim.

### pl-090: Zniszczyłem cudzą rzecz i nikt tego nie widział. Chciałbym naprawić szkodę, ale boję się przyznać.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| Luke 19:8 | False | False |
| Proverbs 28:13 | False | False |
| Matthew 5:23-24 | False | False |

Returned passages:

- **Jana 14:27**: [27] Pokój zostawiam wam, mój pokój daję wam; daję wam nie tak, jak daje świat. Niech się nie trwoży wasze serce ani się nie lęka.
- **Mateusza 5:37**: [37] Ale wasza mowa niech będzie: Tak – tak, nie – nie. A co jest ponadto, pochodzi od złego.
- **Efezjan 4:25**: [25] Dlatego odrzuciwszy kłamstwo, niech każdy mówi prawdę swojemu bliźniemu, bo jesteśmy członkami jedni drugich.

### pl-091: Czytam wiadomości partnera bez jego zgody, bo uważam, że w związku nie powinno być żadnych tajemnic.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| Proverbs 31:11 | True | False |
| 1 Corinthians 13:4-7 | False | False |
| 1 Thessalonians 4:11 | False | False |

Returned passages:

- **Rzymian 12:10**: [10] Miłujcie się wzajemnie miłością braterską, wyprzedzając jedni drugich w okazywaniu szacunku.
- **Mateusza 18:15–17**: [15] Jeśli twój brat zgrzeszy przeciwko tobie, idź, strofuj go sam na sam. Jeśli cię usłucha, pozyskałeś twego brata. [16] Jeśli zaś cię nie usłucha, weź ze sobą jeszcze jednego albo dwóch, aby na podstawie zeznania dwóch albo trzech świadków oparte było każde słowo. [17] Jeśli ich nie usłucha, powiedz kościołowi. A jeśli kościoła nie usłucha, niech będzie dla ciebie jak poganin i celnik.
- **Jakuba 2:8**: [8] A jeśli wypełniacie królewskie prawo zgodnie z Pismem: Będziesz miłował swego bliźniego jak samego siebie, dobrze czynicie.

### pl-092: Koleżanka powiedziała mi coś osobistego. Chcę opowiedzieć to grupie jako zabawną historię.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| Proverbs 11:13 | False | False |
| Proverbs 25:9-10 | False | False |
| Ephesians 4:29 | False | False |

Returned passages:

- **Rzymian 12:17–18**: [17] Nikomu złem za zło nie odpłacajcie; starajcie się o to, co uczciwe wobec wszystkich ludzi. [18] Jeśli to możliwe, o ile to od was zależy, ze wszystkimi ludźmi żyjcie w pokoju.
- **Efezjan 4:25**: [25] Dlatego odrzuciwszy kłamstwo, niech każdy mówi prawdę swojemu bliźniemu, bo jesteśmy członkami jedni drugich.

### pl-093: Rodzice żądają hasła do mojego konta, choć jestem dorosła. Czuję, że nie szanują mojej prywatności.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| 1 Thessalonians 4:11 | False | False |
| Proverbs 25:17 | False | False |
| 1 Corinthians 13:4-5 | False | False |

Returned passages:

- **Rzymian 12:10**: [10] Miłujcie się wzajemnie miłością braterską, wyprzedzając jedni drugich w okazywaniu szacunku.
- **Efezjan 6:1**: Dzieci, bądźcie posłuszne waszym rodzicom w Panu, bo jest to sprawiedliwe.

### pl-094: Znajomy ciągle pożycza moje rzeczy bez pytania. Boję się odmówić, żeby nie wyjść na egoistę.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| Matthew 18:15 | True | False |
| 2 Corinthians 9:7 | False | False |
| Proverbs 29:25 | False | False |

Returned passages:

- **Jakuba 2:8**: [8] A jeśli wypełniacie królewskie prawo zgodnie z Pismem: Będziesz miłował swego bliźniego jak samego siebie, dobrze czynicie.
- **Rzymian 12:10**: [10] Miłujcie się wzajemnie miłością braterską, wyprzedzając jedni drugich w okazywaniu szacunku.

### pl-095: Partner naciska na bliskość, kiedy mówię, że nie chcę. Twierdzi, że gdybym go kochała, nie odmawiałabym.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| 1 Corinthians 13:4-5 | False | False |
| Romans 13:10 | False | False |
| Philemon 1:14 | False | False |

Returned passages:

- **Rzymian 12:17–18**: [17] Nikomu złem za zło nie odpłacajcie; starajcie się o to, co uczciwe wobec wszystkich ludzi. [18] Jeśli to możliwe, o ile to od was zależy, ze wszystkimi ludźmi żyjcie w pokoju.
- **Jana 14:27**: [27] Pokój zostawiam wam, mój pokój daję wam; daję wam nie tak, jak daje świat. Niech się nie trwoży wasze serce ani się nie lęka.
- **Mateusza 18:15–17**: [15] Jeśli twój brat zgrzeszy przeciwko tobie, idź, strofuj go sam na sam. Jeśli cię usłucha, pozyskałeś twego brata. [16] Jeśli zaś cię nie usłucha, weź ze sobą jeszcze jednego albo dwóch, aby na podstawie zeznania dwóch albo trzech świadków oparte było każde słowo. [17] Jeśli ich nie usłucha, powiedz kościołowi. A jeśli kościoła nie usłucha, niech będzie dla ciebie jak poganin i celnik.

### pl-096: Modlę się, ale nie czuję obecności Boga. Boję się przyznać, że mam wątpliwości.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| Mark 9:24 | False | False |
| James 1:5 | True | False |
| 1 Thessalonians 5:21 | False | False |

Returned passages:

- **Filipian 4:6–7**: [6] Nie troszczcie się o nic, ale we wszystkim przez modlitwę i prośbę z dziękczynieniem niech wasze pragnienia będą znane Bogu. [7] A pokój Boży, który przewyższa wszelkie zrozumienie, będzie strzegł waszych serc i myśli w Chrystusie Jezusie.
- **Jana 14:27**: [27] Pokój zostawiam wam, mój pokój daję wam; daję wam nie tak, jak daje świat. Niech się nie trwoży wasze serce ani się nie lęka.
- **Psalmów 130:5–8**: [5] Oczekuję PANA, moja dusza oczekuje; i w jego słowie pokładam nadzieję. [6] Moja dusza oczekuje Pana bardziej niż strażnicy świtu, bardziej niż ci, którzy strzegą do poranka. [7] Niech Izrael oczekuje PANA; u PANA bowiem jest miłosierdzie i u niego obfite odkupienie. [8] On sam odkupi Izraela ze wszystkich jego nieprawości.

### pl-097: Ktoś mówi, że jeśli wpłacę pieniądze jego wspólnocie, Bóg na pewno rozwiąże moje problemy. Nie wiem, czy mu wierzyć.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| 1 Timothy 6:5 | False | False |
| 1 Thessalonians 5:21 | True | False |
| 2 Corinthians 9:7 | False | False |

Returned passages:

- **Przysłów 18:13**: [13] Kto odpowiada, zanim wysłucha, ujawnia głupotę i ściąga na siebie hańbę.
- **Mateusza 6:19–21**: [19] Nie gromadźcie sobie skarbów na ziemi, gdzie mól i rdza niszczą i gdzie złodzieje włamują się i kradną; [20] Ale gromadźcie sobie skarby w niebie, gdzie ani mól, ani rdza nie niszczą i gdzie złodzieje nie włamują się i nie kradną. [21] Gdzie bowiem jest wasz skarb, tam będzie i wasze serce.
- **Łukasza 10:33–34**: [33] Lecz pewien Samarytanin, będąc w podróży, zbliżył się do niego. A gdy go zobaczył, ulitował się nad nim. [34] A podszedłszy, opatrzył mu rany, zalewając je oliwą i winem; potem wsadził go na swoje zwierzę, zawiózł do gospody i opiekował się nim.

### pl-098: Usłyszałem kazanie, z którym się nie zgadzam. Czy samo zadawanie pytań oznacza brak wiary?

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| Mark 9:24 | False | False |
| James 1:5 | True | False |
| 1 Thessalonians 5:21 | False | False |

Returned passages:

- **Filipian 4:6–7**: [6] Nie troszczcie się o nic, ale we wszystkim przez modlitwę i prośbę z dziękczynieniem niech wasze pragnienia będą znane Bogu. [7] A pokój Boży, który przewyższa wszelkie zrozumienie, będzie strzegł waszych serc i myśli w Chrystusie Jezusie.
- **Jana 14:27**: [27] Pokój zostawiam wam, mój pokój daję wam; daję wam nie tak, jak daje świat. Niech się nie trwoży wasze serce ani się nie lęka.
- **Mateusza 6:25**: [25] Dlatego mówię wam: Nie troszczcie się o wasze życie, co będziecie jeść albo co będziecie pić, ani o wasze ciało, w co będziecie się ubierać. Czyż życie nie jest czymś więcej niż pokarm, a ciało niż ubranie?

### pl-099: Muszę podjąć ważną decyzję i każdy mówi mi, że zna wolę Boga dla mojego życia. Jestem coraz bardziej zagubiona.

| Approved target | In first 50 | Sent to generation |
| --- | --- | --- |
| Mark 9:24 | False | False |
| James 1:5 | False | False |
| 1 Thessalonians 5:21 | True | True |

Returned passages:

- **Przysłów 18:13**: [13] Kto odpowiada, zanim wysłucha, ujawnia głupotę i ściąga na siebie hańbę.
- **Filipian 4:6–7**: [6] Nie troszczcie się o nic, ale we wszystkim przez modlitwę i prośbę z dziękczynieniem niech wasze pragnienia będą znane Bogu. [7] A pokój Boży, który przewyższa wszelkie zrozumienie, będzie strzegł waszych serc i myśli w Chrystusie Jezusie.
- **Jana 14:27**: [27] Pokój zostawiam wam, mój pokój daję wam; daję wam nie tak, jak daje świat. Niech się nie trwoży wasze serce ani się nie lęka.

