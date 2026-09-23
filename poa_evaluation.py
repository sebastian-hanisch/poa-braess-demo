"""Auswertung: ein Lauf im Braess-Netz mit Aufzählung der Gleichgewichte, Braess-Fenster, zufällige Netze, Preis der Anarchie im Torwahl-Spiel."""

from dataclasses import dataclass
from functools import lru_cache

import numpy as np

import poa_constants as C
import poa_gates as Gt
import poa_network as N


@dataclass(frozen=True)
class Settings:
    n: int = C.DEFAULT_N
    c_rel: float = C.DEFAULT_CREL
    e_rel: float = C.DEFAULT_EREL
    shortcut: str = "open"
    order: str = "index"
    seed: int = C.DEFAULT_SEED


@dataclass
class Analysis:
    settings: Settings
    net: object
    run: object
    eq_open: list          # alle Gleichgewichte mit Abkürzung
    eq_closed: list        # alle Gleichgewichte ohne Abkürzung
    opt_open: tuple        # (Zustand, Kosten) mit Abkürzung
    opt_closed: tuple

    @property
    def shortcut_open(self):
        return self.settings.shortcut == "open"

    @property
    def social_history(self):
        return [N.social(self.net, N.counts_of(s)) for s in self.run.states]

    def worst_cost(self, shortcut):
        eq = self.eq_open if shortcut else self.eq_closed
        return max(N.social(self.net, s) for s in eq)

    def best_cost(self, shortcut):
        eq = self.eq_open if shortcut else self.eq_closed
        return min(N.social(self.net, s) for s in eq)


@lru_cache(maxsize=64)
def analyse(settings):
    net = N.classic(settings.n, settings.c_rel, settings.e_rel)
    shortcut = settings.shortcut == "open"
    start = N.random_assignment(net.n, shortcut, settings.seed)
    run = N.run_sequential(net, start, shortcut, settings.order, settings.seed)
    return Analysis(settings, net, run, N.equilibria(net, True), N.equilibria(net, False), N.optimum(net, True), N.optimum(net, False))


# --- Experiment 1: Braess-Fenster ------------------------------------------------------------------------------------------------------------


def window_experiment(n=None, c_rels=None, e_rel=0.0):
    n = C.WINDOW_N if n is None else n
    c_rels = C.WINDOW_CRELS if c_rels is None else c_rels
    rows = []
    for c in c_rels:
        net = N.classic(n, c, e_rel)
        eq_o, eq_c = N.equilibria(net, True), N.equilibria(net, False)
        w_o = max(N.social(net, s) for s in eq_o) / n
        w_c = max(N.social(net, s) for s in eq_c) / n
        opt_o = N.optimum(net, True)[1] / n
        rows.append({"c_rel": c, "with_worst": w_o, "with_best": min(N.social(net, s) for s in eq_o) / n, "without": w_c, "opt": opt_o, "poa_with": w_o / opt_o})
    return rows


# --- Experiment 2: zufällige Netze -----------------------------------------------------------------------------------------------------------


def random_net(n, seed, mode):
    rng = np.random.default_rng(seed)
    if mode == "free":
        a, b = rng.uniform(0, 20, 5), rng.uniform(0, 1, 5)
    elif mode == "shaped":
        a = np.array([rng.uniform(0, 3), rng.uniform(5, 25), rng.uniform(5, 25), rng.uniform(0, 3), rng.uniform(0, 6)])
        b = np.array([rng.uniform(0.2, 1), 0, 0, rng.uniform(0.2, 1), 0])
    else:
        raise ValueError(mode)
    return N.Net(tuple(float(x) for x in a), tuple(float(x) for x in b), n)


def network_experiment(mode, n=None, seeds=None):
    """Für jedes Zufallsnetz: erreichtes Gleichgewicht (Best-Response von einer Zufallszuordnung) mit gegen ohne Abkürzung."""
    n = C.NET_N if n is None else n
    seeds = C.NET_SEEDS if seeds is None else seeds
    change = []
    for seed in seeds:
        net = random_net(n, seed, mode)
        r_o = N.run_sequential(net, N.random_assignment(n, True, seed), True, "index", seed)
        r_c = N.run_sequential(net, N.random_assignment(n, False, seed), False, "index", seed)
        c_o, c_c = N.social(net, N.counts_of(r_o.final)), N.social(net, N.counts_of(r_c.final))
        change.append((c_o - c_c) / c_c)
    change = np.array(change)
    return {"mode": mode, "n_nets": len(change), "worse": float(np.mean(change > 1e-9)), "better": float(np.mean(change < -1e-9)),
            "same": float(np.mean(np.abs(change) <= 1e-9)), "worse_5": float(np.mean(change > 0.05)), "mean_change": float(change.mean()),
            "max_worse": float(change.max()), "max_better": float(change.min())}


# --- Experiment 3: Preis der Anarchie im Torwahl-Spiel ---------------------------------------------------------------------------------------


def poa_random(size_mode, n=None, m=None, seeds=None):
    n = C.POA_N if n is None else n
    m = C.POA_M if m is None else m
    seeds = C.POA_SEEDS if seeds is None else seeds
    vals = np.array([Gt.price_of_anarchy(Gt.generate(n, m, size_mode, s)) for s in seeds])
    return {"values": vals, "mean": float(vals.mean()), "median": float(np.median(vals)), "max": float(vals.max())}


def _random_instance(rng, n, m, weighted):
    a = rng.uniform(0.0, 10.0, m)
    b = rng.uniform(0.1, 3.0, m)
    w = rng.choice(C.SIZES, size=n).astype(float) if weighted else np.ones(n)
    return Gt.Instance(a, b, w, 0)


def poa_search(weighted, n=None, m=None, starts=None, steps=None, seed=None):
    """Gezielte Suche nach einer schlechten Instanz: beste von `starts` Zufallsinstanzen, dann Hill Climbing (Tor-Parameter multiplikativ verrauscht,
    Größen umgewürfelt) über beliebige Tor-Parameter, nicht auf die Vehikel-Bereiche beschränkt. Verlauf = bester bisheriger Preis der Anarchie je Bewertung."""
    n = C.POA_N if n is None else n
    m = C.POA_M if m is None else m
    starts = C.SEARCH_RANDOM_STARTS if starts is None else starts
    steps = C.SEARCH_STEPS if steps is None else steps
    seed = C.SEARCH_SEED if seed is None else seed
    rng = np.random.default_rng(seed)
    history, best, best_v = [], None, 0.0
    for _ in range(starts):
        inst = _random_instance(rng, n, m, weighted)
        v = Gt.price_of_anarchy(inst)
        if v > best_v:
            best, best_v = inst, v
        history.append(best_v)
    random_best = best_v
    for _ in range(steps):
        a = np.clip(best.a * np.exp(rng.normal(0, 0.2, m)), 0.0, C.SEARCH_A_MAX)
        b = np.clip(best.b * np.exp(rng.normal(0, 0.2, m)), C.SEARCH_B_MIN, C.SEARCH_B_MAX)
        w = best.w.copy()
        if weighted and rng.random() < 0.3:
            w[rng.integers(n)] = rng.choice(C.SIZES)
        cand = Gt.Instance(a, b, w, 0)
        v = Gt.price_of_anarchy(cand)
        if v >= best_v:
            best, best_v = cand, v
        history.append(best_v)
    return {"history": history, "random_best": random_best, "best": best_v, "instance": best}
