"""Jede im README/PRESET_HELP/App genannte Zahl wird hier nachgerechnet - keine Behauptung ohne Test.

Netz-Läufe sind diskret (ganzzahlige Züge, Gleichstände mit Toleranz), also robust gegen Fließkomma-Rundung. Mehr-Instanzen-Zahlen (Zufallsnetze,
Torwahl-Instanzen, Suche) bekommen großzügige Bänder (feedback_ci_platform_robust_tests / feedback_ci_unpinned_numeric_asserts)."""

import pytest

import poa_constants as C
import poa_evaluation as E
import poa_gates as Gt
import poa_network as N


def _preset(name):
    return E.analyse(E.Settings(**C.PRESETS[name]))


def _per_truck(a, x):
    return x / a.net.n


# --- PRESET_HELP: Einzelläufe mit ganzzahligen Zügen -----------------------------------------------------------------------------------------


def test_standardfall_numbers():
    a = _preset("Standardfall (Braess-Netz)")
    assert len(a.run.moves) == 4 and N.counts_of(a.run.final) == (1, 1, 10)
    assert _per_truck(a, a.social_history[-1]) == pytest.approx(11.08, abs=0.005)
    assert _per_truck(a, a.worst_cost(True)) == pytest.approx(12.0) and _per_truck(a, a.worst_cost(False)) == pytest.approx(9.0)
    assert _per_truck(a, a.opt_open[1]) == pytest.approx(9.0) and a.worst_cost(True) / a.opt_open[1] == pytest.approx(4 / 3)
    assert len(a.eq_open) == 4 and a.eq_closed == [(6, 6, 0)]


def test_gesperrt_numbers():
    a = _preset("Abkürzung gesperrt")
    assert len(a.run.moves) == 2 and N.counts_of(a.run.final) == (6, 6, 0) and _per_truck(a, a.social_history[-1]) == pytest.approx(9.0)


def test_aufwand_numbers():
    a = _preset("Abkürzung mit Aufwand (e = 0,3)")
    assert a.eq_open == [(4, 4, 4)] and _per_truck(a, a.worst_cost(True)) == pytest.approx(9.93, abs=0.005) and _per_truck(a, a.worst_cost(False)) == pytest.approx(9.0)


def test_abkuerzung_hilft_numbers():
    a = _preset("Abkürzung hilft (c = 1,8)")
    assert a.eq_open == [(0, 0, 12)] and _per_truck(a, a.worst_cost(True)) == pytest.approx(12.0) and _per_truck(a, a.worst_cost(False)) == pytest.approx(13.8)


def test_kleine_instanz_numbers():
    a = _preset("Kleine Instanz (6 Lkw)")
    assert len(a.eq_open) == 4 and _per_truck(a, a.best_cost(True)) == pytest.approx(5.17, abs=0.005) and _per_truck(a, a.worst_cost(True)) == pytest.approx(6.0)
    assert _per_truck(a, a.worst_cost(False)) == pytest.approx(4.5)


def test_grosse_instanz_numbers():
    a = _preset("Große Instanz (40 Lkw)")
    assert len(a.run.moves) == 21 and _per_truck(a, a.social_history[-1]) == pytest.approx(39.02, abs=0.005)
    assert _per_truck(a, a.worst_cost(True)) == pytest.approx(40.0) and _per_truck(a, a.worst_cost(False)) == pytest.approx(30.0)
    assert a.worst_cost(True) / a.worst_cost(False) == pytest.approx(4 / 3)


# --- Braess-Fenster (Experiment 1): exakt aufgezählt ------------------------------------------------------------------------------------------


def test_braess_window_bounds_and_peak():
    rows = E.window_experiment()
    hurt = [r["c_rel"] for r in rows if r["with_worst"] > r["without"] + 1e-9]
    helps = [r["c_rel"] for r in rows if r["with_worst"] < r["without"] - 1e-9]
    assert min(hurt) == pytest.approx(0.55) and max(hurt) == pytest.approx(1.45) and min(helps) == pytest.approx(1.55)
    peak = max(rows, key=lambda r: r["poa_with"])
    assert peak["c_rel"] == pytest.approx(1.0) and peak["poa_with"] == pytest.approx(4 / 3)
    assert all(r["poa_with"] <= 4 / 3 + 1e-9 for r in rows)
    at_15 = next(r for r in rows if r["c_rel"] == pytest.approx(1.5))
    assert at_15["with_worst"] == pytest.approx(at_15["without"])


def test_braess_ratio_is_four_thirds_for_every_size():
    for n in (4, 12, 40):
        net = N.classic(n, 1.0, 0.0)
        assert max(N.social(net, s) for s in N.equilibria(net, True)) / max(N.social(net, s) for s in N.equilibria(net, False)) == pytest.approx(4 / 3)


def test_shortcut_with_own_cost_can_still_hurt_but_not_from_e_half():
    net = N.classic(20, 1.0, 0.3)
    assert max(N.social(net, s) for s in N.equilibria(net, True)) > max(N.social(net, s) for s in N.equilibria(net, False))
    net = N.classic(20, 1.0, 0.5)
    assert max(N.social(net, s) for s in N.equilibria(net, True)) == pytest.approx(max(N.social(net, s) for s in N.equilibria(net, False)))


# --- Zufallsnetze (Experiment 2): Bänder -----------------------------------------------------------------------------------------------------------


def test_random_networks_free_vs_shaped():
    free, shaped = E.network_experiment("free"), E.network_experiment("shaped")
    assert free["worse"] < 0.08 and free["same"] > 0.8 and free["worse_5"] == 0.0 and free["better"] > free["worse"]
    assert 0.35 < shaped["worse"] < 0.65 and 0.2 < shaped["worse_5"] < 0.45 and 0.2 < shaped["better"] < 0.45
    assert 0.15 < shaped["max_worse"] < 0.35 and shaped["worse"] > 5 * free["worse"]


# --- Preis der Anarchie im Torwahl-Spiel (Experiment 3): Bänder ------------------------------------------------------------------------------


def test_random_instances_stay_close_to_one():
    mixed, uniform = E.poa_random("mixed"), E.poa_random("uniform")
    assert 1.03 < mixed["mean"] < 1.09 and mixed["max"] < 1.3
    assert 1.0 <= uniform["mean"] < 1.05 and uniform["mean"] < mixed["mean"] and uniform["max"] < 1.3


def test_targeted_search_beats_random_but_stays_far_below_the_bounds():
    weighted, unit = E.poa_search(True), E.poa_search(False)
    assert weighted["best"] > weighted["random_best"] + 0.1 and unit["best"] > unit["random_best"] + 0.05
    assert 1.45 < weighted["best"] < 1.9 and 1.25 < unit["best"] < 1.4
    assert weighted["best"] > unit["best"] and weighted["best"] < C.BOUND_UNWEIGHTED - 0.5


def test_search_never_exceeds_the_theoretical_bounds():
    for weighted in (True, False):
        r = E.poa_search(weighted, steps=300)
        assert r["best"] <= (C.BOUND_WEIGHTED if weighted else C.BOUND_UNWEIGHTED) + 1e-9


def test_bound_constants():
    assert C.BOUND_NONATOMIC == pytest.approx(4 / 3) and C.BOUND_UNWEIGHTED == 2.5 and C.BOUND_WEIGHTED == pytest.approx(2.618, abs=0.001)


def test_default_torwahl_instance_matches_nash_demo():
    r = Gt.analyse(Gt.generate(12, 3, "mixed", 35))
    assert r["n_ne"] == 2915
