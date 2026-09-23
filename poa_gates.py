"""Vehikel "Torwahl" aus nash-demo, wortgleich übernommen (Erzeugung und Vollaufzählung): Tor g hat die Wartezeit a_g + b_g * Last, Lkw i hat Größe w_i.
Hier nur, um den Preis der Anarchie zu messen: schlechtestes reines Gleichgewicht gegen das Optimum (kleinste Summe der Wartezeiten)."""

from dataclasses import dataclass

import numpy as np

import poa_constants as C


@dataclass(frozen=True)
class Instance:
    a: np.ndarray      # (m,) Grundwartezeit
    b: np.ndarray      # (m,) Zuschlag je Ladungseinheit
    w: np.ndarray      # (n,) Lkw-Größe
    seed: int

    @property
    def n(self):
        return len(self.w)

    @property
    def m(self):
        return len(self.a)


def generate(n, m, size_mode="mixed", seed=0):
    rng = np.random.default_rng(seed)
    a = rng.uniform(C.A_MIN, C.A_MAX, size=m)
    b = rng.uniform(C.B_MIN, C.B_MAX, size=m)
    if size_mode == "mixed":
        w = rng.choice(C.SIZES, size=n, p=C.SIZE_PROBS).astype(float)
    elif size_mode == "uniform":
        rng.choice(C.SIZES, size=n, p=C.SIZE_PROBS)      # Ziehung verbrauchen: gleiche Tore wie im gemischten Modus
        w = np.ones(n)
    else:
        raise ValueError(size_mode)
    return Instance(a, b, w, int(seed))


def analyse(inst):
    """Alle reinen Gleichgewichte (kein Lkw verbessert sich strikt durch einen Alleingang, direkt aus der Definition) und das Optimum."""
    N = inst.m ** inst.n
    if N > C.ENUM_MAX_ASSIGNMENTS:
        raise ValueError("zu viele Zuordnungen für die Vollaufzählung")
    idx = np.arange(N, dtype=np.int64)
    A = np.empty((N, inst.n), dtype=np.int8)
    for i in range(inst.n):
        A[:, i] = idx % inst.m
        idx //= inst.m
    L = np.zeros((N, inst.m))
    for i in range(inst.n):
        L[np.arange(N), A[:, i]] += inst.w[i]
    cost_gate = inst.a[None, :] + inst.b[None, :] * L
    truck_cost = np.take_along_axis(cost_gate, A.astype(np.int64), axis=1)
    social = truck_cost.sum(axis=1)
    is_ne = np.ones(N, dtype=bool)
    for i in range(inst.n):
        Li = L.copy()
        Li[np.arange(N), A[:, i]] -= inst.w[i]
        dev = inst.a[None, :] + inst.b[None, :] * (Li + inst.w[i])
        is_ne &= truck_cost[:, i] <= dev.min(axis=1) + C.EPS
    ne_idx = np.flatnonzero(is_ne)
    return {
        "n_ne": int(len(ne_idx)),
        "opt_cost": float(social.min()),
        "ne_cost_min": float(social[ne_idx].min()),
        "ne_cost_max": float(social[ne_idx].max()),
    }


def price_of_anarchy(inst):
    """Schlechtestes reines Gleichgewicht geteilt durch das Optimum (>= 1)."""
    r = analyse(inst)
    return r["ne_cost_max"] / r["opt_cost"]
