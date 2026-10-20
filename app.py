"""Preis der Anarchie & Braess-Paradox - warum eine zusätzliche Straße alle langsamer machen kann - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Zweites Stück der Linie "Spieltheorie & Mechanism Design" der "Konzepte"-Reihe (Nachfolger von nash-demo): das Gleichgewicht ist nicht optimal -
wie schlecht kann es werden, und wann macht mehr Kapazität es schlechter?

Lauffähig mit: streamlit run app.py
"""

import time

import numpy as np
import streamlit as st

import poa_constants as C
import poa_network as N
from poa_evaluation import Settings, analyse, network_experiment, poa_random, poa_search, window_experiment
from poa_presets import apply_preset, bounds, init_session_state_defaults, load_permalink_settings, randomize_seed, sync_query_params
from poa_visualization import build_network, build_network_experiment, build_poa_distribution, build_search_curve, build_social_curve, build_window

st.set_page_config(page_title="Preis der Anarchie & Braess – Sebastian Hanisch", layout="wide")


def de(x, digits=1):
    """Deutsche Zahlenschreibweise: Punkt als Tausendertrenner, Komma als Dezimalzeichen."""
    return f"{x:,.{digits}f}".replace(",", "#").replace(".", ",").replace("#", ".")


def pct(x, digits=0):
    return f"{de(100 * x, digits)} %"


@st.cache_data(show_spinner=False)
def _window():
    return window_experiment()


@st.cache_data(show_spinner=False)
def _networks(mode):
    return network_experiment(mode)


@st.cache_data(show_spinner=False)
def _poa():
    random_mixed, random_uniform = poa_random("mixed"), poa_random("uniform")
    search_w, search_u = poa_search(True), poa_search(False)
    return random_mixed, random_uniform, search_w, search_u


st.title("🛣️ Preis der Anarchie & Braess-Paradox – warum eine zusätzliche Straße alle langsamer machen kann")
st.markdown(
    """
Wenn jeder Lkw für sich den schnellsten Weg wählt, entsteht ein **Nash-Gleichgewicht** - aber nicht unbedingt ein gutes. Der **Preis der Anarchie** misst, wie viel
schlechter das *schlechteste* Gleichgewicht ist als die beste denkbare Zuordnung. Das **Braess-Paradox** ist der Extremfall: Öffnet man eine zusätzliche Abkürzung, wählen
alle Lkw sie - und alle brauchen länger als vorher. Diese Demo zeigt beides: an einem kleinen Straßennetz mit exakt aufgezählten Gleichgewichten und am Torwahl-Spiel
aus der Vorgänger-Demo.
"""
)

# erklaerseite:einfach:start (erzeugt von tools/set_demo_explainer.py (Website-Repo) aus tools/content/explainers/braess-paradox-erklaert.json, nicht von Hand ändern)
with st.expander("💬 In einfachen Worten"):
    st.markdown(
        """
Wenn jeder Lkw für sich den schnellsten Weg wählt, entsteht ein Gleichgewicht, in dem kein einzelner mehr wechseln will. Gut für alle ist es nicht unbedingt. Der **Preis der Anarchie** misst, um wie viel schlechter das schlechteste Gleichgewicht ist als die beste denkbare Zuordnung. Das **Braess-Paradox** ist der Extremfall: Öffnet man in einem kleinen Straßennetz eine zusätzliche Abkürzung, wählen alle Lkw sie, und alle brauchen länger als vorher. Die Demo zählt alle Gleichgewichte exakt auf, zeigt, bei welcher Länge der Umwege die Abkürzung schadet, und vergleicht Zufallsnetze mit Netzen von Braess-Bauart. Es ist ein kleines Modell, und Eigennutz ist darin eine Annahme, kein Befund über echte Terminals.

[Ausführlich und verständlich erklärt, mit Fachteil](https://sebastianhanisch.net/braess-paradox-erklaert.html)
        """
    )
# erklaerseite:einfach:end
st.caption(
    "Zweites Stück der Linie \"Spieltheorie & Mechanism Design\" der \"Konzepte\"-Reihe, Nachfolger von **nash-demo**: dort ging es darum, ob Best-Response ein Gleichgewicht "
    "findet und wie viele es gibt - hier darum, wie gut oder schlecht es ist. Eigennutz ist dabei eine Modellannahme, kein Befund über echte Terminals."
)

