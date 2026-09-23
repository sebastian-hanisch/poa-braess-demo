"""Plotly-Abbildungen der PoA-&-Braess-Demo. Achsen sind gesperrt (fixedrange)."""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import poa_constants as C
import poa_network as N

LINE_COLOR = "#4c78a8"
REF_COLOR = "#7f7f7f"
GOOD = "#54a24b"
BAD = "#e45756"
WARN = "#f58518"
NODE_XY = {"s": (0.0, 0.5), "A": (1.0, 1.0), "B": (1.0, 0.0), "t": (2.0, 0.5)}
EDGE_NODES = (("s", "A"), ("A", "t"), ("s", "B"), ("B", "t"), ("A", "B"))
PATH_COLORS = (LINE_COLOR, WARN, BAD)


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=-0.2), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_network(net, counts, shortcut_open, highlight=None):
    """Das Netz mit Last und Fahrzeit je Kante; Linienstärke = Last. Gesperrte Abkürzung gestrichelt und grau."""
    loads = N.edge_loads(net, counts)
    costs = N.edge_costs(net, counts)
    fig = go.Figure()
    top = max(1.0, float(max(loads)))
    for e, (u, v) in enumerate(EDGE_NODES):
        (x0, y0), (x1, y1) = NODE_XY[u], NODE_XY[v]
        closed = e == 4 and not shortcut_open
        width = 2 + 10 * loads[e] / top if not closed else 2
        fig.add_trace(go.Scatter(x=[x0, x1], y=[y0, y1], mode="lines", line=dict(color="#b0b0b0" if closed else LINE_COLOR, width=width, dash="dash" if closed else "solid"),
                                 hoverinfo="skip", showlegend=False))
        label = "gesperrt" if closed else f"{loads[e]:g} Lkw · {costs[e]:.1f} min"
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        dx, dy = {0: (-0.2, 0.13), 1: (0.2, 0.13), 2: (-0.2, -0.13), 3: (0.2, -0.13), 4: (0.24, 0.0)}[e]
        fig.add_annotation(x=mx + dx, y=my + dy, text=f"<b>{N.EDGES[e]}</b><br>{label}", showarrow=False, font=dict(size=11, color="#8a8a8a" if closed else None))
    for name, (x, y) in NODE_XY.items():
        fig.add_trace(go.Scatter(x=[x], y=[y], mode="markers+text", text=[name], textposition="middle center", marker=dict(size=34, color="white", line=dict(color="#14233B", width=2)),
                                 hoverinfo="skip", showlegend=False))
    fig.update_xaxes(visible=False, range=[-0.55, 2.55])
    fig.update_yaxes(visible=False, range=[-0.3, 1.3])
    return _base(fig, 330)


def build_social_curve(costs_per_truck, n, upto=None, reference=None, reference_label="Optimum"):
    xs = list(range(len(costs_per_truck)))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=costs_per_truck, mode="lines+markers", line=dict(color=BAD, width=2.5), name="Mittlere Fahrzeit"))
    if reference is not None:
        fig.add_hline(y=reference, line=dict(color=REF_COLOR, dash="dot"), annotation_text=reference_label, annotation_position="bottom right")
    if upto is not None:
        fig.add_vline(x=upto, line=dict(color=REF_COLOR, dash="dot"))
    fig.update_xaxes(title_text="Zug (0 = Start)", dtick=1 if len(xs) < 16 else None)
    fig.update_yaxes(title_text="Mittlere Fahrzeit je Lkw (min)")
    fig.update_layout(showlegend=False)
    return _base(fig, 300)


