"""Auswertung: Analyse eines Laufs und die drei Experimente - schnelle Parameter über Funktionsargumente."""

import numpy as np
import pytest

import poa_constants as C
import poa_evaluation as E
import poa_network as N


def test_analyse_default_is_consistent():
    a = E.analyse(E.Settings())
    assert N.counts_of(a.run.final) in set(a.eq_open)
    assert len(a.social_history) == len(a.run.states) == len(a.run.moves) + 1
    assert a.opt_open[1] <= a.best_cost(True) + 1e-9 and a.opt_open[1] <= a.opt_closed[1] + 1e-9
    assert a.best_cost(True) <= a.worst_cost(True)


def test_analyse_closed_shortcut_uses_two_paths_only():
    a = E.analyse(E.Settings(shortcut="closed"))
    assert not a.shortcut_open and all(N.counts_of(s)[2] == 0 for s in a.run.states)


def test_random_order_and_index_order_both_end_in_equilibria():
    for order in C.ORDERS:
        a = E.analyse(E.Settings(order=order, seed=3))
        assert N.counts_of(a.run.final) in set(a.eq_open)


def test_window_experiment_shape_and_invariants():
    rows = E.window_experiment(n=8, c_rels=(0.5, 1.0, 2.0))
    assert [r["c_rel"] for r in rows] == [0.5, 1.0, 2.0]
    for r in rows:
        assert r["with_best"] <= r["with_worst"] + 1e-9 and r["poa_with"] >= 1 - 1e-9 and r["opt"] <= r["with_best"] + 1e-9


def test_random_nets_are_reproducible_and_valid():
    a, b = E.random_net(10, 5, "shaped"), E.random_net(10, 5, "shaped")
    assert a == b
    assert a.b[1] == 0 and a.b[2] == 0 and a.b[4] == 0
    with pytest.raises(ValueError):
        E.random_net(10, 5, "bogus")


def test_network_experiment_shares_sum_to_one():
    for mode in C.NET_MODES:
        r = E.network_experiment(mode, n=8, seeds=range(15))
        assert abs(r["worse"] + r["better"] + r["same"] - 1.0) < 1e-9 and 0 <= r["worse_5"] <= r["worse"]


def test_poa_random_and_search_shapes():
    r = E.poa_random("mixed", seeds=range(10))
    assert len(r["values"]) == 10 and r["max"] >= r["mean"] >= 1 - 1e-9
    s = E.poa_search(True, starts=10, steps=15)
    assert len(s["history"]) == 25 and all(y >= x - 1e-12 for x, y in zip(s["history"], s["history"][1:]))
    assert s["best"] == s["history"][-1] and s["best"] >= s["random_best"]
    u = E.poa_search(False, starts=10, steps=15)
    assert np.all(u["instance"].w == 1.0)


def test_search_is_deterministic():
    a, b = E.poa_search(True, starts=10, steps=20), E.poa_search(True, starts=10, steps=20)
    assert a["history"] == b["history"]
