# -*- coding: utf-8 -*-
"""
Catálogo de puestos (leído de puestos.json, extraído del MOF) y generador del examen
de cada puesto. Las preguntas se arman con la información del propio MOF; las opciones
incorrectas salen de otros puestos. Cada pregunta indica su fuente.
"""
import json
import random
import re
from pathlib import Path

_BASE = Path(__file__).parent
PUESTOS = json.loads((_BASE / "puestos.json").read_text(encoding="utf-8"))

ORDEN_AREAS = [
    "Distribución",
    "Ventas",
    "Almacén",
    "Servicios generales",
    "Mantenimiento y sistemas",
    "Administración y finanzas",
    "Capital Humano, SST y SIG",
    "Gerencia y apoyo",
]


def areas():
    return [a for a in ORDEN_AREAS if any(p["area"] == a for p in PUESTOS)]


def puestos_de(area):
    return [p["nombre"] for p in PUESTOS if p["area"] == area]


def get_puesto(nombre):
    return next(p for p in PUESTOS if p["nombre"] == nombre)


# ------------------------------------------------------------------ utilidades
def _norm(t):
    return re.sub(r"[^a-záéíóúñ0-9 ]", "", t.lower()).strip()


def _palabras(t):
    return {w for w in _norm(t).split() if len(w) > 3}


def _parecidas(a, b):
    pa, pb = _palabras(a), _palabras(b)
    if not pa or not pb:
        return False
    return len(pa & pb) / min(len(pa), len(pb)) > 0.6


def _mayus(t):
    t = t.strip(" .")
    return t[:1].upper() + t[1:]


def _recorta(t, n=165):
    t = t.strip()
    if len(t) <= n:
        return t
    return t[:n].rsplit(" ", 1)[0].rstrip(",;:") + "…"


def _funciones(p):
    return [i for g in p["funciones"] for i in g["items"]]


def _frecuencias():
    f = {}
    for p in PUESTOS:
        for i in set(_norm(x) for x in _funciones(p)):
            f[i] = f.get(i, 0) + 1
    return f


_FREQ = _frecuencias()


_GENERICAS = [
    "otras funciones", "inherente", "demás funciones", "cumplir con las normas", "seguridad e higiene",
    "epp", "capacitaci", "reportar", "informar de cualquier", "normas de seguridad",
    "sistema documentario", "procedimiento", "covid",
]


def _utiles(p):
    """Funciones propias del puesto aptas para preguntar (no genéricas)."""
    out = []
    for i in _funciones(p):
        n = _norm(i)
        if 18 <= len(i) <= 200 and _FREQ.get(n, 0) <= 2 and not any(k in i.lower() for k in _GENERICAS):
            out.append(i)
    return out


# ------------------------------------------------------------------ generador
def _armar(rng, texto, correcta, distractores, explicacion, qid):
    opciones = [correcta] + distractores[:3]
    rng.shuffle(opciones)
    return {
        "id": qid,
        "texto": texto,
        "opciones": opciones,
        "correcta": opciones.index(correcta),
        "explicacion": explicacion,
    }