def build_window(rows):
    """Links: Fahrzeit je Lkw im (schlechtesten) Gleichgewicht mit und ohne Abkürzung und im Optimum; rechts: Preis der Anarchie mit Abkürzung."""
    xs = [r["c_rel"] for r in rows]
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Mittlere Fahrzeit je Lkw", "Preis der Anarchie mit Abkürzung"), horizontal_spacing=0.12)
    fig.add_trace(go.Scatter(x=xs, y=[r["with_worst"] for r in rows], mode="lines", name="Gleichgewicht mit Abkürzung", line=dict(color=BAD, width=2.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=xs, y=[r["without"] for r in rows], mode="lines", name="Gleichgewicht ohne Abkürzung", line=dict(color=GOOD, width=2.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=xs, y=[r["opt"] for r in rows], mode="lines", name="Optimum mit Abkürzung", line=dict(color=REF_COLOR, width=2, dash="dot")), row=1, col=1)
    fig.add_trace(go.Scatter(x=xs, y=[r["poa_with"] for r in rows], mode="lines", line=dict(color=BAD, width=2.5), showlegend=False), row=1, col=2)
    fig.add_hline(y=C.BOUND_NONATOMIC, line=dict(color=REF_COLOR, dash="dot"), annotation_text="4/3", annotation_position="top left", row=1, col=2)
    fig.update_xaxes(title_text="Umweg-Fahrzeit c / (b · n)")
    fig.update_yaxes(title_text="min", row=1, col=1)
    fig.update_yaxes(range=[0.98, 1.4], row=1, col=2)
    fig.update_layout(height=340, margin=dict(l=10, r=10, t=40, b=10), legend=dict(orientation="h", y=-0.3), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_network_experiment(results):
    """Gestapelte Anteile: Abkürzung verschlechtert / ändert nichts / verbessert das erreichte Gleichgewicht, je Netz-Art."""
    labels = [C.NET_MODE_LABELS[r["mode"]] for r in results]
    fig = go.Figure()
    fig.add_trace(go.Bar(y=labels, x=[r["worse"] for r in results], name="verschlechtert", marker_color=BAD, orientation="h"))
    fig.add_trace(go.Bar(y=labels, x=[r["same"] for r in results], name="ändert nichts", marker_color="#c9c9c9", orientation="h"))
    fig.add_trace(go.Bar(y=labels, x=[r["better"] for r in results], name="verbessert", marker_color=GOOD, orientation="h"))
    fig.update_layout(barmode="stack")
    fig.update_xaxes(tickformat=".0%", range=[0, 1], title_text="Anteil der Zufallsnetze")
    return _base(fig, 240)


def _de(x, digits=2):
    return f"{x:.{digits}f}".replace(".", ",")


def build_poa_distribution(random_mixed, random_uniform, best_weighted, best_unit):
    """Verteilung des Preises der Anarchie über Zufallsinstanzen, dazu die Ergebnisse der gezielten Suche und die Schranken aus der Literatur (Legende statt Beschriftung)."""
    counts = [np.histogram(r["values"], bins=np.arange(1.0, 2.72, 0.02))[0].max() for r in (random_mixed, random_uniform)]
    ymax = float(max(counts)) * 1.05
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=random_mixed["values"], xbins=dict(start=1.0, end=2.7, size=0.02), name="Zufall, gemischte Größen", marker_color=LINE_COLOR, opacity=0.75))
    fig.add_trace(go.Histogram(x=random_uniform["values"], xbins=dict(start=1.0, end=2.7, size=0.02), name="Zufall, einheitliche Größen", marker_color=GOOD, opacity=0.75))
    marks = ((best_unit, f"Suche, einheitliche Größen: {_de(best_unit)}", GOOD, "dash"), (best_weighted, f"Suche, gemischte Größen: {_de(best_weighted)}", LINE_COLOR, "dash"),
             (C.BOUND_NONATOMIC, "Schranke nicht atomar: 4/3", REF_COLOR, "dot"), (C.BOUND_UNWEIGHTED, "Schranke ungewichtet: 5/2", BAD, "dot"),
             (C.BOUND_WEIGHTED, f"Schranke gewichtet: {_de(C.BOUND_WEIGHTED, 3)}", "#a83232", "dot"))
    for x, text, color, dash in marks:
        fig.add_trace(go.Scatter(x=[x, x], y=[0, ymax], mode="lines", name=text, line=dict(color=color, dash=dash, width=2.5)))
    fig.update_layout(barmode="overlay")
    fig.update_xaxes(title_text="Preis der Anarchie (schlechtestes Gleichgewicht / Optimum)", range=[0.98, 2.72])
    fig.update_yaxes(title_text="Instanzen")
    return _base(fig, 400).update_layout(legend=dict(orientation="h", y=-0.35))


def build_search_curve(history_weighted, history_unit):
    n = len(history_weighted)
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=history_weighted, mode="lines", name="Suche, gemischte Größen", line=dict(color=LINE_COLOR, width=2.5)))
    fig.add_trace(go.Scatter(y=history_unit, mode="lines", name="Suche, einheitliche Größen", line=dict(color=GOOD, width=2.5)))
    for y, text, color in ((C.BOUND_WEIGHTED, f"Schranke gewichtet: {_de(C.BOUND_WEIGHTED, 3)}", "#a83232"), (C.BOUND_UNWEIGHTED, "Schranke ungewichtet: 5/2", BAD), (C.BOUND_NONATOMIC, "Schranke nicht atomar: 4/3", REF_COLOR)):
        fig.add_trace(go.Scatter(x=[0, n], y=[y, y], mode="lines", name=text, line=dict(color=color, dash="dot", width=2)))
    fig.add_trace(go.Scatter(x=[C.SEARCH_RANDOM_STARTS] * 2, y=[1.0, 2.75], mode="lines", name="ab hier gezielte Suche", line=dict(color="#b0b0b0", dash="dash", width=1.5)))
    fig.update_xaxes(title_text="Bewertete Instanzen", range=[0, n])
    fig.update_yaxes(title_text="Bester bisheriger Preis der Anarchie", range=[1.0, 2.75])
    return _base(fig, 400).update_layout(legend=dict(orientation="h", y=-0.35))