with st.expander("So funktioniert das Braess-Netz", expanded=True):
    st.markdown(
        """
1. **Das Netz.** Vier Knoten *s* (Start), *A*, *B*, *t* (Ziel). Die Kanten *s→A* und *B→t* sind lastabhängig (jeder Lkw darauf verlängert die Fahrzeit um *b* Minuten); die Umwege
   *A→t* und *s→B* haben eine feste Fahrzeit *c*. Ohne Abkürzung gibt es zwei Wege (*s→A→t*, *s→B→t*).
2. **Die Abkürzung.** Öffnet man die Kante *A→B*, kommt ein dritter Weg *s→A→B→t* dazu, der beide lastabhängigen Kanten nutzt.
3. **Gleichgewicht.** Jeder Lkw wählt den für ihn schnellsten Weg, bei Gleichstand bleibt er. Wegen gleicher Lkw genügt die Anzahl je Weg - alle Gleichgewichte lassen sich exakt aufzählen.
4. **Preis der Anarchie.** Schlechtestes Gleichgewicht geteilt durch das Optimum (kleinste Summe der Fahrzeiten). 1 = Eigennutz kostet nichts.
        """
    )

st.caption("🎯 Schnellstart – ein Beispielszenario laden:")
preset_names = list(C.PRESETS.keys())
for row in (preset_names[:3], preset_names[3:]):
    cols = st.columns(len(row))
    for col, name in zip(cols, row):
        with col:
            st.button(name, width="stretch", on_click=apply_preset, args=(name,), help=C.PRESET_HELP[name], key=f"preset_{name}")

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    st.header("⚙️ Einstellungen")
    n_trucks = st.slider("Lkw", *bounds("n_slider"), key="n_slider", step=C.N_STEP, help="Anzahl der Lkw (alle gleich groß), die einen Weg wählen.")
    c_rel = st.slider("Umweg-Fahrzeit c / (b · n)", *bounds("crel_slider"), key="crel_slider", step=C.CREL_STEP, format="%.2f",
                      help="Feste Fahrzeit der Umwege A→t und s→B im Verhältnis zur Fahrzeit, die die lastabhängigen Kanten bei voller Auslastung hätten.")
    e_rel = st.slider("Abkürzung: eigene Fahrzeit e / (b · n)", *bounds("erel_slider"), key="erel_slider", step=C.EREL_STEP, format="%.2f",
                      help="Feste Fahrzeit der Abkürzung A→B. 0 = die Abkürzung ist kostenlos.")
    shortcut = st.selectbox("Abkürzung", C.SHORTCUT_MODES, key="shortcut_select", format_func=lambda k: C.SHORTCUT_LABELS[k])
    order = st.selectbox("Reihenfolge der Best-Response", C.ORDERS, key="order_select", format_func=lambda k: C.ORDER_LABELS[k])
    seed = st.number_input("Zufalls-Seed der Startzuordnung", *bounds("seed_input"), key="seed_input", step=1, help="Legt die zufällige Anfangs-Wegwahl (und zufällige Reihenfolgen) fest.")
    st.button("🎲 Neue Startzuordnung würfeln", width="stretch", on_click=randomize_seed)

sync_query_params({"n_slider": int(n_trucks), "crel_slider": float(c_rel), "erel_slider": float(e_rel), "shortcut_select": shortcut, "order_select": order, "seed_input": int(seed)})

settings = Settings(int(n_trucks), float(c_rel), float(e_rel), shortcut, order, int(seed))
a = analyse(settings)
net, run = a.net, a.run
n = net.n
is_open = a.shortcut_open
n_steps = len(run.states) - 1
history = [x / n for x in a.social_history]
worst_open, worst_closed = a.worst_cost(True) / n, a.worst_cost(False) / n
opt_open = a.opt_open[1] / n
opt_closed = a.opt_closed[1] / n

# --- Best-Response im Netz -----------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Best-Response im Netz")
if "poa_step" not in st.session_state or st.session_state.get("poa_step_owner") != settings:
    st.session_state["poa_step"] = n_steps
    st.session_state["poa_step_owner"] = settings
step_col, play_col = st.columns([5, 2])
with step_col:
    step = st.slider("Zug", 0, n_steps, key="poa_step", help="0 = Startzuordnung.") if n_steps > 0 else 0
