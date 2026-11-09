# -*- coding: utf-8 -*-
"""
Horarios de trabajo PMA Chimbote 2026 (de horario_2026.xls), guardados en horarios.json.
  "grupos":  cada fila del cuadro de horarios (turnos, horas semanales, si está o no sujeto a fiscalización).
  "puestos": qué grupo(s) de horario corresponde a cada puesto del MOF.
Para corregir un horario o asignar uno a un puesto, edita horarios.json.
"""
import json
from pathlib import Path

_D = json.loads((Path(__file__).parent / "horarios.json").read_text(encoding="utf-8"))
GRUPOS = {k: dict(v, id=k) for k, v in _D["grupos"].items()}
MAPA = _D["puestos"]


def grupos_de(nombre):
    return [GRUPOS[g] for g in MAPA.get(nombre, [])]


def tabla_md(g):
    filas = ["| Turno | Lunes a viernes | Sábado |", "|---|---|---|"]
    for t in g["turnos"]:
        filas.append(f"| {t['turno']} | {t['lv'] or '—'} | {t['sab'] or '—'} |")
    return "\n".join(filas)
