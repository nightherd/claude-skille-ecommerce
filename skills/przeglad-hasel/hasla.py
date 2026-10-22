#!/usr/bin/env python3
"""Przegląd wyszukiwanych haseł z eksportu CSV Google Ads (tylko odczyt).

  python3 hasla.py raport.csv [ZYSK_Z_ZAMOWIENIA]

Czyta raport „Wyszukiwane hasła” pobrany z Google Ads (panel po polsku albo po
angielsku, CSV albo CSV dla Excela) i wypisuje koszt na kampanię, hasła
z konwersją i hasła bez konwersji według kosztu.

Znaczniki: „?” podejrzane według prostego wzorca (pytania, „opinie”, „forum”,
„za darmo”, obce alfabety), to tylko podpowiedź; „+” hasło jest już słowem
kluczowym; „W” hasło jest już wykluczone; „!” brak konwersji przy koszcie
powyżej 3 × zysk z zamówienia (gdy podasz zysk).
"""
import collections
import csv
import re
import sys
from pathlib import Path

KOLUMNY = {  # nagłówki eksportu po polsku i po angielsku, małymi literami
    "haslo": {"wyszukiwane hasło", "search term"},
    "klikniecia": {"kliknięcia", "clicks"},
    "koszt": {"koszt", "cost"},
    "konwersje": {"konwersje", "conversions"},
    "kampania": {"kampania", "campaign"},
    "status": {"dodane/wykluczone", "added/excluded"},
    "waluta": {"kod waluty", "currency code"},
}
WYMAGANE = ("haslo", "klikniecia", "koszt", "konwersje")
SUMA = re.compile(r"(total|razem|łącznie|suma)\s*:", re.I)  # wiersze sum pod tabelą, np. „Total: Account”
# ponytail: naiwny wzorzec podpowiedzi; gdy zacznie mylić, dopisać słowa, nie budować klasyfikatora
PODEJRZANE = re.compile(
    r"\b(jak|czym|czy|co|ile|gdzie|dlaczego|forum|opinie|opinia|test|ranking\w*|darmow\w*|"
    r"przepis\w*|praca|pracy|hurt\w*|używan\w*|allegro|olx|"
    r"how|what|why|where|free|reviews?|reddit|diy|jobs?|used)\b", re.I)
LIMIT = 150  # ponytail: tyle haseł bez konwersji na wyjściu, reszta jako jedna suma; wyżej zapcha czat


def podejrzane(haslo):
    return bool(PODEJRZANE.search(haslo)) or any(c.isalpha() and ord(c) > 0x24F for c in haslo)


def liczba(tekst, pl):
    t = re.sub(r"[^\d,.]", "", tekst)  # spacje tysięcy, „zł”, „%”
    if pl and "," in t:
        t = t.replace(".", "").replace(",", ".")
    elif not pl:
        t = t.replace(",", "")
    try:
        return float(t)
    except ValueError:
        return 0.0  # „--” albo puste pole


def wczytaj(sciezka):
    """Zwraca nagłówek (małymi literami) i wiersze pod nim."""
    dane = Path(sciezka).read_bytes()
    if dane[:2] in (b"\xff\xfe", b"\xfe\xff"):
        tekst = dane.decode("utf-16")  # „CSV dla Excela” z Google Ads
    else:
        try:
            tekst = dane.decode("utf-8-sig")
        except UnicodeDecodeError:
            tekst = dane.decode("cp1250")  # plik zapisany ponownie w polskim Excelu
    linie = tekst.splitlines()
    for i, linia in enumerate(linie[:30]):  # nad nagłówkiem bywa tytuł raportu i zakres dat
        for sep in ",;\t":
            komorki = [k.strip().lower() for k in next(csv.reader([linia], delimiter=sep), [])]
            if KOLUMNY["haslo"] & set(komorki):
                return komorki, list(csv.reader(linie[i + 1:], delimiter=sep))
    sys.exit("Nie widzę kolumny „Wyszukiwane hasło” ani „Search term”. To raport wyszukiwanych haseł z Google Ads?")