with play_col:
    auto_play = st.button("▶️ Abspielen", width="stretch", disabled=n_steps == 0)
if n_steps == 0:
    st.info("Die zufällige Startzuordnung ist bereits ein Gleichgewicht - kein Lkw will wechseln. Andere Startzuordnung würfeln oder eine andere Lkw-Zahl wählen.")
view_slot = st.empty()


def _render(s):
    with view_slot.container():
        c1, c2 = st.columns([3, 2])
        counts = N.counts_of(run.states[s])
        head = "Startzuordnung" if s == 0 else f"Zug {s} von {n_steps}"
        c1.markdown(f"**{head} – mittlere Fahrzeit: {de(history[s])} min je Lkw**")
        c1.plotly_chart(build_network(net, counts, is_open), width="stretch", key=f"poa_net_{s}")
        c2.markdown("**Lkw je Weg**")
        rows = {"Weg": list(N.PATH_LABELS[:N.n_paths(is_open)]), "Lkw": list(counts[:N.n_paths(is_open)]),
                "Fahrzeit (min)": [de(x) for x in N.path_costs(net, counts)[:N.n_paths(is_open)]]}
        c2.dataframe(rows, hide_index=True)
        c2.plotly_chart(build_social_curve(history, n, upto=s, reference=opt_open if is_open else opt_closed), width="stretch", key=f"poa_curve_{s}")
        if s > 0:
            i, p, q = run.moves[s - 1]
            c2.caption(f"Lkw {i + 1} wechselt von Weg {p + 1} zu Weg {q + 1}.")


def _frames():
    if n_steps == 0:
        return [0]
    return sorted({int(round(x)) for x in np.linspace(0, n_steps, min(n_steps + 1, 40))})


if auto_play:
    for f in _frames():
        _render(f)
        time.sleep(0.25)
else:
    _render(step)

st.markdown("---")

# --- Ergebnis -------------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Was das Gleichgewicht kostet")
reached = history[-1]
m1, m2, m3, m4 = st.columns(4)
m1.metric("Erreichtes Gleichgewicht", f"{de(reached)} min", help=f"Mittlere Fahrzeit je Lkw nach {len(run.moves)} Wechseln (Best-Response von der Startzuordnung).")
m2.metric("Schlechtestes Gleichgewicht mit Abkürzung", f"{de(worst_open)} min", help=f"Unter {len(a.eq_open)} Gleichgewichten (Vollaufzählung).")
m3.metric("Schlechtestes Gleichgewicht ohne Abkürzung", f"{de(worst_closed)} min", help=f"Unter {len(a.eq_closed)} Gleichgewichten (Vollaufzählung).")
m4.metric("Optimum mit Abkürzung", f"{de(opt_open)} min", delta=f"Preis der Anarchie {de(worst_open / opt_open, 3)}", delta_color="off",
          help="Kleinste mittlere Fahrzeit über alle Zuordnungen, gesteuert von außen. Preis der Anarchie = schlechtestes Gleichgewicht / Optimum.")

if worst_open > worst_closed + 1e-9:
    st.warning(f"⚠️ **Braess-Paradox:** Mit der Abkürzung brauchen im schlechtesten Gleichgewicht alle {de(worst_open)} min statt {de(worst_closed)} min "
               f"({pct(worst_open / worst_closed - 1)} mehr). Jeder einzelne Lkw wählt die Abkürzung, weil sie für ihn kurzfristig besser ist - gemeinsam verlieren sie.")
elif worst_open < worst_closed - 1e-9:
    st.success(f"✅ Die Abkürzung hilft: {de(worst_open)} statt {de(worst_closed)} min je Lkw im schlechtesten Gleichgewicht.")
else:
    st.info(f"Kein Unterschied: mit und ohne Abkürzung {de(worst_open)} min je Lkw im schlechtesten Gleichgewicht.")

