# -*- coding: utf-8 -*-
"""Dibuja assets/slides/organigrama.jpg a partir de organigrama.json y puestos.json (necesita matplotlib)."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import textwrap

BASE = Path(__file__).parent
nodos = json.loads((BASE / "organigrama.json").read_text(encoding="utf-8"))["nodos"]
puestos = {p["nombre"]: p["area"] for p in json.loads((BASE / "puestos.json").read_text(encoding="utf-8"))}
COLOR = {"Administración": "#5B2D8E", "Almacén": "#2E7D32", "Distribución": "#1565C0", "Operador Logístico": "#E65100", "Ventas": "#C8102E"}
hijos = {}
for n in nodos:
    hijos.setdefault(n["padre"], []).append(n["id"])
por_id = {n["id"]: n for n in nodos}


def area_de(i):
    n = por_id[i]
    if i in puestos:
        return puestos[i]
    return n.get("area")


pos, hojas = {}, [0]


def colocar(i, prof):
    hs = hijos.get(i, [])
    if not hs:
        y = hojas[0]; hojas[0] += 1
    else:
        ys = [colocar(h, prof + 1) for h in hs]
        y = (ys[0] + ys[-1]) / 2
    pos[i] = (prof, y)
    return y


raiz = [n["id"] for n in nodos if n["padre"] is None][0]
colocar(raiz, 0)
prof_max = max(p[0] for p in pos.values())
W, H = 3.5, 0.74   # separación entre columnas y filas
fig, ax = plt.subplots(figsize=((prof_max + 1) * W * 0.95, hojas[0] * H * 0.95 + 1.2))
BW, BH = 2.95, 0.56
for i, (x, y) in pos.items():
    for h in hijos.get(i, []):
        hx, hy = pos[h]
        xm = x * W + BW + (hx * W - x * W - BW) / 2
        ax.plot([x * W + BW, xm, xm, hx * W], [-y * H, -y * H, -hy * H, -hy * H], color="#9aa5b1", lw=1.4, zorder=1)
for i, (x, y) in pos.items():
    n = por_id[i]; a = area_de(i)
    col = COLOR.get(a, "#455A64")
    if n["tipo"] == "cargo":
        fc, ec, tc, ls = col, col, "white", "-"
    elif n["tipo"] == "grupo":
        fc, ec, tc, ls = "#FFF3E0", col, "#333333", "-"
    else:  # jefatura que no figura en la base de datos
        fc, ec, tc, ls = "#F5F5F5", "#78909C", "#37474F", "--"
    ax.add_patch(FancyBboxPatch((x * W, -y * H - BH / 2), BW, BH, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec=ec, lw=1.6, ls=ls, zorder=2))
    ax.text(x * W + BW / 2, -y * H, "\n".join(textwrap.wrap(i, 21)), ha="center", va="center", fontsize=10, color=tc, fontweight="bold" if n["tipo"] == "cargo" else "normal", zorder=3)
# leyenda
ly = -hojas[0] * H + 0.1
for k, (a, c) in enumerate(COLOR.items()):
    ax.add_patch(FancyBboxPatch((k * 3.1, ly - 0.15), 0.35, 0.3, boxstyle="round,pad=0.01", fc=c, ec=c))
    ax.text(k * 3.1 + 0.45, ly, a, va="center", fontsize=10)
ax.text(0, ly - 0.55, "Recuadro punteado: jefatura que no figura entre el personal activo de la sede.", fontsize=9, color="#546E7A")
ax.set_xlim(-0.2, (prof_max + 1) * W); ax.set_ylim(ly - 0.9, 0.6); ax.axis("off")
out = BASE / "assets" / "slides" / "organigrama.jpg"
fig.savefig(out, dpi=105, bbox_inches="tight", facecolor="white", pil_kwargs={"quality": 88})
print("organigrama guardado:", out)
