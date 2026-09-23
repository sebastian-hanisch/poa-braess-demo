"""AppTest-Rauchtests: Voreinstellung, jedes Preset, Zug-Slider, Abspielen ohne doppelte Schlüssel, Würfel-Knopf, Permalink-Grenzen, Extremwerte,
drei Experimente auf Abruf, Footer."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import poa_constants as C

APP = str(Path(__file__).resolve().parent.parent / "app.py")


def _run(**state):
    at = AppTest.from_file(APP, default_timeout=300)
    for k, v in state.items():
        at.session_state[k] = v
    at.run()
    return at


def _ok(at):
    assert not at.exception, [e.value for e in at.exception]


def test_default_run_has_no_exception_and_shows_the_braess_paradox():
    at = _run()
    _ok(at)
    assert at.metric and any("Braess-Paradox" in w.value for w in at.warning)


@pytest.mark.parametrize("name", list(C.PRESETS))
def test_every_preset_button_runs(name):
    at = _run()
    next(b for b in at.button if b.key == f"preset_{name}").click().run()
    _ok(at)
    p = C.PRESETS[name]
    assert at.session_state["n_slider"] == p["n"] and at.session_state["shortcut_select"] == p["shortcut"]
    assert at.metric


def test_step_slider_runs_at_various_positions():
    at = _run()
    step = next(s for s in at.slider if s.key == "poa_step")
    step.set_value(0).run()
    _ok(at)
    step = next(s for s in at.slider if s.key == "poa_step")
    step.set_value(step.max).run()
    _ok(at)
    assert at.get("plotly_chart")


def test_play_runs_without_duplicate_keys():
    at = _run()
    next(b for b in at.button if b.label == "▶️ Abspielen").click().run()
    _ok(at)


def test_verdict_switches_with_the_umweg_time():
    assert any("Braess-Paradox" in w.value for w in _run(crel_slider=1.0).warning)
    assert any("Die Abkürzung hilft" in s.value for s in _run(crel_slider=1.8).success)
    assert any("Kein Unterschied" in i.value for i in _run(crel_slider=0.25).info)


def test_dice_button_changes_the_seed():
    at = _run()
    old = at.session_state["seed_input"]
    next(b for b in at.button if b.label == "🎲 Neue Startzuordnung würfeln").click().run()
    _ok(at)
    assert at.session_state["seed_input"] != old


def test_permalink_values_are_clamped_and_snapped():
    at = AppTest.from_file(APP, default_timeout=300)
    at.query_params["n"] = "9999"
    at.query_params["c"] = "9999"
    at.query_params["e"] = "0.33"
    at.run()
    _ok(at)
    assert at.session_state["n_slider"] == C.N_MAX and at.session_state["crel_slider"] == C.CREL_MAX
    assert abs(at.session_state["erel_slider"] - 0.35) < 1e-9


@pytest.mark.parametrize("kw", [dict(n_slider=C.N_MIN), dict(n_slider=C.N_MAX), dict(crel_slider=C.CREL_MIN), dict(crel_slider=C.CREL_MAX),
                                dict(erel_slider=C.EREL_MAX), dict(shortcut_select="closed"), dict(order_select="random")])
def test_extreme_settings_run(kw):
    _ok(_run(**kw))


def test_window_experiment_runs_on_demand(monkeypatch):
    monkeypatch.setattr(C, "WINDOW_N", 8)
    monkeypatch.setattr(C, "WINDOW_CRELS", (0.5, 1.0, 1.6))
    at = _run()
    next(b for b in at.button if b.key == "window_start").click().run()
    _ok(at)
    assert at.session_state["window_on"] and at.get("plotly_chart")


def test_network_experiment_runs_on_demand(monkeypatch):
    monkeypatch.setattr(C, "NET_SEEDS", (1, 2, 3, 4))
    monkeypatch.setattr(C, "NET_N", 8)
    at = _run()
    next(b for b in at.button if b.key == "networks_start").click().run()
    _ok(at)
    assert at.session_state["networks_on"]


def test_poa_experiment_runs_on_demand(monkeypatch):
    monkeypatch.setattr(C, "POA_SEEDS", (1, 2, 3))
    monkeypatch.setattr(C, "SEARCH_RANDOM_STARTS", 5)
    monkeypatch.setattr(C, "SEARCH_STEPS", 5)
    at = _run()
    next(b for b in at.button if b.key == "poa_start").click().run()
    _ok(at)
    assert at.session_state["poa_on"]


def test_footer_and_grenzen_are_present():
    at = _run()
    assert any("Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net)" in c.value for c in at.caption)
    assert any("Wo die Annahmen enden" in s.value for s in at.subheader)
