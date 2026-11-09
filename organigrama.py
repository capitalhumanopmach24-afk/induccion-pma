# -*- coding: utf-8 -*-
"""Organigrama de la sede (organigrama.json): consulta de la línea de mando y dibujo de la imagen."""
import json
from pathlib import Path

_D = json.loads((Path(__file__).parent / "organigrama.json").read_text(encoding="utf-8"))
TITULO = _D["titulo"]
NODOS = {n["id"]: n for n in _D["nodos"]}


def jefes_de(nombre):
    """Cadena de mando hacia arriba (del jefe inmediato hasta Gerencia)."""
    out, n = [], NODOS.get(nombre)
    while n and n["padre"]:
        n = NODOS[n["padre"]]
        out.append(n["id"])
    return out


def subordinados_de(nombre):
    return [n["id"] for n in _D["nodos"] if n["padre"] == nombre]
