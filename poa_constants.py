"""Konstanten der PoA-&-Braess-Demo: Braess-Netz (Einheitslkw), Vehikel "Torwahl" aus nash-demo, Regler, Experimente (Presets nach den Messungen)."""

EPS = 1e-9                         # ein Wechsel zählt nur bei echter Verbesserung
SEED_MAX = 999999

# --- Braess-Netz -----------------------------------------------------------------------------------------------------------------------------

CLASSIC_B = 0.5                    # Zuschlag je Lkw auf den lastabhängigen Kanten s→A und B→t (Minuten)
N_MIN, N_MAX, DEFAULT_N, N_STEP = 4, 40, 12, 2
CREL_MIN, CREL_MAX, DEFAULT_CREL, CREL_STEP = 0.25, 2.0, 1.0, 0.05      # c = c_rel * b * n: feste Fahrzeit der Umwege A→t und s→B
EREL_MIN, EREL_MAX, DEFAULT_EREL, EREL_STEP = 0.0, 0.5, 0.0, 0.05       # e = e_rel * b * n: Fahrzeit der Abkürzung A→B
DEFAULT_SEED = 7                   # Seed der Startzuordnung
ORDERS = ("index", "random")
ORDER_LABELS = {"index": "Feste Reihenfolge (Nummer)", "random": "Zufällige Reihenfolge"}
SHORTCUT_MODES = ("open", "closed")
SHORTCUT_LABELS = {"open": "Abkürzung offen", "closed": "Abkürzung gesperrt"}

# --- Vehikel "Torwahl" (wortgleich zu nash-demo) ----------------------------------------------------------------------------------------------

A_MIN, A_MAX = 2.0, 10.0
B_MIN, B_MAX = 0.5, 3.0
SIZES = (1, 2, 3)
SIZE_PROBS = (0.5, 0.3, 0.2)
ENUM_MAX_ASSIGNMENTS = 2_000_000

# --- Experimente (feste Seeds) ----------------------------------------------------------------------------------------------------------------

WINDOW_N = 20
WINDOW_CRELS = tuple(round(0.25 + 0.05 * k, 2) for k in range(36))       # 0,25 bis 2,0
NET_N = 20
NET_SEEDS = tuple(range(400000, 400300))
NET_MODES = ("free", "shaped")
NET_MODE_LABELS = {"free": "Beliebige Kantenwerte", "shaped": "Braess-Bauart (Zufahrten lastabhängig, Umwege konstant)"}
POA_N, POA_M = 6, 3
POA_SEEDS = tuple(range(500000, 500200))
SEARCH_RANDOM_STARTS = 200
SEARCH_STEPS = 3000
SEARCH_SEED = 11
SEARCH_A_MAX, SEARCH_B_MIN, SEARCH_B_MAX = 50.0, 0.01, 20.0
BOUND_NONATOMIC = 4 / 3            # Roughgarden/Tardos 2002: nicht-atomar, affine Kosten
BOUND_UNWEIGHTED = 5 / 2           # Christodoulou/Koutsoupias 2005: atomar, ungewichtet, affine Kosten
BOUND_WEIGHTED = (3 + 5 ** 0.5) / 2  # Awerbuch/Azar/Epstein 2005 und Christodoulou/Koutsoupias 2005: atomar, gewichtet, affine Kosten

# --- Presets (Werte nach den Messungen; PRESET_HELP aus dem Netz mit Startzuordnungs-Seed 7) ----------------------------------------------------


def _preset(n=DEFAULT_N, c_rel=DEFAULT_CREL, e_rel=DEFAULT_EREL, shortcut="open", order="index", seed=DEFAULT_SEED):
    return {"n": n, "c_rel": c_rel, "e_rel": e_rel, "shortcut": shortcut, "order": order, "seed": seed}


PRESETS = {
    "Standardfall (Braess-Netz)": _preset(),
    "Abkürzung gesperrt": _preset(shortcut="closed"),
    "Abkürzung mit Aufwand (e = 0,3)": _preset(e_rel=0.3),
    "Abkürzung hilft (c = 1,8)": _preset(c_rel=1.8),
    "Kleine Instanz (6 Lkw)": _preset(n=6),
    "Große Instanz (40 Lkw)": _preset(n=40),
}
PRESET_HELP = {
    "Standardfall (Braess-Netz)": "12 Lkw, Umweg-Fahrzeit c = b·n: Best-Response endet nach 4 Wechseln bei 11,1 min je Lkw. Ohne Abkürzung wären es 9,0 min. Das schlechteste Gleichgewicht mit Abkürzung: 12,0 min.",
    "Abkürzung gesperrt": "Dasselbe Netz ohne die Abkürzung: 2 Wechsel, die Lkw teilen sich auf beide Wege (6/6), jeder braucht 9,0 min - besser als mit der zusätzlichen Straße.",
    "Abkürzung mit Aufwand (e = 0,3)": "Die Abkürzung kostet selbst Fahrzeit: das Gleichgewicht ist jetzt eindeutig (4/4/4 Lkw), mit 9,9 min je Lkw trotzdem schlechter als ohne Abkürzung (9,0).",
    "Abkürzung hilft (c = 1,8)": "Sind die Umwege lang genug, lohnt die Abkürzung: alle 12 Lkw nehmen sie und brauchen 12,0 min - ohne sie wären es 13,8 min.",
    "Kleine Instanz (6 Lkw)": "6 Lkw: vier Gleichgewichte mit Abkürzung (5,2 bis 6,0 min je Lkw), ohne Abkürzung eines mit 4,5 min.",
    "Große Instanz (40 Lkw)": "40 Lkw: 21 Wechsel bis zu 39,0 min je Lkw, ohne Abkürzung 30,0 min - der Abstand wächst mit der Lkw-Zahl, das Verhältnis bleibt bei 4/3.",
}
