# -*- coding: utf-8 -*-
"""
Inducción General de Capital Humano - Distribuidora PMA E.I.R.L. (versión juego, v2)

Ejecutar:   streamlit run app.py
"""
import base64
import csv
import json
import os
import random
import urllib.request
from datetime import datetime
from pathlib import Path

import streamlit as st

from bloques import BLOQUES, COMITE
from examen_puesto import areas, generar_examen, get_puesto, puestos_de

BASE = Path(__file__).parent
SLIDES = BASE / "assets" / "slides"
PUESTOS_IMG = BASE / "assets" / "puestos"
COMITE_IMG = BASE / "assets" / "comite"
LOGO = BASE / "assets" / "logo_pma.jpg"
DATA = BASE / "data"
ARCH_RESULTADOS = DATA / "resultados.csv"
ARCH_RESPUESTAS = DATA / "respuestas.csv"

IDX_PUESTO = 5  # bloque 6: ficha y examen del puesto
IDX_MARCACION = 2  # bloque 3: lleva una pregunta que depende del puesto

ENCABEZADO_RESPUESTAS = ["fecha", "nombre", "puesto", "bloque", "pregunta_id", "intento", "correcto"]
ENCABEZADO_RESULTADOS = ["fecha", "nombre", "puesto", "area", "sede", "puntos", "maximo", "porcentaje", "nota_examen_puesto", "aprobado"]

PTS_PRIMER_INTENTO = 10
PTS_SEGUNDO_INTENTO = 5
UMBRAL_APROBAR = 0.70  # mínimo para pasar un bloque
UMBRAL_INSIGNIA = 0.80  # para ganar la insignia del bloque

st.set_page_config(page_title="Inducción PMA", page_icon="🥤", layout="centered")

st.markdown(
    """
    <style>
      .block-container {padding-top: 4.5rem; padding-bottom: 3rem; max-width: 720px;}
      h1, h2, h3 {color: #5B2D8E;}
      div.stButton > button {
          width: 100%; min-height: 3rem; border-radius: 12px;
          font-size: 1.05rem; text-align: left; white-space: normal;
      }
      .linea-roja {border-bottom: 3px solid #C8102E; margin: 0.2rem 0 1rem 0;}
      .puntos {text-align: right; font-weight: 700; color: #5B2D8E;}
    </style>
    """,
    unsafe_allow_html=True,
)

ss = st.session_state


# --------------------------------------------------------------------------- datos
def puesto_actual():
    return get_puesto(ss.puesto)


def preguntas_marcacion():
    """Pregunta sobre marcación según el puesto (solo entrada o entrada y salida)."""
    if puesto_actual()["no_fiscaliza"]:
        return {
            "id": "B3-M",
            "texto": "¿Cuántas veces marcas asistencia al día en tu puesto?",
            "opciones": ["Dos veces: entrada y salida", "Solo una vez: mi entrada", "Cuatro veces", "No marco asistencia"],
            "correcta": 1,
            "explicacion": "Tu puesto no está sujeto a fiscalización horaria: marcas una sola vez, tu entrada.",
        }
    return {
        "id": "B3-M",
        "texto": "En tu puesto, ¿qué debes registrar en la marcación de asistencia?",
        "opciones": ["Solo mi entrada", "Mi ingreso y mi salida", "Solo mi salida", "Nada, no es obligatorio"],
        "correcta": 1,
        "explicacion": "Debes registrar tu ingreso y tu salida del centro de trabajo. Si no registras tu asistencia, se considera una falta pasible de descuento.",
    }


def preguntas_de(i):
    if i == IDX_PUESTO:
        return ss.examen
    qs = list(BLOQUES[i]["preguntas"])
    if i == IDX_MARCACION:
        qs.insert(4, preguntas_marcacion())
    return qs


def tarjetas_de(i):
    return BLOQUES[i]["tarjetas"]


def max_bloque(i):
    return PTS_PRIMER_INTENTO * len(preguntas_de(i))


def max_total():
    return sum(max_bloque(i) for i in range(len(BLOQUES)))


def total_puntos():
    return sum(ss.puntos_bloque.values())


# --------------------------------------------------------------------------- registro
def _secreto(nombre):
    """Lee un valor de variable de entorno o de los Secrets de Streamlit."""
    valor = os.environ.get(nombre, "")
    if not valor:
        try:
            valor = str(st.secrets.get(nombre, ""))
        except Exception:
            valor = ""
    return valor


