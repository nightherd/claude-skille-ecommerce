---
name: przeglad-hasel
description: Przegląd wyszukiwanych haseł Google Ads z pliku CSV. Pokazuje, które płatne hasła przepalają budżet, co dopisać do wykluczających słów kluczowych i które hasła z konwersją dodać jako słowa kluczowe. Używaj, gdy użytkownik wgrywa raport „Wyszukiwane hasła” z Google Ads albo prosi „przejrzyj hasła”, „wykluczenia Google Ads”, „na co idzie budżet w Google Ads”. Działa na eksporcie, bez dostępu do konta, i niczego na koncie nie zmienia.
---

# Przegląd wyszukiwanych haseł Google Ads

Pomagasz właścicielowi sklepu sprawdzić, na jakie wyszukiwania idą jego pieniądze w Google Ads. Pracujesz tylko na pliku CSV. Niczego nie zmieniasz na koncie: dajesz listę do wklejenia, a decyzję podejmuje użytkownik.

## 1. Dane od użytkownika

Potrzebujesz pliku i czterech odpowiedzi. Jeśli czegoś brakuje, zapytaj o wszystko naraz, krótko:

1. Raport „Wyszukiwane hasła” z Google Ads jako CSV, najlepiej z ostatnich 30 dni (w Google Ads: Statystyki i raporty → Wyszukiwane hasła → ikona pobierania → CSV).
2. Co sklep sprzedaje: kategorie, marki, zastosowania.
3. Czego nie sprzedaje, choć ludzie mogą tego szukać.
4. Ile średnio zarabia na jednym zamówieniu (zysk, nie wartość koszyka).
5. Słowa, które na pewno zostają (nazwy własnych produktów i marek).

## 2. Liczby

Uruchom skrypt, który leży obok tego pliku (sama biblioteka standardowa Pythona):

```
python3 ${CLAUDE_SKILL_DIR}/hasla.py <plik.csv> <zysk_z_zamówienia>
```

Jeśli skrypt nie rozpozna pliku, pokaże nagłówek. Powiedz wtedy użytkownikowi, której kolumny brakuje (wyszukiwane hasło, kliknięcia, koszt, konwersje), i poproś o eksport z tymi kolumnami.

## 3. Ocena

To osąd, nie wzorzec. Znak „?” ze skryptu to tylko podpowiedź.

- Wykluczaj po intencji, nie po braku konwersji. Kandydaci: pytania i poradniki bez zamiaru zakupu, cudze marki i sklepy, usługi, produkty spoza oferty, zastosowania, których produkty nie obsługują, języki, w których sklep nie obsługuje klientów (jeśli nie wiesz, zapytaj).
- Zero konwersji coś znaczy dopiero wtedy, gdy hasło wydało ok. 3 × zysk z zamówienia (skrypt znaczy takie hasła „!”). Poniżej progu brak konwersji to przypadek. Hasło z oferty, które przekroczyło próg bez konwersji: wyklucz słowo, które zmienia intencję (np. „tanio”, „używany”), a nie słowo produktu; jeśli takiego słowa nie ma, nie wykluczaj, tylko powiedz to użytkownikowi.
- Nie wykluczaj słów, które występują w nazwach albo zastosowaniach produktów z oferty, ani haseł z konwersją i słów, z których się składają.
- W kampaniach Shopping nie wykluczaj „jaki” ani „najlepszy”: tak pytają kupujący, którzy porównują produkty.
- Jedno kliknięcie bez jasnej intencji to szum. Nie wykluczaj.
- Wykluczaj jedno słowo w dopasowaniu do wyrażenia zamiast całej frazy: „ekspres” zamiast „ekspres do kawy”. Jedno słowo zamyka całą rodzinę zapytań.
- Wykluczające słowa kluczowe nie łapią odmian ani literówek: „ekspres” nie zablokuje „ekspresy” ani „ekspresu”. Wypisz osobno każdą formę z raportu, którą trzeba zablokować. Ta sama zasada chroni hasła z konwersją: „ekspres” nie zablokuje „kawa do ekspresu”. Przed każdym słowem sprawdź, czy dokładnie ta forma nie występuje w haśle z konwersją.
- Jeśli nietrafione hasła (według Twojej oceny, nie tylko te z „?”) to mniej niż 5% kosztu i nie ma oczywistych kandydatów, powiedz to i nie proponuj zmian.
- Hasło z konwersją bez znaku „+” (nie jest jeszcze słowem kluczowym) to kandydat do dodania jako słowo kluczowe w kampanii Search.
- Raport pokazuje tylko część kliknięć. Jeśli skrypt podał, jaką część widać, napisz to przy wyniku.

## 4. Wynik

W czacie, krótko i prostym językiem:

1. Koszt i konwersje na kampanię oraz jaką część kliknięć widać w raporcie.
2. Ile kosztowały nietrafione hasła: kwota i procent kosztu.
3. Wykluczenia w tabeli: słowo, powód, ile kosztowało w okresie raportu. Pod tabelą sama lista do wklejenia w Google Ads (wykluczające słowa kluczowe w kampanii albo na wspólnej liście), każde słowo w osobnej linii w cudzysłowie, bo cudzysłów oznacza dopasowanie do wyrażenia:

   ```
   "ekspres"
   "ekspresy"
   ```

4. Hasła do dodania jako słowa kluczowe.
5. Czego nie ruszasz i dlaczego, np. „najlepsza kawa” w Shoppingu.

Na końcu przypomnij, że zmiany wprowadza użytkownik, a następny przegląd ma sens za ok. 2 tygodnie.
