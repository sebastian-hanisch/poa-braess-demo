# 🛣️ Preis der Anarchie & Braess-Paradox – warum eine zusätzliche Straße alle langsamer machen kann

Zweites Stück der **Spieltheorie-&-Mechanism-Design-Linie** der "Konzepte"-Reihe im Portfolio von
[Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning. Nachfolger von
[nash-demo](https://sebastianhanisch-nash-demo.streamlit.app/): dort ging es darum, ob Best-Response ein Gleichgewicht findet und wie viele
es gibt – hier darum, **wie gut oder schlecht** es ist. Eigennutz ist dabei eine Modellannahme, kein Befund über echte Terminals.

## Warum dieses Problem

Wenn jeder Lkw für sich den schnellsten Weg wählt, entsteht ein Nash-Gleichgewicht – aber nicht unbedingt ein gutes. Der **Preis der
Anarchie** misst, wie viel schlechter das *schlechteste* Gleichgewicht ist als die beste denkbare Zuordnung. Das **Braess-Paradox**
(Braess 1968) ist der Extremfall: Öffnet man eine zusätzliche Abkürzung, wählen alle Lkw sie – und alle brauchen länger als vorher.

## Modell

**Braess-Netz** (`poa_network.py`): vier Knoten *s*, *A*, *B*, *t*, fünf Kanten mit affiner Fahrzeit $a_e + b_e x_e$ ($x_e$ = Lkw auf der Kante).
*s→A* und *B→t* sind lastabhängig ($b$ Minuten je Lkw), die Umwege *A→t* und *s→B* haben die feste Fahrzeit $c$, die Abkürzung *A→B* die feste Fahrzeit $e$.
Drei Wege: *s→A→t*, *s→B→t* und *s→A→B→t*. Alle Lkw sind gleich groß, deshalb genügt die Anzahl je Weg – alle Gleichgewichte lassen sich bis 40 Lkw
**exakt aufzählen**. Regler: Lkw-Zahl, $c/(b\,n)$, $e/(b\,n)$, Abkürzung offen/gesperrt.

**Torwahl-Vehikel** (`poa_gates.py`): wortgleich aus [nash-demo](https://github.com/sebastian-hanisch/nash-demo) übernommen (Tore mit Wartezeit
$a_g + b_g \cdot$ Last, Lkw mit Größe 1, 2 oder 3), samt Vollaufzählung aller reinen Gleichgewichte – dort ist der Preis der Anarchie das Verhältnis von
schlechtestem Gleichgewicht zu Optimum.

## Methodik

- **Best-Response** im Netz: ein Lkw nach dem anderen wechselt zu seinem schnellsten Weg (bei Gleichstand bleibt er). Weil das Spiel ein Potenzialspiel ist (Rosenthal 1973),
  endet das immer in einem Gleichgewicht.
- **Gleichgewichte** werden nicht aus der Dynamik gewonnen, sondern aus der Definition aufgezählt; ein Test prüft die Zähltupel-Fassung gegen die Einzel-Lkw-Fassung
  über alle $3^n$ Zuordnungen.
- **Optimum** = kleinste Summe der Fahrzeiten über alle Zustände.
- **Schranken aus der Literatur** (per Recherche geprüft, nicht im Test nachbewiesen): $4/3$ für unendlich viele infinitesimal kleine Fahrer (Roughgarden/Tardos 2002),
  $5/2$ für endlich viele gleich große Spieler und $(3+\sqrt5)/2 \approx 2{,}618$ für verschieden große (Christodoulou/Koutsoupias 2005, Awerbuch/Azar/Epstein 2005).
- **Gezielte Suche** nach schlechten Torwahl-Instanzen: beste von 200 Zufallsinstanzen, dann 3000 Hill-Climbing-Schritte über beliebige Tor-Parameter.

## Befunde (gemessen, keine Behauptungen)

| Frage | Befund | Test |
|---|---|---|
| Wann schadet die Abkürzung? | Bei 20 Lkw und kostenloser Abkürzung verschlechtert sie das schlechteste Gleichgewicht für $c/(b\,n)$ von 0,55 bis 1,45; bei 1,5 ändert sie nichts, ab 1,55 hilft sie. Analytisch: alle auf der Abkürzung ist Gleichgewicht genau für $c \ge b\,n$, ohne Abkürzung braucht jeder $b\,n/2 + c$, die Abkürzung schadet also für $b\,n \le c < 1{,}5\,b\,n$ (dazu kommt ein Bereich mit gemischten Gleichgewichten darunter). | `test_braess_window_bounds_and_peak` |
| Wie groß wird der Preis der Anarchie im Netz? | Maximum bei $c = b\,n$: genau 4/3 (20 → 15 min ohne, 20 min mit Abkürzung je Lkw), für 4, 12 und 40 Lkw gleich. Nie darüber. | `test_braess_ratio_is_four_thirds_for_every_size` |
| Standardinstanz (12 Lkw, Seed 7) | Best-Response endet nach 4 Wechseln bei 11,1 min je Lkw; schlechtestes Gleichgewicht mit Abkürzung 12,0, ohne 9,0 min (+33 %). Gesperrt: 2 Wechsel, 6/6 Lkw, 9,0 min. | `test_standardfall_numbers`, `test_gesperrt_numbers` |
| Hilft es, die Abkürzung teurer zu machen? | Nur teilweise: mit $e = 0{,}3\,b\,n$ ist das Gleichgewicht eindeutig (4/4/4 Lkw), aber mit 9,9 min noch schlechter als ohne (9,0); erst ab $e = 0{,}5\,b\,n$ gleichauf. | `test_aufwand_numbers`, `test_shortcut_with_own_cost_can_still_hurt_but_not_from_e_half` |
| Schadet jede neue Straße? | Nein. In 300 Zufallsnetzen mit beliebigen Kantenwerten schadet die Abkürzung dem erreichten Gleichgewicht nur in 3,3 % der Netze (nie um mehr als 5 %), ändert in 88,3 % nichts und hilft in 8,3 %. In Netzen von Braess-Bauart (Zufahrten lastabhängig, Umwege konstant) schadet sie in 48,3 % (in 33,3 % um mehr als 5 %, höchstens 26,4 %), hilft in 33,0 %. Das Paradox hängt an der Netz-Struktur. | `test_random_networks_free_vs_shaped` |
| Wie schlecht ist das Torwahl-Spiel? | Zufällige Vehikel-Instanzen (6 Lkw, 3 Tore): Preis der Anarchie im Mittel 1,058 (gemischte Größen, Maximum 1,155) und 1,023 (einheitliche Größen, Maximum 1,163). | `test_random_instances_stay_close_to_one` |
| Und im schlimmsten Fall? | Die gezielte Suche findet 1,62 (gemischte) und 1,32 (einheitliche Größen) – weit unter den allgemeinen Schranken 2,618 und 5/2. Das sind Ergebnisse dieser Suche, keine bewiesenen Grenzen; die Schranken gelten für beliebige Strategiemengen, das Torwahl-Spiel ist der Sonderfall paralleler Wege. Die Suche überschreitet die Schranken nie. | `test_targeted_search_beats_random_but_stays_far_below_the_bounds`, `test_search_never_exceeds_the_theoretical_bounds` |

## Ehrliche Grenzen

| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Alle Lkw sind im Netz gleich groß** | Bei verschieden großen Lkw steigt die Schranke von 5/2 auf 2,618; im Torwahl-Spiel zeigt die Suche höhere Werte als bei einheitlichen Größen. | – |
| **Ein festes Netz mit vier Knoten** | Das Paradox tritt in vielen Netzen auf, aber nicht in jedem (siehe Zufallsnetze). Die Demo betrachtet nur diese eine Form. | – |
| **Affine Fahrzeiten** | Bei stärker überlastungsabhängigen Kosten wächst der Preis der Anarchie über alle Grenzen. Hier nicht untersucht. | – |
| **Das Gleichgewicht sich selbst überlassen** | Wer das Ergebnis verbessern will, kann von außen eingreifen, etwa mit Preisen, die die Kosten für andere einpreisen. | Maut / Grenzkosten-Preise (nächstes Stück) |
| **Alle entscheiden gleichzeitig, keiner legt sich fest** | Ein Anführer, der sich zuerst festlegt, kann das Ergebnis lenken. | Stackelberg |
| **Jeder kennt alle Fahrzeiten und reagiert perfekt** | Ohne dieses Wissen bleibt nur Lernen aus der eigenen Erfahrung. | No-Regret-Lernen |

Nur **reine** Gleichgewichte. Die Suche nach schlechten Torwahl-Instanzen ist ein einfacher Hill Climber mit festem Seed; ein stärkerer Suchalgorithmus könnte höhere Werte finden.
Bei Gleichstand bleibt ein Lkw, deshalb gibt es im Netz oft mehrere fast gleich gute Gleichgewichte (ein Tupel mit einem oder zwei Lkw mehr oder weniger auf den Umwegen).

Verwandt: [nash-demo](https://sebastianhanisch-nash-demo.streamlit.app/) (Vorgänger), `marl-demo` (Agenten lernen ohne Gleichgewichtswissen).

## Tests

Pytest-Suite (`pytest tests/ -v`): Netz-Kosten und Gleichgewichte per Handrechnung (4 Lkw, $b=1$, $c=4$), Zähltupel gegen Einzel-Lkw-Definition, Best-Response endet
in einem aufgezählten Gleichgewicht, Torwahl-Vehikel gegen die Zahlen aus nash-demo und gegen eine skalare Definition, AppTest-Rauchtests (jedes Preset, Zug-Slider inkl. Abspielen,
Permalink-Grenzen, Urteil je nach Umweg-Zeit, drei Experimente auf Abruf) und `test_claims.py` (jede Zahl aus diesem README; Mehr-Instanzen-Zahlen mit großzügigen Bändern).

## Dateistruktur

| Datei | Inhalt |
|---|---|
| `app.py` | Streamlit-Einstiegspunkt |
| `poa_constants.py` | Regler-Grenzen, Netz- und Vehikel-Konstanten, Experiment-Seeds, Schranken, Presets |
| `poa_presets.py` | Permalink/Presets-Mechanik |
| `poa_network.py` | Braess-Netz, Zähltupel, Gleichgewichte, Optimum, Best-Response |
| `poa_gates.py` | Torwahl-Vehikel und Vollaufzählung (aus nash-demo) |
| `poa_evaluation.py` | Analyse eines Laufs, Braess-Fenster, Zufallsnetze, Preis der Anarchie im Torwahl-Spiel |
| `poa_visualization.py` | Plotly-Abbildungen |

## Bewusst nicht umgesetzt

- Beliebige Netze (nur die Braess-Form) und nicht-affine Fahrzeiten.
- Gemischte Gleichgewichte und die Korrelierten Gleichgewichte (spätere Stücke der Linie).
- Eingriffe wie Maut oder Kapazitätsanpassungen – das ist das nächste Stück.
- Ein PDF-Export – wie bei den anderen Konzepte-Demos dieses Portfolios nicht Teil der Linie.

## Lokal ausführen

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements-dev.txt
streamlit run app.py
```

Gebaut mit Streamlit, Plotly und numpy.
