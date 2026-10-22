# Skille Claude do reklam e-commerce

Darmowe skille dla Claude (Claude Code i Claude.ai) dla małych sklepów internetowych, które same prowadzą reklamy. Działają na plikach eksportu z panelu reklamowego, bez kluczy API i bez dostępu do konta. Niczego na koncie nie zmieniają: pokazują, co zmienić, a decyzja zostaje u Ciebie.

| Skill | Co robi |
|---|---|
| [przeglad-hasel](skills/przeglad-hasel/) | przegląd wyszukiwanych haseł Google Ads: na co idzie budżet, co wykluczyć, co dodać jako słowa kluczowe |

## Przegląd haseł Google Ads

1. Pobierz z Google Ads raport „Wyszukiwane hasła” jako CSV (Statystyki i raporty → Wyszukiwane hasła → pobierz → CSV), najlepiej z ostatnich 30 dni.
2. Daj plik Claude'owi i napisz, co sprzedajesz, czego nie sprzedajesz, ile zarabiasz na zamówieniu i jakie słowa na pewno zostają.
3. Dostajesz koszt na kampanię, hasła, które przepalają pieniądze (każde z powodem), listę wykluczeń do wklejenia w Google Ads i hasła z konwersją do dodania jako słowa kluczowe.

Metoda:

- wykluczaj po intencji, nie po braku konwersji;
- zero konwersji coś znaczy dopiero po wydaniu na hasło ok. 3 × zysku z zamówienia, wcześniej to przypadek;
- wykluczaj jedno słowo w dopasowaniu do wyrażenia zamiast całej frazy;
- wykluczające słowa kluczowe nie łapią odmian: „ekspres” nie zablokuje „ekspresy”, ale też nie zablokuje hasła „kawa do ekspresu”;
- w Shoppingu „jaki” i „najlepszy” zostają, bo tak pytają kupujący, którzy porównują produkty;
- przeciek poniżej 5% kosztu: nic nie rób.

### Przykład

[`sklep-z-kawa.csv`](skills/przeglad-hasel/przyklad/sklep-z-kawa.csv) to zmyślony sklep z kawą: 44 hasła z 30 dni w dwóch kampaniach. Liczby liczy skrypt, oceną zajmuje się Claude.

```
$ python3 skills/przeglad-hasel/hasla.py skills/przeglad-hasel/przyklad/sklep-z-kawa.csv 40
sklep-z-kawa.csv: hasła 44, kliknięcia 635, koszt 1362.00 PLN
Raport pokazuje 635 z 1052 kliknięć (60%), resztę Google ukrywa.

Kampania                                  klik.     koszt  konw.
Wszystkie produkty (Shopping)               329    712.30      8
Kawa ziarnista (Search)                     306    649.70     12

Podejrzane („?”) bez konwersji: 87.00 z 1362.00 (6% kosztu)
Próg: 3 × 40 = 120; „!” = bez konwersji i koszt powyżej progu
...
## Bez konwersji według kosztu („?” podejrzane, „+” słowo kluczowe, „W” wykluczone, „!” ponad próg)
  ! kawa ziarnista tanio                               klik.   55  koszt   128.40  [Kawa ziarnista (Search)]
    ekspres do kawy                                    klik.   27  koszt    61.20  [Wszystkie produkty (Shopping)]
    ekspres ciśnieniowy delonghi                       klik.   18  koszt    45.90  [Wszystkie produkty (Shopping)]
...
```

Na tym pliku Claude zaproponował 17 wykluczeń za 466,30 zł (34% kosztu widocznego w raporcie), m.in. „tanio”, „ekspres” i osobno „ekspresy”. Zostawił „najlepsza kawa ziarnista” w Shoppingu i nie ruszył hasła „kawa do ekspresu kolbowego”, które sprzedaje.

### Instalacja

Claude Code:

```
git clone https://github.com/nightherd/claude-skille-ecommerce.git
cp -r claude-skille-ecommerce/skills/przeglad-hasel ~/.claude/skills/
```

Repo jest też wtyczką Claude Code (`skille-ecommerce`), więc można je wczytać na jedną sesję: `claude --plugin-dir claude-skille-ecommerce`.

Potem w Claude Code napisz na przykład: „przejrzyj hasła z ~/Downloads/raport.csv”.

Claude.ai: spakuj cały folder skilla (`cd claude-skille-ecommerce/skills && zip -r przeglad-hasel.zip przeglad-hasel/`, w ZIP-ie musi być folder, nie same pliki) i wgraj go w Customize → Skills. Skrypt wymaga włączonego wykonywania kodu.

Test skryptu: `python3 skills/przeglad-hasel/test_hasla.py`

### Czego to nie robi

- nie łączy się z kontem Google Ads i niczego w nim nie zmienia;
- nie widzi haseł, które Google ukrywa w raporcie (w małych kontach to często połowa kliknięć);
- nie obejmuje kampanii Performance Max, które mają osobny raport statystyk wyszukiwanych haseł;
- nie zna Twojej oferty lepiej niż Ty: każdą propozycję sprawdź przed wklejeniem.

### Evale: czy skill pomaga

