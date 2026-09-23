"""Braess-Netz: Handrechnung, Gleichgewichte gegen eine unabhängige Prüfung auf Einzel-Lkw-Ebene, Best-Response endet in einem aufgezählten Gleichgewicht."""

import itertools

import numpy as np
import pytest

import poa_network as N


def hand_net():
    """4 Lkw, b = 1 auf s→A und B→t, Umwege c = 4, Abkürzung kostenlos."""
    return N.Net((0.0, 4.0, 4.0, 0.0, 0.0), (1.0, 0.0, 0.0, 1.0, 0.0), 4)


def test_hand_calculation_of_costs_and_social_cost():
    net = hand_net()
    assert list(N.path_costs(net, (2, 2, 0))) == [6.0, 6.0, 4.0]     # Weg 3 ungenutzt: bei aktueller Last 2 + 0 + 2; ein Wechsler sähe 3 + 0 + 3 = 6, also keine Verbesserung
    assert N.social(net, (2, 2, 0)) == 24.0
    assert list(N.path_costs(net, (0, 0, 4))) == [8.0, 8.0, 8.0]
    assert N.social(net, (0, 0, 4)) == 32.0


def test_hand_calculation_of_equilibria_and_ratio():
    net = hand_net()
    assert N.equilibria(net, False) == [(2, 2, 0)]
    assert set(N.equilibria(net, True)) == {(0, 0, 4), (0, 1, 3), (1, 0, 3), (1, 1, 2)}
    worst = max(N.social(net, s) for s in N.equilibria(net, True))
    assert worst / N.optimum(net, True)[1] == pytest.approx(4 / 3)


def test_counting_states_agree_with_per_truck_definition():
    """Ein Zähltupel ist genau dann Gleichgewicht, wenn keine der 3^n Einzelzuordnungen, die es erzeugen, einem Lkw einen strikt besseren Weg lässt."""
    net = N.classic(5, 1.0, 0.0)
    for shortcut in (True, False):
        eq = set(N.equilibria(net, shortcut))
        for assign in itertools.product(range(N.n_paths(shortcut)), repeat=net.n):
            counts = N.counts_of(np.array(assign))
            stable = all(N.best_move(net, np.array(assign), i, shortcut) == assign[i] for i in range(net.n))
            assert stable == (counts in eq)


@pytest.mark.parametrize("shortcut", [True, False])
@pytest.mark.parametrize("seed", range(8))
def test_best_response_ends_in_an_enumerated_equilibrium(seed, shortcut):
    net = N.classic(12, 0.6 + 0.15 * seed, 0.05 * (seed % 3))
    run = N.run_sequential(net, N.random_assignment(net.n, shortcut, seed), shortcut, "random", seed)
    assert N.counts_of(run.final) in set(N.equilibria(net, shortcut))


def test_closed_shortcut_never_uses_the_third_path():
    net = N.classic(10, 1.0, 0.0)
    run = N.run_sequential(net, N.random_assignment(10, False, 3), False)
    assert all(max(s) <= 1 for s in run.states)
    assert all(q < 2 for _, _, q in run.moves)


def test_optimum_is_a_lower_bound_of_every_equilibrium_and_closing_never_improves_the_optimum():
    for c in (0.5, 1.0, 1.5, 2.0):
        net = N.classic(8, c, 0.0)
        assert N.optimum(net, True)[1] <= N.optimum(net, False)[1] + 1e-9
        for s in N.equilibria(net, True):
            assert N.social(net, s) >= N.optimum(net, True)[1] - 1e-9


def test_all_states_counts():
    assert len(N.all_states(6, True)) == 28 and len(N.all_states(6, False)) == 7
    assert all(sum(s) == 6 for s in N.all_states(6, True))
