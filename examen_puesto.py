# -*- coding: utf-8 -*-
"""
Catálogo de puestos (puestos.json: los cargos activos de la base de datos de PMA, con su ficha del MOF
o una ficha provisional) y generador del examen de cada puesto.

Las preguntas se arman con la información de la ficha; las opciones incorrectas salen de otros puestos.
Si la ficha es provisional (creada por Capital Humano), no se preguntan funciones ni misión: el examen
usa solo lo que está confirmado (horario del cuadro 2026, a quién reporta si está confirmado y las
responsabilidades de seguridad y antisoborno, que son iguales para todos).
"""
import json
import random
import re
from pathlib import Path

from horarios import GRUPOS, grupos_de

_BASE = Path(__file__).parent
PUESTOS = json.loads((_BASE / "puestos.json").read_text(encoding="utf-8"))

ORDEN_AREAS = ["Distribución", "Ventas", "Almacén", "Administración", "Operador Logístico"]


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
    """Cuántos puestos distintos comparten cada función (las variantes de un puesto cuentan una sola vez)."""
    f, vistos = {}, set()
    for p in PUESTOS:
        firma = json.dumps(p["funciones"], ensure_ascii=False)
        if firma in vistos:
            continue
        vistos.add(firma)
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


def _armar(rng, texto, correcta, distractores, explicacion, qid):
    opciones = [correcta] + distractores[:3]
    rng.shuffle(opciones)
    return {"id": qid, "texto": texto, "opciones": opciones, "correcta": opciones.index(correcta), "explicacion": explicacion}


# ------------------------------------------------------------------ generador
def generar_examen(nombre, semilla=None, con_horario=True):
    rng = random.Random(semilla if semilla is not None else nombre)
    p = get_puesto(nombre)
    creada = p.get("provisional_creada", False)
    otros = [o for o in PUESTOS if o["nombre"] != nombre and not o.get("provisional_creada")]
    fuente = f"Fuente: MOF, puesto {nombre}."
    slug = re.sub(r"\W+", "-", _norm(nombre))[:20]
    qs = []

    def nid():
        return f"EX-{slug}-{len(qs) + 1}"

    # 1. Misión del puesto
    if p.get("mision") and not creada:
        correcta = _recorta(p["mision"])
        pool = [_recorta(o["mision"]) for o in otros if o.get("mision") and not _parecidas(o["mision"], p["mision"])]
        pool = sorted(set(pool))
        rng.shuffle(pool)
        if len(pool) >= 3:
            qs.append(_armar(rng, "¿Cuál es la misión de tu puesto?", correcta, pool[:3], f"Esa es la misión de tu puesto. {fuente}", nid()))

    # 2. A quién reportas (solo si está confirmado)
    if p["reporta_a"] and p.get("reporta_confirmado", True):
        correcta = p["reporta_a"][0]
        propios = {_norm(x) for x in p["reporta_a"]}
        vistos = {}
        for o in PUESTOS:
            if o["nombre"] != nombre and o["reporta_a"] and o.get("reporta_confirmado", True):
                for x in o["reporta_a"]:
                    if _norm(x) not in propios:
                        vistos.setdefault(_norm(x), x)
        pool = sorted(vistos.values())
        rng.shuffle(pool)
        if len(pool) >= 3:
            qs.append(_armar(rng, "¿A quién reportas en tu puesto?", correcta, pool[:3], f"Reportas a: {correcta}. {fuente}", nid()))

    # 3. Funciones propias vs. ajenas
    if not creada:
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

    # 4. Horario (cuadro de horarios PMA Chimbote 2026). Si el puesto no está en el cuadro, no se pregunta.
    gs = grupos_de(nombre) if con_horario else []
    if len(gs) == 1 and gs[0]["id"] != "distribucion":
        correcta = gs[0]["resumen"]
        pool = sorted({g["resumen"] for g in GRUPOS.values() if g["id"] != "distribucion" and _norm(g["resumen"]) != _norm(correcta)})
        rng.shuffle(pool)
        if len(pool) >= 3:
            qs.append(_armar(rng, "Según el cuadro de horarios 2026, ¿cuál es tu horario de trabajo?", correcta, pool[:3],
                             f"Tu horario: {correcta}. Fuente: cuadro de horarios PMA Chimbote 2026.", nid()))

    # 5. Día de descanso (solo fichas del MOF)
    d = p["descanso"]
    if d and not creada and all(g.get("descanso_q", True) for g in gs):
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

    # 7. Seguridad y antisoborno (MOF: responsabilidades SIG, iguales para todos los puestos)
    sig = "Fuente: MOF, responsabilidades en calidad, seguridad, salud ocupacional y medio ambiente (SIG)."
    qs.append(_armar(
        rng, "Un cliente o proveedor te ofrece un regalo a cambio de un favor. ¿Qué debes hacer?",
        "No aceptarlo y reportarlo (política antisoborno)",
        ["Aceptarlo si es pequeño", "Aceptarlo y no decir nada", "Compartirlo con el equipo"],
        "El MOF indica no aceptar regalos, atenciones, donaciones ni beneficios similares para beneficio propio. " + sig, nid()))
    qs.append(_armar(
        rng, "Si notas un incumplimiento de la política antisoborno, ¿qué debes hacer?",
        "Reportarlo",
        ["Ignorarlo si no te afecta", "Esperar a que otra persona lo reporte", "Comentarlo solo con tus compañeros"],
        "Debes reportar cualquier inquietud o incumplimiento de la política antisoborno. " + sig, nid()))
    qs.append(_armar(
        rng, "Si en tu trabajo no existe un procedimiento para una situación, o el que existe no es adecuado, ¿qué debes hacer?",
        "Identificar la situación y comunicarla",
        ["Resolverla a tu manera sin avisar", "Esperar a que ocurra un incidente", "Ignorarla"],
        "El MOF indica seguir los procedimientos y comunicar las situaciones para las que no existen procedimientos o no son los adecuados. " + sig, nid()))
    return qs