st.markdown("**Alle Gleichgewichte** (Vollaufzählung der Zähltupel Lkw je Weg)")
eq_rows = [(s, True) for s in a.eq_open] + [(s, False) for s in a.eq_closed]
st.dataframe(
    {"Netz": ["mit Abkürzung" if o else "ohne Abkürzung" for _, o in eq_rows],
     "Lkw auf s→A→t": [s[0] for s, _ in eq_rows], "Lkw auf s→B→t": [s[1] for s, _ in eq_rows], "Lkw über die Abkürzung": [s[2] for s, _ in eq_rows],
     "Mittlere Fahrzeit (min)": [de(N.social(net, s) / n, 2) for s, _ in eq_rows]},
    hide_index=True,
)
st.caption("Bei Gleichstand bleibt ein Lkw, deshalb kann es mehrere, fast gleich gute Gleichgewichte geben.")

st.markdown("---")

# --- Experiment 1: Braess-Fenster ---------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Wann schadet die Abkürzung? Das Braess-Fenster")
st.caption(f"{C.WINDOW_N} Lkw, kostenlose Abkürzung (e = 0); Umweg-Fahrzeit c von {de(C.WINDOW_CRELS[0], 2)} bis {de(C.WINDOW_CRELS[-1], 2)} mal b·n. Schlechtestes Gleichgewicht je Fall, exakt aufgezählt.")
if st.button("Fenster berechnen", key="window_start"):
    st.session_state["window_on"] = True
if st.session_state.get("window_on"):
    rows_w = _window()
    st.plotly_chart(build_window(rows_w), width="stretch", key="window_chart")
    hurt = [r["c_rel"] for r in rows_w if r["with_worst"] > r["without"] + 1e-9]
    help_ = [r["c_rel"] for r in rows_w if r["with_worst"] < r["without"] - 1e-9]
    peak = max(rows_w, key=lambda r: r["poa_with"])
    st.warning(
        f"**Befund:** Die Abkürzung verschlechtert das schlechteste Gleichgewicht für c von {de(min(hurt), 2)} bis {de(max(hurt), 2)} mal b·n. Der Preis der Anarchie erreicht bei c = {de(peak['c_rel'], 2)} · b·n "
        f"sein Maximum von {de(peak['poa_with'], 3)} - genau die Schranke 4/3 für affine Kosten (Roughgarden und Tardos 2002). Bei kleinerem c wird die Abkürzung nicht gewählt oder ist harmlos; "
        f"ab c = {de(min(help_), 2)} · b·n hilft sie sogar."
    )

st.markdown("---")

# --- Experiment 2: zufällige Netze ---------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Wie oft schadet eine neue Abkürzung in einem Zufallsnetz?")
st.caption(f"Dieselbe Netzform, {C.NET_N} Lkw, {len(C.NET_SEEDS)} Zufallsnetze je Art mit zufälligen Kantenwerten. Verglichen wird das erreichte Gleichgewicht "
           "(Best-Response von einer Zufallszuordnung) mit gegen ohne Abkürzung.")
if st.button("Zufallsnetze vergleichen (dauert einige Sekunden)", key="networks_start"):
    st.session_state["networks_on"] = True
if st.session_state.get("networks_on"):
    with st.spinner("Rechne 600 Netze..."):
        res_nets = [_networks(mode) for mode in C.NET_MODES]
    st.plotly_chart(build_network_experiment(res_nets), width="stretch", key="networks_chart")
    free, shaped = res_nets
    st.warning(
        f"**Befund:** Bei beliebigen Kantenwerten schadet die Abkürzung nur in {pct(free['worse'])} der Netze, in {pct(free['same'])} ändert sie nichts und in {pct(free['better'])} hilft sie. "
        f"Erst wenn das Netz Braess-Bauart hat (Zufahrten lastabhängig, Umwege konstant), schadet sie in {pct(shaped['worse'])} - "
        f"in {pct(shaped['worse_5'])} um mehr als 5 %, im schlimmsten Fall um {pct(shaped['max_worse'])}; in {pct(shaped['better'])} hilft sie dagegen. Das Paradox ist an eine Struktur gebunden, "
        "keine Eigenschaft jeder neuen Straße."
    )

st.markdown("---")

# --- Experiment 3: Preis der Anarchie im Torwahl-Spiel -------------------------------------------------------------------------------------------