def generar_examen(nombre, semilla=None):
    rng = random.Random(semilla if semilla is not None else nombre)
    p = get_puesto(nombre)
    otros = [o for o in PUESTOS if o["nombre"] != nombre]
    fuente = f"Fuente: MOF, puesto {nombre}."
    slug = re.sub(r"\W+", "-", _norm(nombre))[:20]
    qs = []

    def nid():
        return f"EX-{slug}-{len(qs) + 1}"

    # 1. Misión del puesto
    if p.get("mision"):
        correcta = _recorta(p["mision"])
        pool = [_recorta(o["mision"]) for o in otros if o.get("mision") and not _parecidas(o["mision"], p["mision"])]
        rng.shuffle(pool)
        if len(pool) >= 3:
            qs.append(_armar(rng, "¿Cuál es la misión de tu puesto?", correcta, pool[:3], f"Esa es la misión de tu puesto. {fuente}", nid()))

    # 2. A quién reportas
    if p["reporta_a"]:
        correcta = _mayus(p["reporta_a"][0]).title().replace(" De ", " de ").replace(" En El ", " en el ").replace(" Y ", " y ")
        propios = {_norm(x) for x in p["reporta_a"]}
        vistos = {}
        for o in otros:
            if o["reporta_a"] and _norm(o["reporta_a"][0]) not in propios:
                vistos.setdefault(_norm(o["reporta_a"][0]), _mayus(o["reporta_a"][0]).title().replace(" De ", " de ").replace(" En El ", " en el ").replace(" Y ", " y "))
        pool = sorted(vistos.values())
        rng.shuffle(pool)
        if len(pool) >= 3:
            qs.append(_armar(rng, "¿A quién reportas en tu puesto?", correcta, pool[:3], f"Reportas a: {correcta}. {fuente}", nid()))

    # 3. Funciones propias vs. ajenas
    propias = _utiles(p)
    rng.shuffle(propias)
    mis_funciones = _funciones(p)
    ajenas = []
    for o in otros:
        for i in _utiles(o):
            if not any(_parecidas(i, m) for m in mis_funciones):
                ajenas.append((o["area"] != p["area"], i))
    rng.shuffle(ajenas)
    ajenas.sort(key=lambda x: not x[0])  # primero las de otras áreas
    ajenas = [i for _, i in ajenas]
    usadas = set()

    def tomar_ajenas(n):
        out = []
        for i in ajenas:
            if i not in usadas and not any(_parecidas(i, x) for x in out):
                out.append(i)
                usadas.add(i)
            if len(out) == n:
                break
        return out

    n_es = 3 if len(propias) >= 6 else (2 if len(propias) >= 4 else 1)
    for k in range(n_es):
        if k < len(propias):
            d = tomar_ajenas(3)
            if len(d) == 3:
                qs.append(_armar(rng, "¿Cuál de estas es una función de tu puesto?", propias[k], d,
                                 f"Correcto: «{propias[k]}» es una función de tu puesto. {fuente}", nid()))
    if len(propias) >= n_es + 3:
        tres = propias[n_es:n_es + 3]
        d = tomar_ajenas(1)
        if d:
            qs.append(_armar(rng, "¿Cuál de estas NO es una función de tu puesto?", d[0], tres,
                             f"«{d[0]}» corresponde a otro puesto; las demás sí son funciones del tuyo. {fuente}", nid()))

    # 4. Horario
    if p["horario"]:
        hor = lambda x: _recorta(" ".join(x["horario"]).strip(" ."), 120)
        correcta = hor(p)
        pool = sorted({hor(o) for o in otros if o["horario"] and _norm(hor(o)) != _norm(correcta)})
        rng.shuffle(pool)
        if len(pool) >= 3:
            qs.append(_armar(rng, "Según el MOF, tu horario de trabajo es…", correcta, pool[:3], f"Tu horario: {correcta}. {fuente}", nid()))

    # 5. Día de descanso
    d = p["descanso"]
    if d:
        d = "Sábados y Domingos" if ("sábado" in d.lower() and "domingo" in d.lower()) else _mayus(d)
        base = ["Domingos", "Sábados y Domingos", "Lunes", "Miércoles"]
        if d in base:
            qs.append(_armar(rng, "¿Cuál es tu periodo de descanso?", d, [x for x in base if x != d], f"Tu descanso: {d}. {fuente}", nid()))

    # 6. Licencia de conducir
    if p["licencia"]:
        canon = lambda s: re.sub(r"\s+", "", s.lower().replace("necesario", "necesaria"))
        lic = p["licencia"].replace("No es necesario", "No es necesaria")
        vistos, pool = {canon(lic)}, []
        for o in otros:
            l = o["licencia"].replace("No es necesario", "No es necesaria")
            if l and canon(l) not in vistos:
                vistos.add(canon(l))
                pool.append(l)
        rng.shuffle(pool)
        if len(pool) >= 3:
            qs.append(_armar(rng, "¿Qué licencia de conducir se requiere para tu puesto?", lic, pool[:3], f"Requisito de licencia: {lic}. {fuente}", nid()))

    # 7. Antisoborno (común a todos los puestos, MOF: responsabilidades SIG)
    qs.append(_armar(
        rng,
        "Un cliente o proveedor te ofrece un regalo a cambio de un favor. ¿Qué debes hacer?",
        "No aceptarlo y reportarlo (política antisoborno)",
        ["Aceptarlo si es pequeño", "Aceptarlo y no decir nada", "Compartirlo con el equipo"],
        "El MOF indica no aceptar regalos, atenciones, donaciones ni beneficios similares para beneficio propio, y reportar cualquier incumplimiento de la política antisoborno.",
        nid(),
    ))
    return qs