def enviar_a_hoja(envios):
    """Envía filas a la hoja de Google (Apps Script). None = no configurado, True/False = resultado."""
    url = _secreto("HOJA_URL")
    if not url:
        return None
    cuerpo = json.dumps({"token": _secreto("HOJA_TOKEN"), "envios": envios}).encode("utf-8")
    req = urllib.request.Request(url, data=cuerpo, headers={"Content-Type": "text/plain; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.read().decode("utf-8", "ignore").strip().lower().startswith("ok")
    except Exception:
        return False


def _agregar_csv(ruta, encabezado, fila):
    try:
        DATA.mkdir(exist_ok=True)
        nuevo = not ruta.exists()
        with open(ruta, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if nuevo:
                w.writerow(encabezado)
            w.writerow(fila)
    except OSError:
        pass  # el juego no debe caerse si no se puede escribir el registro


def registrar_respuesta(q, intento, correcto):
    qid = q["id"]
    clave = qid if not qid.startswith("EX-") else f"EX|{ss.puesto}|{q['opciones'][q['correcta']][:50]}"
    fila = [datetime.now().isoformat(timespec="seconds"), ss.nombre, ss.puesto, BLOQUES[ss.bloque]["titulo"], clave, intento, int(correcto)]
    ss.log_respuestas.append(fila)
    _agregar_csv(ARCH_RESPUESTAS, ENCABEZADO_RESPUESTAS, fila)


def registrar_resultado():
    if ss.get("guardado"):
        return
    total, mx = total_puntos(), max_total()
    ex = ss.puntos_bloque.get(IDX_PUESTO, 0)
    ex_max = max_bloque(IDX_PUESTO)
    fila = [
        datetime.now().isoformat(timespec="seconds"),
        ss.nombre,
        ss.puesto,
        ss.area,
        ss.sede,
        total,
        mx,
        round(100 * total / mx) if mx else 0,
        round(100 * ex / ex_max) if ex_max else 0,
        "SI",
    ]
    _agregar_csv(ARCH_RESULTADOS, ENCABEZADO_RESULTADOS, fila)
    ss.payload = [
        {"hoja": "resultados", "encabezado": ENCABEZADO_RESULTADOS, "filas": [fila]},
        {"hoja": "respuestas", "encabezado": ENCABEZADO_RESPUESTAS, "filas": list(ss.log_respuestas)},
    ]
    with st.spinner("Registrando tus resultados..."):
        ss.envio = enviar_a_hoja(ss.payload)
    ss.guardado = True


def reintentar_envio():
    ss.envio = enviar_a_hoja(ss.payload)


# --------------------------------------------------------------------------- estado
def iniciar_estado():
    ss.setdefault("etapa", "inicio")  # inicio | mapa | bloque | final
    ss.setdefault("bloque", 0)
    ss.setdefault("fase", "tarjetas")  # tarjetas | preguntas | resumen
    ss.setdefault("repaso", False)
    ss.setdefault("card_i", 0)
    ss.setdefault("q_i", 0)
    ss.setdefault("intentos", 0)
    ss.setdefault("estado_q", None)  # None | reintento | ok | fallo
    ss.setdefault("descartadas", [])
    ss.setdefault("puntos_bloque", {})
    ss.setdefault("aprobados", {})
    ss.setdefault("insignias", {})
    ss.setdefault("nombre", "")
    ss.setdefault("puesto", "")
    ss.setdefault("area", "")
    ss.setdefault("sede", "")
    ss.setdefault("examen", [])
    ss.setdefault("log_respuestas", [])
    ss.setdefault("envio", None)


def reiniciar_pregunta():
    ss.intentos = 0
    ss.estado_q = None
    ss.descartadas = []


def comenzar():
    # Los campos del formulario usan claves "w_*": Streamlit las borra al dejar de
    # mostrarse, así que se copian a variables propias.
    ss.nombre = ss.w_nombre.strip()
    ss.area = ss.w_area
    ss.puesto = ss.w_puesto
    ss.sede = ss.get("w_sede", "").strip()
    ss.examen = generar_examen(ss.puesto, random.randrange(10**9))
    ss.puntos_bloque, ss.aprobados, ss.insignias = {}, {}, {}
    ss.log_respuestas, ss.envio = [], None
    ss.guardado = False
    ss.globos = False
    ss.etapa = "mapa"
    reiniciar_pregunta()


def abrir_bloque(i):
    ss.bloque = i
    ss.etapa = "bloque"
    ss.fase = "tarjetas"
    ss.card_i = 0
    ss.repaso = bool(ss.aprobados.get(i))
    reiniciar_pregunta()


def volver_mapa():
    ss.etapa = "mapa"


def card_siguiente():
    ss.card_i += 1


def card_anterior():
    ss.card_i = max(0, ss.card_i - 1)


def ir_a_preguntas():
    ss.fase = "preguntas"
    ss.q_i = 0
    ss.puntos_bloque[ss.bloque] = 0
    reiniciar_pregunta()


def responder(i):
    q = preguntas_de(ss.bloque)[ss.q_i]
    ss.intentos += 1
    ok = i == q["correcta"]
    registrar_respuesta(q, ss.intentos, ok)
    if ok:
        ss.estado_q = "ok"
        ss.puntos_bloque[ss.bloque] += PTS_PRIMER_INTENTO if ss.intentos == 1 else PTS_SEGUNDO_INTENTO
    elif ss.intentos >= 2:
        ss.estado_q = "fallo"
    else:
        ss.estado_q = "reintento"
        ss.descartadas = ss.descartadas + [i]


def pregunta_siguiente():
    ss.q_i += 1
    reiniciar_pregunta()
    if ss.q_i >= len(preguntas_de(ss.bloque)):
        ss.fase = "resumen"
        mx = max_bloque(ss.bloque)
        pct = ss.puntos_bloque.get(ss.bloque, 0) / mx if mx else 0
        if pct >= UMBRAL_APROBAR:
            ss.aprobados[ss.bloque] = True
        if pct >= UMBRAL_INSIGNIA:
            ss.insignias[ss.bloque] = True


def repetir_bloque():
    if ss.bloque == IDX_PUESTO:  # nuevo examen con otras preguntas
        ss.examen = generar_examen(ss.puesto, random.randrange(10**9))
    ss.fase = "tarjetas"
    ss.card_i = 0
    ss.puntos_bloque.pop(ss.bloque, None)
    reiniciar_pregunta()


def ver_final():
    ss.etapa = "final"


# --------------------------------------------------------------------------- vistas
def cabecera():
    c1, c2 = st.columns([1, 5])
    with c1:
        mostrar_imagen(LOGO.name, LOGO.parent, ancho=64)
    with c2:
        st.markdown("### Inducción general · Capital Humano")
    st.markdown('<div class="linea-roja"></div>', unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def _data_uri(ruta):
    mime = "image/png" if ruta.lower().endswith(".png") else "image/jpeg"
    with open(ruta, "rb") as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode()


def mostrar_imagen(nombre, carpeta=SLIDES, ancho=None):
    """Muestra una imagen incrustada en la página (evita imágenes rotas)."""
    ruta = carpeta / nombre
    if ruta.exists():
        w = f"{ancho}px" if ancho else "100%"
        st.markdown(
            f'<img src="{_data_uri(str(ruta))}" alt="" style="width:{w};max-width:100%;border-radius:8px;display:block;margin:.4rem 0;">',
            unsafe_allow_html=True,
        )


def vista_inicio():
    cabecera()
    st.markdown("## ¡Bienvenido a PMA! 🥤")
    st.write(
        "Recorre **7 bloques cortos**: lee la información, responde la prueba de cada bloque, "
        "gana puntos e insignias. Tus respuestas se guardan para Capital Humano."
    )
    st.text_input("Tu nombre y apellido", key="w_nombre", placeholder="Ej.: Juan Pérez")
    area = st.selectbox("Tu área", areas(), key="w_area")
    st.selectbox("Tu puesto", puestos_de(area), key="w_puesto")
    st.text_input("Tu sede (opcional)", key="w_sede", placeholder="Ej.: Chimbote")
    st.caption("Escribe tu nombre y presiona Enter para activar el botón.")
    st.button("🚀 Comenzar", type="primary", disabled=not ss.get("w_nombre", "").strip(), on_click=comenzar)


def vista_mapa():
    cabecera()
    st.markdown(f"## Tu recorrido, {ss.nombre.split()[0]} 🗺️")
    st.caption(f"Puesto: {ss.puesto}")
    hechos = sum(1 for i in range(len(BLOQUES)) if ss.aprobados.get(i))
    st.progress(hechos / len(BLOQUES))
    c1, c2 = st.columns([3, 1])
    with c1:
        st.caption(f"{hechos} de {len(BLOQUES)} bloques completados")
    with c2:
        st.markdown(f'<div class="puntos">⭐ {total_puntos()} pts</div>', unsafe_allow_html=True)

    siguiente = next((i for i in range(len(BLOQUES)) if not ss.aprobados.get(i)), None)
    for i, b in enumerate(BLOQUES):
        n = f"{i + 1}. {b['titulo']}"
        if ss.aprobados.get(i):
            mx = max_bloque(i)
            medalla = " 🏅" if ss.insignias.get(i) else ""
            st.button(f"✅ {n} · {ss.puntos_bloque.get(i, 0)}/{mx}{medalla}", key=f"bl_{i}", on_click=abrir_bloque, args=(i,))
        elif i == siguiente:
            st.button(f"▶️ {n}", key=f"bl_{i}", type="primary", on_click=abrir_bloque, args=(i,))
        else:
            st.button(f"🔒 {n}", key=f"bl_{i}", disabled=True)
    if siguiente is None:
        st.success("¡Completaste todos los bloques!")
        st.button("🏆 Ver mi resultado final", type="primary", on_click=ver_final)
    else:
        st.caption("Los bloques completados se pueden repasar cuando quieras.")


def barra_bloque():
    b = ss.bloque
    st.progress(b / len(BLOQUES))
    c1, c2 = st.columns([3, 1])
    with c1:
        st.caption(f"Bloque {b + 1} de {len(BLOQUES)}" + (" · repaso" if ss.repaso and ss.fase == "tarjetas" else ""))
    with c2:
        st.markdown(f'<div class="puntos">⭐ {total_puntos()} pts</div>', unsafe_allow_html=True)
    st.markdown(f"## {BLOQUES[b]['icono']} {BLOQUES[b]['titulo']}")


# ---- tarjetas especiales
def card_marcacion():
    p = puesto_actual()
    st.markdown("### 🖐️ Marcación de asistencia")
    if p["no_fiscaliza"]:
        st.markdown("- Tu puesto no está sujeto a fiscalización horaria: **marcas una sola vez, tu entrada**.")
    else:
        st.markdown(
            "- Debes registrar tu **ingreso y salida** del centro de trabajo. "
            "Si no registras tu asistencia, se considera una falta pasible de descuento."
        )
    st.markdown(
        "- La marcación es personal: marcar, modificar o suplantar a otro trabajador es una **falta grave**.\n"
        "- Si hay algún problema con la marcación, avisa de inmediato a Recursos Humanos, en un plazo de **24 horas**."
    )


def card_comite(t):
    st.markdown(f"### {t['icono']} {t['titulo']}")
    for pto in t["puntos"]:
        st.markdown(f"- {pto}")
    for fila in (COMITE[:2], COMITE[2:]):
        cols = st.columns(2)
        for col, m in zip(cols, fila):
            with col:
                mostrar_imagen(m["foto"], COMITE_IMG)
                st.markdown(f"**{m['nombre']}**")
                st.caption(m["cargo"])


def _lista(items):
    for x in items:
        st.markdown(f"- {x}")


def card_ficha():
    p = puesto_actual()
    st.markdown(f"### 🪪 {p['nombre']}")
    st.caption(f"Área: {p['area']} · Información del Manual de Organización y Funciones (MOF)")
    tabs = st.tabs(["🎯 Misión", "🧰 Funciones", "🕘 Horario", "📋 Requisitos", "🦺 Seguridad"])
    with tabs[0]:
        st.markdown(p["mision"])
        st.markdown("**Tu línea de mando**")
        reporta = ", ".join(p["reporta_a"]) if p["reporta_a"] else "Dirección de la empresa"
        st.markdown(f"⬆️ **Reportas a:** {reporta}")
        st.markdown(f"🧑 **Tú:** {p['nombre']}")
        if p["le_reportan"]:
            st.markdown("⬇️ **Te reportan / trabajas con:**")
            _lista(p["le_reportan"])
        mapa = PUESTOS_IMG / "mapa.json"
        if mapa.exists():
            img = json.loads(mapa.read_text(encoding="utf-8")).get(p["nombre"])
            if img:
                mostrar_imagen(img, PUESTOS_IMG, ancho=200)
    with tabs[1]:
        total = sum(len(g["items"]) for g in p["funciones"])
        st.caption(f"{total} funciones. Toca cada grupo para abrirlo.")
        if len(p["funciones"]) == 1:
            _lista(p["funciones"][0]["items"])
        else:
            for k, g in enumerate(p["funciones"]):
                with st.expander(f"{g['grupo']} ({len(g['items'])})", expanded=(k == 0)):
                    _lista(g["items"])
    with tabs[2]:
        _lista(p["horario"])
        if p["descanso"]:
            st.markdown(f"**Periodo de descanso:** {p['descanso']}")
        if p["no_fiscaliza"]:
            st.info("Tu puesto no está sujeto a fiscalización horaria: marcas una sola vez, tu entrada.")
        else:
            st.info("Debes registrar tu ingreso y tu salida en la marcación de asistencia.")
    with tabs[3]:
        for titulo, datos in (
            ("Requisitos generales", p["req_generales"]),
            ("Conocimientos", p["req_conocimientos"]),
            ("Experiencia", p["req_experiencia"]),
        ):
            if datos:
                st.markdown(f"**{titulo}**")
                _lista(datos)
    with tabs[4]:
        st.caption("Estas responsabilidades de calidad, seguridad, salud ocupacional y medio ambiente aplican a tu puesto.")
        _lista(p["sig"])


def vista_tarjetas():
    barra_bloque()
    tarjetas = tarjetas_de(ss.bloque)
    total = len(tarjetas)
    ss.card_i = min(ss.card_i, total - 1)
    t = tarjetas[ss.card_i]

    st.caption(f"Tarjeta {ss.card_i + 1} de {total}")
    with st.container(border=True):
        tipo = t.get("tipo")
        if tipo == "ficha":
            card_ficha()
        elif tipo == "marcacion":
            card_marcacion()
        elif tipo == "comite":
            card_comite(t)
        else:
            st.markdown(f"### {t.get('icono', '')} {t['titulo']}")
            for pto in t["puntos"]:
                st.markdown(f"- {pto}")
            for clave in ("imagen", "imagen2", "imagen3"):
                if t.get(clave):
                    mostrar_imagen(t[clave])

    c1, c2 = st.columns(2)
    with c1:
        st.button("⬅️ Anterior", on_click=card_anterior, disabled=ss.card_i == 0)
    with c2:
        if ss.card_i < total - 1:
            st.button("Siguiente ➡️", type="primary", on_click=card_siguiente)
        elif ss.repaso:
            st.button("🗺️ Volver al mapa", type="primary", on_click=volver_mapa)
        else:
            etiqueta = "📝 Ir a mi examen" if ss.bloque == IDX_PUESTO else "🎮 ¡A la prueba!"
            st.button(etiqueta, type="primary", on_click=ir_a_preguntas)
    if not ss.repaso:
        st.button("🗺️ Salir al mapa", key="salir_mapa", on_click=volver_mapa)


def vista_pregunta():
    barra_bloque()
    preguntas = preguntas_de(ss.bloque)
    q = preguntas[ss.q_i]
    st.caption(f"{'Examen' if ss.bloque == IDX_PUESTO else 'Pregunta'} {ss.q_i + 1} de {len(preguntas)}")
    st.markdown(f"#### {q['texto']}")

    if ss.estado_q in (None, "reintento"):
        if ss.estado_q == "reintento":
            st.warning(f"Casi. Inténtalo otra vez (ahora vale {PTS_SEGUNDO_INTENTO} puntos).")
        for i, opcion in enumerate(q["opciones"]):
            if i in ss.descartadas:
                continue
            st.button(opcion, key=f"op_{ss.bloque}_{ss.q_i}_{i}", on_click=responder, args=(i,))
    else:
        correcta = q["opciones"][q["correcta"]]
        if ss.estado_q == "ok":
            ganados = PTS_PRIMER_INTENTO if ss.intentos == 1 else PTS_SEGUNDO_INTENTO
            st.success(f"¡Correcto! +{ganados} puntos")
        else:
            st.error(f"La respuesta correcta era: **{correcta}**")
        st.info(q["explicacion"])
        etiqueta = "Siguiente ➡️" if ss.q_i + 1 < len(preguntas) else "Ver mi resultado 🏁"
        st.button(etiqueta, type="primary", on_click=pregunta_siguiente)


def vista_resumen():
    barra_bloque()
    pts, mx = ss.puntos_bloque.get(ss.bloque, 0), max_bloque(ss.bloque)
    pct = pts / mx if mx else 0
    st.markdown(f"### Resultado: {pts} de {mx} puntos ({round(pct * 100)}%)")
    st.progress(min(pct, 1.0))
    if pct >= UMBRAL_APROBAR:
        if pct >= UMBRAL_INSIGNIA:
            st.success(f"🏅 ¡Aprobaste y ganaste la insignia **{BLOQUES[ss.bloque]['insignia']}**!")
        else:
            st.success("✅ ¡Bloque aprobado! Con 80% o más ganas la insignia: puedes repetirlo si quieres.")
            st.button("🔁 Repetir para ganar la insignia", on_click=repetir_bloque)
        todos = all(ss.aprobados.get(i) for i in range(len(BLOQUES)))
        if todos:
            st.button("🏆 Ver mi resultado final", type="primary", on_click=ver_final)
        else:
            st.button("🗺️ Volver al mapa", type="primary", on_click=volver_mapa)
    else:
        st.warning("Necesitas al menos 70% para pasar este bloque. Repasa las tarjetas y vuelve a intentarlo.")
        st.button("🔁 Repasar y repetir", type="primary", on_click=repetir_bloque)


def vista_final():
    cabecera()
    registrar_resultado()
    total, mx = total_puntos(), max_total()
    pct = total / mx if mx else 0
    st.markdown(f"## 🏆 ¡Terminaste, {ss.nombre.split()[0]}!")
    st.markdown(f"### {total} de {mx} puntos ({round(pct * 100)}%)")
    st.progress(min(pct, 1.0))
    st.success("✅ Inducción general completada. ¡Bienvenido al equipo PMA!")
    if not ss.get("globos"):
        st.balloons()
        ss.globos = True
    insignias = [BLOQUES[i]["insignia"] for i in sorted(ss.insignias)]
    if insignias:
        st.markdown("**Tus insignias:**")
        for ins in insignias:
            st.markdown(f"- 🏅 {ins}")
    if ss.envio is False:
        st.warning("No se pudo enviar tu resultado a Capital Humano (revisa tu conexión). Presiona el botón para reintentar.")
        st.button("🔄 Reintentar envío", on_click=reintentar_envio)
    elif ss.envio is True:
        st.caption("Muestra esta pantalla a Capital Humano. Tus resultados ya fueron registrados.")
    else:
        st.caption("Muestra esta pantalla a Capital Humano.")
    st.button("Volver al inicio", on_click=lambda: ss.clear())


# --------------------------------------------------------------------------- panel RR.HH.
def clave_admin():
    clave = os.environ.get("CLAVE_ADMIN", "")
    if not clave:
        try:
            clave = st.secrets.get("CLAVE_ADMIN", "")
        except Exception:
            clave = ""
    return clave


def panel_capital_humano():
    import pandas as pd

    with st.sidebar.expander("🔒 Panel Capital Humano"):
        if _secreto("HOJA_URL"):
            st.caption("Los resultados se envían a la hoja de Google configurada: revísalos allí.")
        clave = clave_admin()
        if not clave:
            st.caption("Define la variable CLAVE_ADMIN para activar este panel.")
            return
        if st.text_input("Clave", type="password", key="clave_admin") != clave:
            return
        if ARCH_RESULTADOS.exists():
            res = pd.read_csv(ARCH_RESULTADOS)
            st.metric("Colaboradores que terminaron", len(res))
            st.metric("Promedio de puntaje (%)", round(res["porcentaje"].mean()))
            st.dataframe(res)
            st.download_button(
                "Descargar resultados (CSV)",
                res.to_csv(index=False).encode("utf-8-sig"),
                "resultados_induccion.csv",
                "text/csv",
            )
        else:
            st.caption("Aún no hay resultados.")
        if ARCH_RESPUESTAS.exists():
            r = pd.read_csv(ARCH_RESPUESTAS)
            primero = r[r["intento"] == 1]
            if len(primero):
                st.markdown("**% de error al primer intento, por pregunta**")
                err = (1 - primero.groupby("pregunta_id")["correcto"].mean()) * 100
                st.bar_chart(err.sort_values(ascending=False).head(15))


# --------------------------------------------------------------------------- principal
def main():
    iniciar_estado()
    panel_capital_humano()
    if ss.etapa == "inicio":
        vista_inicio()
    elif ss.etapa == "mapa":
        vista_mapa()
    elif ss.etapa == "final":
        vista_final()
    else:
        cabecera()
        if ss.fase == "tarjetas":
            vista_tarjetas()
        elif ss.fase == "preguntas":
            vista_pregunta()
        else:
            vista_resumen()


main()
