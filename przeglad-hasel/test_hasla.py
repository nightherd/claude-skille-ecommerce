#!/usr/bin/env python3
"""Test na przykładowym pliku i na eksporcie z angielskiego panelu: python3 test_hasla.py"""
import tempfile
from pathlib import Path

import hasla

TU = Path(__file__).parent


def test_przyklad():
    h, kampanie, sumy, waluta = hasla.policz(TU / "przyklad" / "sklep-z-kawa.csv")
    assert len(h) == 44 and waluta == "PLN"
    assert round(sum(x[1] for x in h.values()), 2) == 1362.0
    assert sum(x[2] for x in h.values()) == 20
    assert h["kawa ziarnista 1kg"][:3] == [61, 120.2, 4]  # to samo hasło w dwóch kampaniach
    assert h["kawa ziarnista"][4] == "+" and h["kawa ziarnista 1kg"][4] == ""
    assert h["kawa rozpuszczalna tania"][4] == "W"
    assert max(sumy) == 1052  # „1 052” z twardą spacją w wierszu „Razem: konto”
    assert round(kampanie["Kawa ziarnista (Search)"][1], 2) == 649.7
    assert hasla.podejrzane("jak parzyć kawę w dripie") and hasla.podejrzane("кава в зернах")
    assert not hasla.podejrzane("kawa ziarnista 1kg") and not hasla.podejrzane("najlepsza kawa ziarnista")


def test_eksport_angielski_dla_excela():
    # „CSV dla Excela”: UTF-16, tabulatory, kropka dziesiętna i przecinek tysięcy
    tekst = ("Search terms report\n\"October 1, 2026 - October 14, 2026\"\n"
             "Search term\tAdded/Excluded\tCampaign\tCurrency code\tCost\tClicks\tConversions\n"
             "coffee beans\tAdded\tSearch\tEUR\t1,234.50\t1,020\t12.00\n"
             "free coffee\tNone\tSearch\tEUR\t3.10\t2\t0.00\n"
             "Total: Account\t--\t--\t--\t1,300.00\t1,100\t12.00\n")
    with tempfile.TemporaryDirectory() as d:
        plik = Path(d) / "report.csv"
        plik.write_text(tekst, encoding="utf-16")
        h, kampanie, sumy, waluta = hasla.policz(plik)
    assert h["coffee beans"][:3] == [1020, 1234.5, 12] and h["coffee beans"][4] == "+"
    assert round(kampanie["Search"][1], 2) == 1237.6
    assert sumy == [1100] and waluta == "EUR"
    assert hasla.podejrzane("free coffee")


if __name__ == "__main__":
    test_przyklad()
    test_eksport_angielski_dla_excela()
    print("OK")
