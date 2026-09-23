"""Torwahl-Vehikel: wortgleich zu nash-demo (Zahlen von dort), Aufzählung gegen eine skalare Definition, Preis der Anarchie >= 1."""

import itertools

import numpy as np
import pytest

import poa_gates as Gt


def truck_costs(inst, assign):
    loads = np.bincount(assign, weights=inst.w, minlength=inst.m)
    return (inst.a + inst.b * loads)[assign]


def is_ne(inst, assign):
    loads = np.bincount(assign, weights=inst.w, minlength=inst.m)
    for i in range(inst.n):
        cur = inst.a[assign[i]] + inst.b[assign[i]] * loads[assign[i]]
        L = loads.copy()
        L[assign[i]] -= inst.w[i]
        if (inst.a + inst.b * (L + inst.w[i])).min() < cur - 1e-9:
            return False
    return True


def test_matches_nash_demo_on_the_default_instance():
    """Zahlen aus nash-demo (Seed 35, 12 Lkw, 3 Tore, gemischt): Optimum 156,2; Gleichgewichte 164,9 bis 166,6 min."""
    r = Gt.analyse(Gt.generate(12, 3, "mixed", 35))
    assert r["n_ne"] == 2915 and abs(r["opt_cost"] - 156.2) < 0.05
    assert abs(r["ne_cost_min"] - 164.9) < 0.05 and abs(r["ne_cost_max"] - 166.6) < 0.05


def test_uniform_mode_has_the_same_gates_as_mixed():
    mixed, uniform = Gt.generate(12, 3, "mixed", 9), Gt.generate(12, 3, "uniform", 9)
    assert np.array_equal(mixed.a, uniform.a) and np.array_equal(mixed.b, uniform.b) and np.all(uniform.w == 1.0)


def test_unknown_size_mode_raises_and_too_big_raises():
    with pytest.raises(ValueError):
        Gt.generate(4, 2, "bogus", 0)
    with pytest.raises(ValueError):
        Gt.analyse(Gt.generate(40, 6, "mixed", 0))


@pytest.mark.parametrize("seed", range(6))
def test_enumeration_agrees_with_the_scalar_definition(seed):
    inst = Gt.generate(6, 3, "mixed", seed)
    res = Gt.analyse(inst)
    costs = [truck_costs(inst, np.array(a)).sum() for a in itertools.product(range(3), repeat=6)]
    ne = [c for a, c in zip(itertools.product(range(3), repeat=6), costs) if is_ne(inst, np.array(a))]
    assert res["n_ne"] == len(ne)
    assert res["opt_cost"] == pytest.approx(min(costs)) and res["ne_cost_max"] == pytest.approx(max(ne)) and res["ne_cost_min"] == pytest.approx(min(ne))


def test_price_of_anarchy_is_at_least_one():
    for seed in range(20):
        assert Gt.price_of_anarchy(Gt.generate(6, 3, "mixed", seed)) >= 1.0 - 1e-12
