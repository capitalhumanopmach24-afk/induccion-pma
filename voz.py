# -*- coding: utf-8 -*-
"""
Voz de la inducción. Dos niveles, ambos gratuitos:

  1) Audio natural pre-generado (assets/audio/<clave>.mp3), creado una sola vez con generar_audios.py
     (edge-tts por defecto; Gemini opcional). Si el archivo existe, la app lo reproduce.
  2) Si no existe, la app lee el texto con la voz del propio celular o navegador (sin internet ni costo).

Este módulo solo arma los textos y las claves; no depende de Streamlit para poder usarlo desde el generador.
"""
import hashlib
import re
import unicodedata
from pathlib import Path

AUDIO_DIR = Path(__file__).parent / "assets" / "audio"

# Siglas que el lector de voz pronuncia mal si se dejan escritas igual.
PRONUNCIACION = {
    "SSO": "S S O", "SIG": "S I G", "CTS": "C T S", "EPP": "E P P", "EPPs": "E P Pes", "PMA": "P M A", "RIT": "R I T",
    "DM": "D M", "EsSalud": "Es Salud", "ACL": "A C L", "SAC": "S A C", "MOF": "M O F", "PDV": "P D V",
    "KKAA": "K K A A", "OL": "O L", "CDA": "C D A", "CCHH": "Capital Humano", "AFP": "A F P", "T1": "T uno", "T2": "T dos",
    "FEFO": "F E F O", "UIT": "U I T",
}
_EMOJI = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\uFE0F\u20E3\u200d]")


def _sin_tildes(t):
    return "".join(c for c in unicodedata.normalize("NFKD", t) if not unicodedata.combining(c))


def slug(t):
    return re.sub(r"[^a-z0-9]+", "-", _sin_tildes(t.lower())).strip("-")[:40]


def limpiar(texto):
    """Deja el texto listo para leerse en voz alta."""
    t = _EMOJI.sub("", texto or "")
    t = t.replace("*", "").replace("_", " ").replace("`", "").replace("«", "").replace("»", "")
    t = t.replace("%", " por ciento").replace("&", " y ").replace(" / ", " o ").replace("–", ", ").replace(" - ", ", ")
    for sigla, dicho in PRONUNCIACION.items():
        t = re.sub(rf"\b{re.escape(sigla)}\b", dicho, t)
    return re.sub(r"\s+", " ", t).strip()


def _frase(x):
    x = limpiar(x)
    return x if (not x or x[-1] in ".!?:;…") else x + "."


# ------------------------------------------------------------------ textos fijos de la marcación
MARCACION = {
    "entrada": [
        "Tu puesto no está sujeto a fiscalización horaria: **marcas una sola vez, tu entrada**.",
        "La marcación es personal: marcar, modificar o suplantar a otro trabajador es una **falta grave**.",
        "Si hay algún problema con la marcación, avisa de inmediato a Recursos Humanos, en un plazo de **24 horas**.",
    ],
    "entrada_salida": [
        "Debes registrar tu **ingreso y salida** del centro de trabajo. Si no registras tu asistencia, se considera una falta pasible de descuento.",
        "La marcación es personal: marcar, modificar o suplantar a otro trabajador es una **falta grave**.",
        "Si hay algún problema con la marcación, avisa de inmediato a Recursos Humanos, en un plazo de **24 horas**.",
    ],
    None: [
        "Consulta con Capital Humano si en tu puesto marcas ingreso y salida o solo tu ingreso.",
        "La marcación es personal: marcar, modificar o suplantar a otro trabajador es una **falta grave**.",
        "Si hay algún problema con la marcación, avisa de inmediato a Recursos Humanos, en un plazo de **24 horas**.",
    ],
}


# ------------------------------------------------------------------ textos de narración
def texto_tarjeta(t):
    return " ".join([_frase(t["titulo"])] + [_frase(x) for x in t.get("puntos", [])])


def texto_marcacion(modo):
    return " ".join([_frase("Marcación de asistencia")] + [_frase(x) for x in MARCACION[modo]])


def texto_comite(t, comite):
    miembros = "; ".join(f"{m['nombre']}, {m['cargo']}" for m in comite)
    return texto_tarjeta(t) + " " + _frase(f"Integrantes del Sub Comité: {miembros}")


def texto_ficha(p):
    partes = [_frase(f"Tu puesto: {p['nombre']}, del área de {p['area']}")]
    if p.get("nota"):
        partes.append(_frase(p["nota"]))
    if p.get("reporta_a"):
        partes.append(_frase("Reportas a " + " y ".join(p["reporta_a"])))
    if p.get("mision"):
        partes.append(_frase("Tu misión: " + p["mision"]))
    funs = [i for g in p["funciones"] for i in g["items"]][:6]
    if funs:
        partes.append("Algunas de tus funciones principales son: " + " ".join(_frase(f) for f in funs))
        partes.append("Revisa la pestaña Funciones para verlas todas.")
    return " ".join(partes)


def texto_horario(gs):
    if not gs:
        return "Tu horario aún no está registrado en el cuadro de horarios. Consulta con tu jefe o con Capital Humano."
    out = []
    for g in gs:
        if g["fiscalizado"]:
            filas = []
            for t in g["turnos"]:
                s = f"{t['turno']}: de lunes a viernes {t['lv']}"
                if t["sab"]:
                    s += f", sábado {t['sab']}"
                filas.append(_frase(s))
            out.append(_frase(f"Tu horario, {g['titulo']}") + " " + " ".join(filas) + " " + _frase(g["horas"]))
        else:
            ing = f" Hora de ingreso: {g['ingreso']}." if g.get("ingreso") else ""
            out.append(_frase(g["nota"]) + ing)
    return " ".join(out)


# ------------------------------------------------------------------ claves de audio
def clave_generica(bloque_i, card_i):
    return f"b{bloque_i + 1}_{card_i + 1}"


def clave_ficha(nombre_puesto):
    return f"ficha_{slug(nombre_puesto)}"


def clave_marcacion(modo):
    return f"marcacion_{modo or 'general'}"


def con_hash(clave, texto):
    """Agrega al nombre una huella del texto: si el texto cambia, el audio anterior ya no se usa."""
    return f"{clave}_{hashlib.md5(texto.encode('utf-8')).hexdigest()[:6]}"


def ruta_audio(clave):
    for ext in ("mp3", "wav"):
        r = AUDIO_DIR / f"{clave}.{ext}"
        if r.exists():
            return r
    return None


def elementos_audio(bloques, puestos, comite):
    """Lista de (clave, texto) de todo lo que se puede narrar. La usa generar_audios.py."""
    out = []
    for bi, b in enumerate(bloques):
        for ci, t in enumerate(b["tarjetas"]):
            tipo = t.get("tipo")
            if tipo == "ficha":
                for p in puestos:
                    t_ = texto_ficha(p)
                    out.append((con_hash(clave_ficha(p["nombre"]), t_), t_))
            elif tipo == "marcacion":
                for modo in ("entrada", "entrada_salida", None):
                    t_ = texto_marcacion(modo)
                    out.append((con_hash(clave_marcacion(modo), t_), t_))
            elif tipo == "horario":
                continue  # son tablas por puesto: se leen con la voz del dispositivo
            elif tipo == "comite":
                t_ = texto_comite(t, comite)
                out.append((con_hash(clave_generica(bi, ci), t_), t_))
            else:
                t_ = texto_tarjeta(t)
                out.append((con_hash(clave_generica(bi, ci), t_), t_))
    return out
