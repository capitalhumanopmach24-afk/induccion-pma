# -*- coding: utf-8 -*-
"""
Base de conocimiento del asistente «Pregúntale a PMA»: el RIT 2026, el RISST 2026, las fichas de puesto del MOF y el cuadro
de horarios, cortados en fragmentos (conocimiento.json). La búsqueda es por palabras clave (BM25), sin servicios externos:
solo los fragmentos más relevantes se envían a Gemini junto con la pregunta.
No incluye el contenido de la inducción (PPT) para no contradecir al RIT aprobado.
"""
import json
import math
import re
import unicodedata
from collections import Counter
from pathlib import Path

_RUTA = Path(__file__).parent / "conocimiento.json"
_PARADA = set("""a al algo ante con contra cual cuales cuando cuanto cuantos cuanta cuantas de del desde donde el ella ellos en entre era es esta estan este esto estos fue ha han hay la las le les lo los me mi mis mas muy no nos o otro para pero por que quien quienes se si sin sobre su sus tambien te tengo tiene tienen todo tu tus un una uno unos unas y ya yo
puedo puede pueden debo debe deben hacer hago como cual cuales quiero necesito saber sobre segun""".split())


def _norm(t):
    t = unicodedata.normalize("NFKD", t.lower())
    return "".join(c for c in t if not unicodedata.combining(c))


def _raiz(p):
    for suf in ("aciones", "acion", "amientos", "amiento", "mente", "idades", "idad", "ando", "iendo", "ados", "adas", "ado", "ada", "es", "s"):
        if p.endswith(suf) and len(p) - len(suf) >= 4:
            p = p[: -len(suf)]
            break
    if len(p) >= 7 and p.endswith(("ar", "er", "ir")):      # entregar -> entreg
        return p[:-2]
    if len(p) >= 6 and p[-1] in "aeiou":                    # renuncia / renuncio -> renunci
        return p[:-1]
    return p


# Palabras que usan los trabajadores y su equivalente en el reglamento.
_SINONIMOS = {
    "sancion": ["medida", "disciplinaria", "amonestacion", "suspension", "despido"],
    "castigo": ["medida", "disciplinaria", "sancion"],
    "marcar": ["registrar", "asistencia", "control", "tarjeta", "reloj"],
    "marcacion": ["registrar", "asistencia", "control", "tarjeta"],
    "marco": ["registrar", "asistencia", "control", "tarjeta", "falta", "grave"],
    "marcando": ["registrar", "asistencia", "control", "tarjeta", "falta", "grave"],
    "refrigerio": ["refrigerio", "almuerzo", "minutos"],
    "almuerzo": ["refrigerio"],
    "falta": ["inasistencia", "ausencia", "justificar"],
    "justificar": ["justificacion", "justificada", "documentacion", "inasistencia", "certificado"],
    "justificacion": ["documentacion", "inasistencia", "certificado"],
    "faltar": ["inasistencia", "ausencia", "justificar"],
    "tarde": ["tardanza"],
    "llegar": ["tardanza", "puntualidad"],
    "permiso": ["licencia", "autorizacion"],
    "despedir": ["despido"],
    "renunciar": ["renuncia", "retiro"],
    "sueldo": ["remuneracion"],
    "pago": ["remuneracion", "descuento"],
    "medico": ["certificado", "enfermedad", "salud"],
    "enfermo": ["enfermedad", "salud", "certificado"],
    "fumar": ["vapear", "fumar", "prohibido"],
    "uniforme": ["uniformes", "indumentaria", "ropa"],
    "casco": ["equipo", "proteccion", "epp"],
    "epp": ["equipo", "proteccion", "personal"],
    "accidente": ["accidentes", "informar", "incidente"],
    "regalo": ["dadivas", "regalos", "agasajos", "clientes"],
    "horario": ["jornada", "horas", "turno"],
    "horas extras": ["sobretiempo"],
}


def tokens(texto):
    out = []
    for p in re.findall(r"[a-z0-9]+", _norm(texto)):
        if p in _PARADA or (len(p) < 3 and not p.isdigit()):
            continue
        out.append(_raiz(p))
    return out


class Base:
    def __init__(self, fragmentos):
        self.f = fragmentos
        self.docs = [Counter(tokens(f["ref"] + " " + f.get("seccion", "") + " " + f["texto"])) for f in fragmentos]
        self.len = [sum(d.values()) for d in self.docs]
        self.avg = sum(self.len) / max(1, len(self.len))
        df = Counter()
        for d in self.docs:
            df.update(d.keys())
        n = len(self.docs)
        self.idf = {t: math.log(1 + (n - c + 0.5) / (c + 0.5)) for t, c in df.items()}

    def buscar(self, pregunta, k=6, fuentes=None):
        q = tokens(pregunta)
        extra = []
        for t in q:
            for clave, sin in _SINONIMOS.items():
                if t == _raiz(clave) or t == clave:
                    extra += [_raiz(_norm(s)) for s in sin]
        q = q + extra
        # si el trabajador cita un artículo («artículo 53»), ese fragmento va primero
        directos = []
        for n in re.findall(r"art[ií]culo\s+(\d+)", pregunta.lower()):
            directos += [dict(f, puntaje=99.0) for f in self.f if re.match(rf"Art\. {n}\b", f["ref"]) and (not fuentes or f["fuente"] in fuentes)]
        if not q:
            return []
        pun = []
        for i, d in enumerate(self.docs):
            if fuentes and self.f[i]["fuente"] not in fuentes:
                continue
            s = 0.0
            for t in q:
                if t in d:
                    tf = d[t]
                    s += self.idf.get(t, 0) * tf * 2.5 / (tf + 1.5 * (0.6 + 0.4 * self.len[i] / self.avg)) * (1.12 if self.f[i]["fuente"] == "RIT 2026" else 1.0)
            if s > 0:
                pun.append((s, i))
        pun.sort(reverse=True)
        return (directos + [dict(self.f[i], puntaje=round(s, 2)) for s, i in pun[:k]])[:k]

    def de_puesto(self, nombre):
        """Fragmentos de la ficha y del horario del puesto del trabajador."""
        return [f for f in self.f if f.get("puesto") == nombre]


def cargar():
    return Base(json.loads(_RUTA.read_text(encoding="utf-8")))