st.subheader(f"🔬 Preis der Anarchie im Torwahl-Spiel: Zufall gegen gezielte Suche gegen Schranke")
st.markdown(
    f"""
Für Überlastungsspiele mit affinen Kosten gibt es **Worst-Case-Schranken** für den Preis der Anarchie: **4/3** für unendlich viele infinitesimal kleine Fahrer
(Roughgarden und Tardos 2002), **5/2** für endlich viele gleich große Spieler und **(3 + √5)/2 ≈ {de(C.BOUND_WEIGHTED, 3)}** mit verschieden großen (Christodoulou und Koutsoupias 2005;
Awerbuch, Azar und Epstein 2005). Wie nah kommt man dem im Torwahl-Spiel der Vorgänger-Demo ({C.POA_N} Lkw, {C.POA_M} Tore)?
"""
)
st.caption(f"Schlechtestes reines Gleichgewicht / Optimum, exakt aufgezählt. Zufall: {len(C.POA_SEEDS)} Vehikel-Instanzen wie in nash-demo. Gezielte Suche: {C.SEARCH_RANDOM_STARTS} Zufallsinstanzen, danach "
           f"{C.SEARCH_STEPS} Hill-Climbing-Schritte über beliebige Tor-Parameter (nicht auf die Vehikel-Bereiche beschränkt).")
if st.button("Zufall und Suche vergleichen (dauert einige Sekunden)", key="poa_start"):
    st.session_state["poa_on"] = True
if st.session_state.get("poa_on"):
    with st.spinner("Rechne..."):
        r_mixed, r_uniform, s_w, s_u = _poa()
    st.plotly_chart(build_poa_distribution(r_mixed, r_uniform, s_w["best"], s_u["best"]), width="stretch", key="poa_dist")
    st.plotly_chart(build_search_curve(s_w["history"], s_u["history"]), width="stretch", key="poa_search")
    st.warning(
        f"**Befund:** Zufällige Instanzen liegen bei einem Preis der Anarchie von im Mittel {de(r_mixed['mean'], 3)} (gemischte Größen, Maximum {de(r_mixed['max'], 3)}) bzw. {de(r_uniform['mean'], 3)} "
        f"(einheitliche Größen, Maximum {de(r_uniform['max'], 3)}). Die gezielte Suche findet {de(s_w['best'], 2)} mit gemischten und {de(s_u['best'], 2)} mit einheitlichen Größen - "
        f"weit unter {de(C.BOUND_UNWEIGHTED, 1)} und {de(C.BOUND_WEIGHTED, 3)}. Die Schranken gelten für beliebige Strategiemengen (Netze mit vielen Wegen), das Torwahl-Spiel ist der "
        "Sonderfall paralleler Wege; hier bleibt der tatsächliche Wert deutlich darunter (für einheitliche Größen auffällig nahe an 4/3). Ein Beweis ist das nicht - nur die Messung dieser Suche."
    )

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Alle Lkw sind gleich groß** | Bei verschieden großen Lkw steigt die Schranke von 5/2 auf 2,618; im Torwahl-Spiel zeigt die Suche höhere Werte als bei einheitlichen Größen. | - |
| **Ein festes Netz mit vier Knoten** | Das Braess-Paradox tritt in vielen Netzen auf, aber nicht in jedem - das Experiment oben zeigt, wie stark es von der Bauart abhängt. Die Demo betrachtet nur diese eine Form. | - |
| **Affine Fahrzeiten** | Bei stärker überlastungsabhängigen Kosten (etwa Staufunktionen mit hohen Potenzen) wächst der Preis der Anarchie über alle Grenzen. Hier nicht untersucht. | - |
| **Das Gleichgewicht sich selbst überlassen** | Wer das Ergebnis verbessern will, kann von außen eingreifen - etwa mit Preisen, die die Kosten für andere einpreisen. | **Maut / Grenzkosten-Preise** (nächstes Stück) |
| **Alle entscheiden gleichzeitig, keiner legt sich fest** | Ein Anführer, der sich zuerst festlegt, kann das Ergebnis lenken. | **Stackelberg** |
| **Jeder kennt alle Fahrzeiten und reagiert perfekt** | Ohne dieses Wissen bleibt nur Lernen aus der eigenen Erfahrung. | **No-Regret-Lernen** |
"""
)
st.caption(
    "Verwandt: [nash-demo](https://sebastianhanisch-nash-demo.streamlit.app/) (Vorgänger: Best-Response im Torwahl-Spiel), [marl-demo](https://sebastianhanisch-marl-demo.streamlit.app/) "
    "(Agenten lernen ohne Gleichgewichtswissen)."
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    # erklaerseite:lesehilfe:start (erzeugt von tools/set_demo_explainer.py (Website-Repo) aus tools/content/explainers/braess-paradox-erklaert.json, nicht von Hand ändern)
    st.markdown(
        r"""
