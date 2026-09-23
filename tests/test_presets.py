"""Presets: Vollständigkeit, gültige Werte, Grenzen/Schrittweiten - reine Datenprüfungen ohne Streamlit-Session
(Permalink-Klammern und Preset-Knöpfe werden über AppTest in test_app.py geprüft)."""

import poa_constants as C
import poa_evaluation as E
import poa_presets as P


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, p in C.PRESETS.items():
        assert set(p) == set(P.PRESET_KEYS) and C.PRESET_HELP[name] and "TODO" not in C.PRESET_HELP[name]


def test_preset_values_are_valid_and_match_the_setting_specs():
    for p in C.PRESETS.values():
        assert C.N_MIN <= p["n"] <= C.N_MAX and C.CREL_MIN <= p["c_rel"] <= C.CREL_MAX and C.EREL_MIN <= p["e_rel"] <= C.EREL_MAX
        assert p["shortcut"] in C.SHORTCUT_MODES and p["order"] in C.ORDERS
        for key, state_key in P.PRESET_KEYS.items():
            P.SETTING_SPECS[state_key].caster(p[key])


def test_default_preset_equals_the_default_settings():
    assert E.Settings(**C.PRESETS["Standardfall (Braess-Netz)"]) == E.Settings()


def test_bounds_and_steps_constants():
    assert P.bounds("n_slider") == (C.N_MIN, C.N_MAX)
    assert P.bounds("crel_slider") == (C.CREL_MIN, C.CREL_MAX)
    assert P.bounds("seed_input") == (0, C.SEED_MAX)
    assert set(P.STEPS) == {"n_slider", "crel_slider", "erel_slider"}


def test_url_params_are_unique():
    assert len({spec.url_param for spec in P.SETTING_SPECS.values()}) == len(P.SETTING_SPECS)


def test_window_grid_lies_on_the_slider_grid():
    for c in C.WINDOW_CRELS:
        assert abs((c - C.CREL_MIN) / C.CREL_STEP - round((c - C.CREL_MIN) / C.CREL_STEP)) < 1e-9
