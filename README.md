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

## In English

Free Claude skills (Claude Code and Claude.ai) for small online shops that run their own ads. They work on exported report files, with no API keys and no account access, and never change anything in the account. The first skill reviews a Google Ads search terms export: spend per campaign, terms that waste budget with a reason for each, a paste-ready negative keyword list and converting terms to add as keywords. The method: exclude by intent, not by missing conversions; zero conversions only means something after spending about 3× the profit per order; exclude single words in phrase match; negative keywords don't match Polish inflections, so each form is listed separately. `hasla.py` reads Polish and English exports (CSV and the UTF-16 Excel CSV) with only the Python standard library and has a test. The skills are written in Polish for Polish shops.

Licencja: [MIT](LICENSE).