**Lesehilfe.** Gegeben sind $n$ gleiche Lkw, das Braess-Netz mit den Fahrzeitparametern $b$, $c$ und $e$ und die Wahl, die Abkürzung zu öffnen oder zu sperren. Gesucht sind die Gleichgewichte $NE$, die Summe der Fahrzeiten $SC(s)$ und der Preis der Anarchie $\mathrm{PoA}$.

| Symbol | Bedeutung |
|---|---|
| $a_e$, $b_e$ | feste und lastabhängige Fahrzeit der Kante $e$ (Fahrzeit $a_e + b_e x_e$) |
| $x_e$ | Zahl der Lkw auf der Kante $e$ |
| $b$ | Minuten je Lkw auf den lastabhängigen Kanten $sA$ und $Bt$ |
| $c$ | feste Fahrzeit der Umwege $At$ und $sB$ |
| $e$ | feste Fahrzeit der Abkürzung $AB$ (als Index: eine Kante) |
| $n$ | Zahl der Lkw |
| $P_1$, $P_2$, $P_3$ | Weg über $A$, Weg über $B$, Weg über die Abkürzung |
| $s$, $NE$ | Zustand (Zahl der Lkw je Weg), Menge der Gleichgewichte |
| $c_i(s)$, $SC(s)$ | Fahrzeit des Lkw $i$ im Zustand $s$, Summe der Fahrzeiten aller Lkw |
| $\mathrm{PoA}$ | Preis der Anarchie: schlechtestes Gleichgewicht geteilt durch Optimum |

[Schritt für Schritt erklärt, mit Herleitung und Literatur](https://sebastianhanisch.net/braess-paradox-erklaert.html#fachleute)
        """
    )
    # erklaerseite:lesehilfe:end
    st.markdown(
        r"""
**Braess-Netz.** Kanten $e \in \{sA, At, sB, Bt, AB\}$ mit Fahrzeit $a_e + b_e x_e$, $x_e$ = Zahl der Lkw auf der Kante. Wege $P_1 = (sA, At)$, $P_2 = (sB, Bt)$, $P_3 = (sA, AB, Bt)$.
Klassisch: $b_{sA} = b_{Bt} = b$, $a_{At} = a_{sB} = c$, $a_{AB} = e$, alle anderen 0.

**Preis der Anarchie.** $\mathrm{PoA} = \max_{s \in NE} SC(s) \,/\, \min_{s} SC(s)$ mit $SC(s) = \sum_i c_i(s)$ (Summe der Fahrzeiten).

**Wann steht alles auf der Abkürzung?** Alle $n$ Lkw auf $P_3$ haben je $2bn + e$. Wechselt einer auf $P_1$ oder $P_2$, braucht er $bn + c$. Also ist "alle auf $P_3$" genau dann ein Gleichgewicht,
wenn $c \ge bn + e$. Ohne Abkürzung teilen sich die Lkw zu gleichen Teilen auf $P_1$ und $P_2$ auf: $bn/2 + c$ je Lkw. Die Abkürzung schadet, sobald $2bn + e > bn/2 + c$,
bei $e = 0$ also für $bn \le c < 1{,}5\,bn$. Bei $c = bn$ ist das Verhältnis $2bn \,/\, 1{,}5\,bn = 4/3$ - die Schranke für affine Kosten.

**Schranken** (affine Kosten, Summe der Fahrzeiten): $4/3$ nicht-atomar (Roughgarden/Tardos 2002), $5/2$ atomar ungewichtet, $(3+\sqrt5)/2 \approx 2{,}618$ atomar gewichtet
(Christodoulou/Koutsoupias 2005, Awerbuch/Azar/Epstein 2005).

Implementiert in `poa_network.py` (Netz, Zähltupel, Gleichgewichte, Best-Response), `poa_gates.py` (Torwahl-Vehikel und Aufzählung), `poa_evaluation.py` (Experimente).
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zur Reihe: [Spieltheorie: von Nash bis Myerson-Satterthwaite](https://sebastianhanisch.net/konzepte-spieltheorie.html)."
)
