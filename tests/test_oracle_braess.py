"""Orakel (anderer Rechenweg): Gleichgewichte und Optimum des Braess-Netzes per Vollaufzählung aller Einzel-Lkw-Zuordnungen mit reinen Schleifen (ganzzahlige Kantenwerte, also
viele Gleichstände), Preis der Anarchie im Torwahl-Spiel per Aufzählung, Standardnetz gegen die geschlossene Formel (alle auf der Abkürzung: 2bn je Lkw; geteilt: bn/2 + c)."""

import itertools

import numpy as np
import pytest

import poa_constants as C
import poa_gates as Gt
import poa_network as N

EPS = 1e-9


def _truck_cost(net, assign, i):
    load = [0] * 5
    for p in assign:
        for e in N.PATHS[p]:
            load[e] += 1
    ec = [net.a[e] + net.b[e] * load[e] for e in range(5)]
    return sum(ec[e] for e in N.PATHS[assign[i]])


def _brute(net, shortcut):
    P = 3 if shortcut else 2
    eqs, best = set(), np.inf
    for assign in itertools.product(range(P), repeat=net.n):
        best = min(best, sum(_truck_cost(net, assign, i) for i in range(net.n)))
        stable = all(_truck_cost(net, assign, i) <= min(_truck_cost(net, assign[:i] + (q,) + assign[i + 1:], i) for q in range(P)) + EPS for i in range(net.n))
        if stable:
            eqs.add(tuple(assign.count(p) for p in range(3)))
    return eqs, best


def test_equilibria_and_optimum_match_the_per_truck_enumeration_on_random_integer_nets():
    rng = np.random.default_rng(5)
    for _ in range(30):
        n = int(rng.integers(1, 6))
        net = N.Net(tuple(float(x) for x in rng.integers(0, 8, 5)), tuple(float(x) for x in rng.integers(0, 3, 5)), n)
        for shortcut in (True, False):
            eqs, best = _brute(net, shortcut)
            assert set(N.equilibria(net, shortcut)) == eqs
            assert N.optimum(net, shortcut)[1] == pytest.approx(best)


@pytest.mark.parametrize("n", [4, 12, 40])
def test_standard_net_matches_the_closed_form(n):
    net = N.classic(n, 1.0, 0.0)
    b = C.CLASSIC_B
    worst = max(N.social(net, s) for s in N.equilibria(net, True)) / n
    free = max(N.social(net, s) for s in N.equilibria(net, False)) / n
    assert worst == pytest.approx(2 * b * n) and free == pytest.approx(b * n / 2 + b * n)
    assert worst / (N.optimum(net, True)[1] / n) == pytest.approx(4 / 3)


def test_price_of_anarchy_of_the_gate_vehicle_matches_enumeration():
    rng = np.random.default_rng(9)
    for k in range(25):
        n, m = int(rng.integers(1, 6)), int(rng.integers(1, 4))
        a = rng.integers(0, 6, m).astype(float)
        b = rng.integers(1, 4, m).astype(float)
        w = rng.choice([1.0, 2.0, 3.0], n)
        socs, eq = [], []
        for asg in itertools.product(range(m), repeat=n):
            load = [sum(w[j] for j in range(n) if asg[j] == g) for g in range(m)]
            cost = [a[asg[i]] + b[asg[i]] * load[asg[i]] for i in range(n)]
            socs.append(sum(cost))
            if all(a[g] + b[g] * (load[g] + w[i]) >= cost[i] - EPS for i in range(n) for g in range(m) if g != asg[i]):
                eq.append(sum(cost))
        assert Gt.price_of_anarchy(Gt.Instance(a, b, w, 0)) == pytest.approx(max(eq) / min(socs))