def policz(sciezka):
    """Zwraca (hasła, kampanie, kliknięcia z wierszy sum, waluta).

    hasła: {hasło: [kliknięcia, koszt, konwersje, {kampanie}, „+” / „W” / „”]}
    kampanie: {kampania: [kliknięcia, koszt, konwersje]}
    """
    naglowek, wiersze = wczytaj(sciezka)
    kol = {n: next((i for i, k in enumerate(naglowek) if k in w), None) for n, w in KOLUMNY.items()}
    brak = [n for n in WYMAGANE if kol[n] is None]
    if brak:
        sys.exit(f"Brakuje kolumn: {', '.join(brak)}. Nagłówek pliku: {naglowek}")
    pl = "wyszukiwane hasło" in naglowek
    ostatnia = max(i for i in kol.values() if i is not None)

    def pole(w, nazwa, domyslne=""):
        return w[kol[nazwa]].strip() if kol[nazwa] is not None else domyslne

    hasla = collections.defaultdict(lambda: [0.0, 0.0, 0.0, set(), ""])
    kampanie = collections.defaultdict(lambda: [0.0, 0.0, 0.0])
    sumy, waluta = [], ""
    for w in wiersze:
        if len(w) <= ostatnia:
            continue
        haslo = pole(w, "haslo")
        liczby = [liczba(pole(w, n), pl) for n in ("klikniecia", "koszt", "konwersje")]
        if SUMA.match(w[0].strip()) or SUMA.match(haslo):
            sumy.append(liczby[0])
            continue
        if not haslo:
            continue
        kampania = pole(w, "kampania", "(cały plik)")
        waluta = waluta or pole(w, "waluta")
        h, k = hasla[haslo], kampanie[kampania]
        for i, v in enumerate(liczby):
            h[i] += v
            k[i] += v
        h[3].add(kampania)
        status = pole(w, "status").lower()
        if status.startswith(("dodan", "added")):
            h[4] = "+"
        elif status.startswith(("wyklucz", "excluded")) and h[4] != "+":
            h[4] = "W"
    return dict(hasla), dict(kampanie), sumy, waluta


def wypisz(sciezka, zysk=None):
    hasla, kampanie, sumy, waluta = policz(sciezka)
    widoczne = sum(h[0] for h in hasla.values())
    koszt = sum(h[1] for h in hasla.values())
    print(f"{Path(sciezka).name}: hasła {len(hasla)}, kliknięcia {widoczne:.0f}, koszt {koszt:.2f} {waluta}".rstrip())
    if sumy and max(sumy) > widoczne:
        print(f"Raport pokazuje {widoczne:.0f} z {max(sumy):.0f} kliknięć ({100 * widoczne / max(sumy):.0f}%), resztę Google ukrywa.")

    print(f"\n{'Kampania':40} {'klik.':>6} {'koszt':>9} {'konw.':>6}")
    for nazwa, (kl, ko, kv) in sorted(kampanie.items(), key=lambda x: -x[1][1]):
        print(f"{nazwa[:40]:40} {kl:6.0f} {ko:9.2f} {kv:6g}")

    podejrz = sum(h[1] for k, h in hasla.items() if not h[2] and podejrzane(k))
    print(f"\nPodejrzane („?”) bez konwersji: {podejrz:.2f} z {koszt:.2f} ({100 * podejrz / koszt if koszt else 0:.0f}% kosztu)")
    prog = 3 * zysk if zysk else None
    if prog:
        print(f"Próg: 3 × {zysk:g} = {prog:g}; „!” = bez konwersji i koszt powyżej progu")

    def linia(znak, k, h, konw=True):
        dopisek = f"  konw. {h[2]:g}" if konw else ""
        print(f"{znak} {k[:50]:50} klik. {h[0]:4.0f}  koszt {h[1]:8.2f}{dopisek}  [{', '.join(sorted(h[3]))}]")

    print("\n## Z konwersją (nie wykluczać; bez „+” = kandydat na słowo kluczowe)")
    for k, h in sorted(hasla.items(), key=lambda x: -x[1][2]):
        if h[2]:
            linia(f"{h[4] or ' ':2} ", k, h)

    print("\n## Bez konwersji według kosztu („?” podejrzane, „+” słowo kluczowe, „W” wykluczone, „!” ponad próg)")
    bez = sorted(((k, h) for k, h in hasla.items() if not h[2]), key=lambda x: -x[1][1])
    for k, h in bez[:LIMIT]:
        znak = ("?" if podejrzane(k) else " ") + (h[4] or " ") + ("!" if prog and h[1] > prog else " ")
        linia(znak, k, h, konw=False)
    if len(bez) > LIMIT:
        print(f"... pozostałe hasła: {len(bez) - LIMIT}, razem {sum(h[1] for _, h in bez[LIMIT:]):.2f}, każde tańsze od powyższych")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    wypisz(sys.argv[1], float(sys.argv[2].replace(",", ".")) if len(sys.argv) > 2 else None)