W [`evals/`](evals/) jest zestaw testów dla wbudowanego w Claude Code polecenia `claude plugin eval`. Każdy przypadek to prośba właściciela sklepu i raport CSV. Przypadek idzie 3 razy ze skillem i 3 razy bez niego (ten sam Claude Code z tym samym plikiem), a różnica pokazuje, co wnosi skill.

21 przypadków na zmyślonych danych:

- kawa (10, przykład z repo): pełny przegląd, wyższy zysk z zamówienia, sklep, który sprzedaje też ekspresy, brak danych od użytkownika, plik zapisany ponownie w Excelu;
- lniana pościel (6, nowe dane): odmiany słów („kołdra” wykluczyć, „kołdrę” nie, bo jest w haśle, które sprzedaje), eksport z angielskiego panelu, prośba „wyklucz wszystko bez sprzedaży”;
- planszówki (3, nowe dane): czysty raport, w którym dobra odpowiedź to „nic nie wykluczaj”;
- 2 prośby spoza zakresu, przy których skill nie powinien się włączać.

Oceniają to gradery: czy dane słowo jest na liście wykluczeń albo czy go tam nie ma (regex), czy liczby z raportu się zgadzają, czy skill się włączył, a w 8 przypadkach krótka ocena modelu Haiku według kryteriów zapisanych w przypadku. Wynik to średnia część zaliczonych kontroli (1,00 = wszystko dobrze).

Wynik z 22.10.2026: Sonnet 5.5, sędzia Haiku 5.5, Claude Code 2.1.274 na Linuksie, 126 przebiegów, ok. 20 $ według cennika API.

| Sklep | Przypadki | Ze skillem | Bez skilla | Różnica |
|---|---|---|---|---|
| kawa | 10 | 1,00 | 0,61 | +0,39 |
| lniana pościel | 6 | 0,95 | 0,76 | +0,19 |
| planszówki | 3 | 1,00 | 0,78 | +0,22 |
| prośby spoza zakresu | 2 | 1,00 | 1,00 | 0,00 |
| razem | 21 | 0,99 | 0,71 | +0,28 |

Co wyszło:

- Bez skilla Claude nie pyta o brakujące dane, w tym o zysk z zamówienia, tylko od razu przegląda raport na własnych założeniach.
- Bez skilla zgadza się wykluczać całe frazy („ekspres do kawy”, „kapsułki nespresso”) zamiast jednego słowa, więc inne warianty z raportu, np. „ekspres przelewowy” i „kapsułki do kawy”, dalej kosztują.
- Bez skilla nie liczy progu 3 × zysk, a w czystym raporcie pisze „prawie nic nie trzeba wykluczać” i mimo to proponuje drobne wykluczenia, np. „gry logiczne”, choć to gry dla dzieci z oferty sklepu.
- Skill zaliczył wszystkie kontrole w 59 z 63 przebiegów. Potknięcia są przy pościeli: dwa razy wykluczył „kołdry”, choć sklep sprzedaje poszewki na kołdry, raz nie zablokował hasła „materac 160x200” i raz pominął poradnik „jak prać pościel lnianą”.
- Skill bywał mądrzejszy od testów: nie wykluczył słowa „materac”, bo klienci szukają „prześcieradło na materac”, tylko zablokował samo hasło `[materac 160x200]`. Dlatego gradery sprawdzają, czy hasło jest zablokowane, a nie jedną metodę.

Uruchomienie (każdy przebieg to wywołania modelu z Twojego abonamentu albo konta API):

```
claude plugin eval . --scaffold --allow-tools "Bash(python3 *)" --model claude-sonnet-5-5
```

`--scaffold` pozwala skryptom `przygotuj.sh` skopiować raport do pustego katalogu przebiegu, a Bash dostaje tylko `python3`, w piaskownicy Claude Code (na Linuksie wymaga ona `bubblewrap` i `socat`).

Czego to nie mierzy:

- czy wykluczenia poprawią wynik kampanii: to wymaga testu na prawdziwym koncie;
- prawdziwych danych: wszystkie raporty są zmyślone;
- całej listy wykluczeń: gradery sprawdzają wybrane słowa, a nie każdą pozycję;
- propozycji wpisanych w zwykłe zdanie zamiast listy albo tabeli: takie się nie liczą, co dotyczy głównie wersji bez skilla;
- przypadki z kawą są łatwiejsze dla skilla, bo jego instrukcja używa słów z tego przykładu („ekspres”, „najlepsza kawa”); uczciwszy obraz dają pościel i planszówki;
- jeden model w jednym dniu i 3 przebiegi na przypadek to mała próba.

## In English

Free Claude skills (Claude Code and Claude.ai) for small online shops that run their own ads. They work on exported report files, with no API keys and no account access, and never change anything in the account. The first skill reviews a Google Ads search terms export: spend per campaign, terms that waste budget with a reason for each, a paste-ready negative keyword list and converting terms to add as keywords. The method: exclude by intent, not by missing conversions; zero conversions only means something after spending about 3× the profit per order; exclude single words in phrase match; negative keywords don't match Polish inflections, so each form is listed separately. `hasla.py` reads Polish and English exports (CSV and the UTF-16 Excel CSV) with only the Python standard library and has a test. An eval suite for `claude plugin eval` (21 cases, 3 runs each with and without the skill, Sonnet 5.5) scores 0.99 with the skill and 0.71 without it. The skills are written in Polish for Polish shops.

Licencja: [MIT](LICENSE).
