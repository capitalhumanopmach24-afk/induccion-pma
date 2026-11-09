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
from datetime import datetime
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from bloques import BLOQUES, COMITE
from examen_puesto import areas, generar_examen, get_puesto, puestos_de
import asistente
import conocimiento
from envio import CAMPOS_FORM, enviar_apps_script, enviar_formulario, parsear_enlace_form, probar_conexion
from horarios import grupos_de, tabla_md
from organigrama import NODOS, TITULO as TITULO_ORG, jefes_de, subordinados_de
from voz import (MARCACION, clave_ficha, clave_generica, clave_marcacion, con_hash, limpiar, ruta_audio,
                 texto_comite, texto_ficha, texto_horario, texto_marcacion, texto_tarjeta)

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

SEDES = ["Chimbote", "Trujillo", "Chocope", "Guadalupe"]  # sedes oficiales
# Sedes para las que existe información propia. Si agregas el cuadro de horarios o el comité
# de otra sede, añade su nombre aquí.
SEDES_HORARIO_2026 = {"Chimbote"}  # cuadro "HORARIOS DE TRABAJO - PMA CHIMBOTE 2026"
SEDES_COMITE = {"Chimbote"}  # Sub Comité de Hostigamiento Sexual Laboral - Chimbote 2026-2028

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
    """Pregunta sobre marcación según el puesto. Si no se sabe cómo marca el puesto, no se pregunta."""
    modo = puesto_actual().get("marcacion")
    if modo == "entrada":
        return {
            "id": "B3-M",
            "texto": "¿Cuántas veces marcas asistencia al día en tu puesto?",
            "opciones": ["Dos veces: entrada y salida", "Solo una vez: mi entrada", "Cuatro veces", "No marco asistencia"],
            "correcta": 1,
            "explicacion": "Tu puesto no está sujeto a fiscalización horaria: marcas una sola vez, tu entrada.",
        }
    if modo == "entrada_salida":
        return {
            "id": "B3-M",
            "texto": "En tu puesto, ¿qué debes registrar en la marcación de asistencia?",
            "opciones": ["Solo mi entrada", "Mi ingreso y mi salida", "Solo mi salida", "Nada, no es obligatorio"],
            "correcta": 1,
            "explicacion": "Debes registrar tu ingreso y tu salida del centro de trabajo. Si no registras tu asistencia, se considera una falta pasible de descuento.",
        }
    return None


def preguntas_de(i):
    if i == IDX_PUESTO:
        return ss.examen
    qs = list(BLOQUES[i]["preguntas"])
    if i == IDX_MARCACION:
        qm = preguntas_marcacion()
        if qm:
            qs.insert(4, qm)
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


MAX_PREGUNTAS_SESION = 8
ESPERA_ENTRE_PREGUNTAS = 4  # segundos


@st.cache_resource(show_spinner=False)
def _base_conocimiento():
    return conocimiento.cargar()


def asistente_activo():
    return bool(_secreto("GEMINI_API_KEY"))


def _consultar(pregunta, puesto, sede):
    return asistente.preguntar(
        pregunta, puesto, sede, _base_conocimiento(), _secreto("GEMINI_API_KEY"),
        modelo=_secreto("GEMINI_MODELO") or None,
        url_base=_secreto("GEMINI_URL_BASE") or asistente.URL_GEMINI,
        tope_dia=int(_secreto("PREGUNTAS_POR_DIA") or 300),
    )


def preguntar_cb():
    q = (ss.get("q_asistente") or "").strip()
    if not q:
        return
    ahora = datetime.now().timestamp()
    if ss.n_preguntas >= MAX_PREGUNTAS_SESION:
        ss.resp_asistente = {"tipo": "limite", "texto": "Llegaste al máximo de preguntas de esta sesión. Si te quedan dudas, consúltalas con Capital Humano.", "fuentes": []}
        return
    if ahora - ss.get("ultima_pregunta", 0) < ESPERA_ENTRE_PREGUNTAS:
        ss.resp_asistente = {"tipo": "error", "texto": "Espera unos segundos antes de hacer otra pregunta.", "fuentes": []}
        return
    ss.ultima_pregunta = ahora
    r = _consultar(q, ss.puesto, ss.sede)
    if r["tipo"] in ("ia", "fija"):
        ss.n_preguntas += 1
    ss.resp_asistente = r


def seccion_asistente():
    with st.expander("💬 ¿Tienes una duda? Pregúntale a PMA"):
        if not asistente_activo():
            st.caption("El asistente todavía no está activado.")
            return
        st.caption(
            "Responde con el Reglamento Interno de Trabajo, el reglamento de Seguridad y Salud, tu ficha de puesto y tu horario. "
            "**No escribas datos personales ni cuentes casos personales:** esta herramienta no es confidencial. "
            "Las respuestas son orientativas; ante cualquier duda consulta con Capital Humano."
        )
        q = st.text_input("Escribe tu pregunta", key="q_asistente", max_chars=asistente.MAX_PREGUNTA,
                          placeholder="Ej.: ¿Cuántos días tengo para justificar una falta?")
        st.button("Preguntar", key="btn_preguntar", on_click=preguntar_cb, disabled=not (q or "").strip())
        r = ss.get("resp_asistente")
        if r:
            if r["tipo"] == "error" or r["tipo"] == "limite":
                st.warning(r["texto"])
            else:
                st.markdown(r["texto"])
                if r["fuentes"]:
                    st.caption("Basado en: " + " · ".join(r["fuentes"]))
                escuchar(None, r["texto"])


def enviar_resultados():
    """Envía el resultado a Google. Devuelve (estado, detalle): True / False / None (sin hoja configurada)."""
    if _secreto("HOJA_URL"):
        return enviar_apps_script(_secreto("HOJA_URL"), _secreto("HOJA_TOKEN"), ss.payload)
    if _secreto("FORM_ENLACE"):
        return enviar_formulario(_secreto("FORM_ENLACE"), ss.valores_form)
    return None, "No hay hoja de resultados configurada."


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
    errores = ", ".join(r[4] for r in ss.log_respuestas if r[5] == 1 and r[6] == 0)[:900] or "ninguno"
    # mismo orden que CAMPOS_FORM
    ss.valores_form = [ss.nombre, ss.puesto, ss.area, ss.sede, str(total), str(fila[7]), str(fila[8]), errores]
    with st.spinner("Registrando tus resultados..."):
        ss.envio, ss.envio_detalle = enviar_resultados()
    ss.guardado = True


def reintentar_envio():
    ss.envio, ss.envio_detalle = enviar_resultados()


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
    ss.setdefault("envio_detalle", "")
    ss.setdefault("n_preguntas", 0)
    ss.setdefault("valores_form", [])


def reiniciar_pregunta():
    ss.intentos = 0
    ss.estado_q = None
    ss.descartadas = []


def examen_nuevo():
    return generar_examen(ss.puesto, random.randrange(10**9), con_horario=ss.sede in SEDES_HORARIO_2026)


def comenzar():
    # Los campos del formulario usan claves "w_*": Streamlit las borra al dejar de
    # mostrarse, así que se copian a variables propias.
    ss.nombre = ss.w_nombre.strip()
    ss.area = ss.w_area
    ss.puesto = ss.w_puesto
    ss.sede = ss.w_sede
    ss.examen = examen_nuevo()
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
        ss.examen = examen_nuevo()
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
    st.selectbox("Tu sede", SEDES, index=None, placeholder="Elige tu sede", key="w_sede")
    st.caption("Escribe tu nombre, elige tu sede y presiona Enter para activar el botón.")
    listo = bool(ss.get("w_nombre", "").strip()) and bool(ss.get("w_sede"))
    st.button("🚀 Comenzar", type="primary", disabled=not listo, on_click=comenzar)


def vista_mapa():
    cabecera()
    st.markdown(f"## Tu recorrido, {ss.nombre.split()[0]} 🗺️")
    st.caption(f"Puesto: {ss.puesto} · Sede: {ss.sede}")
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
    seccion_asistente()


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
    for linea in MARCACION[p.get("marcacion")]:
        st.markdown(f"- {linea}")


def _linea_mando(nombre):
    jefes = jefes_de(nombre)
    if jefes:
        st.markdown("⬆️ **Reporta a:** " + " → ".join(jefes))
    subs = subordinados_de(nombre)
    if subs:
        st.markdown("⬇️ **Le reportan:** " + ", ".join(subs))
    if not subs:
        st.markdown("⬇️ **Le reportan:** nadie (puesto operativo)")


def card_organigrama(t):
    st.markdown(f"### {t['icono']} {t['titulo']}")
    for pto in t["puntos"]:
        st.markdown(f"- {pto}")
    mostrar_imagen(t["imagen"])
    st.caption(TITULO_ORG + ". Si trabajas en otra sede, puede haber diferencias.")
    p = puesto_actual()
    st.markdown("**Tu línea de mando**")
    _linea_mando(p["nombre"])
    cargos = [n for n, d in NODOS.items() if d["tipo"] == "cargo"]
    elegido = st.selectbox(
        "Ver la línea de mando de otro puesto", cargos,
        index=cargos.index(p["nombre"]) if p["nombre"] in cargos else 0, key="org_ver",
    )
    if elegido != p["nombre"]:
        _linea_mando(elegido)


def card_comite(t):
    st.markdown(f"### {t['icono']} {t['titulo']}")
    for pto in t["puntos"]:
        st.markdown(f"- {pto}")
    if ss.get("sede") not in SEDES_COMITE:
        st.warning("Este es el Sub Comité de la sede Chimbote. Pregunta a Capital Humano de tu sede quién integra el comité que te corresponde.")
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


def render_horario(p):
    """Horario del puesto según el cuadro 2026; si no está en el cuadro, el del MOF (con aviso) o una indicación."""
    usa_cuadro = ss.get("sede") in SEDES_HORARIO_2026
    gs = grupos_de(p["nombre"]) if usa_cuadro else []
    if not gs:
        if not usa_cuadro:
            st.caption("El cuadro de horarios 2026 es de la sede Chimbote. Confirma tu horario con Capital Humano de tu sede.")
        if p["horario"] and not p.get("provisional_creada"):
            if usa_cuadro:
                st.caption("Tu horario exacto no está en el cuadro de horarios 2026. Lo siguiente viene del MOF: confirma el tuyo con Capital Humano.")
            _lista(p["horario"])
        elif usa_cuadro:
            st.info("Tu horario aún no está registrado en el cuadro de horarios. Consúltalo con tu jefe o con Capital Humano.")
    for g in gs:
        if len(gs) > 1:
            st.markdown(f"**{g['titulo']}**")
        if g["fiscalizado"]:
            st.markdown(tabla_md(g))
            st.caption(f"{g['horas']} · Cuadro de horarios PMA Chimbote 2026")
        else:
            if g.get("ingreso"):
                st.markdown(f"**Hora de ingreso:** {g['ingreso']}")
            st.info(g["nota"])
    if p["descanso"] and all(g.get("descanso_q", True) for g in gs):
        st.markdown(f"**Periodo de descanso:** {p['descanso']}")
    modo = p.get("marcacion")
    if modo and (not gs or all(g["fiscalizado"] for g in gs)):
        if modo == "entrada":
            st.info("Tu puesto no está sujeto a fiscalización horaria: marcas una sola vez, tu entrada.")
        else:
            st.info("Debes registrar tu ingreso y tu salida en la marcación de asistencia.")


def card_horario():
    st.markdown("### 🕘 Tu horario")
    render_horario(puesto_actual())


def card_ficha():
    p = puesto_actual()
    st.markdown(f"### 🪪 {p['nombre']}")
    origen = "" if p.get("provisional_creada") else " · Información del Manual de Organización y Funciones (MOF)"
    st.caption(f"Área: {p['area']}{origen}")
    if p.get("nota"):
        st.info(p["nota"])
    tabs = st.tabs(["🎯 Misión", "🧰 Funciones", "🕘 Horario", "📋 Requisitos", "🦺 Seguridad"])
    with tabs[0]:
        st.markdown(p["mision"])
        st.markdown("**Tu línea de mando**")
        reporta = ", ".join(p["reporta_a"]) if p["reporta_a"] else "Dirección de la empresa"
        if not p.get("reporta_confirmado", True):
            reporta += " (por confirmar)"
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
        render_horario(p)
    with tabs[3]:
        hay = False
        for titulo, datos in (
            ("Requisitos generales", p["req_generales"]),
            ("Conocimientos", p["req_conocimientos"]),
            ("Experiencia", p["req_experiencia"]),
        ):
            if datos:
                hay = True
                st.markdown(f"**{titulo}**")
                _lista(datos)
        if not hay:
            st.caption("Los requisitos de tu cargo aún no están definidos en el MOF.")
    with tabs[4]:
        st.caption("Estas responsabilidades de calidad, seguridad, salud ocupacional y medio ambiente aplican a tu puesto.")
        _lista(p["sig"])


# ---- voz: audio natural pre-generado (Gemini) o, si no existe, la voz del propio dispositivo (gratis)
@st.cache_data(show_spinner=False)
def _audio_b64(ruta):
    with open(ruta, "rb") as f:
        return base64.b64encode(f.read()).decode()


def _html_voz_dispositivo(texto):
    return """
<div style="font-family:sans-serif;display:flex;align-items:center;gap:8px">
  <button id="p" style="padding:6px 12px;border-radius:8px;border:1px solid #bbb;background:#fff;cursor:pointer;font-size:15px">🔊 Escuchar</button>
  <button id="s" style="padding:6px 12px;border-radius:8px;border:1px solid #bbb;background:#fff;cursor:pointer;font-size:15px">⏹ Detener</button>
  <span id="m" style="font-size:12px;color:#666"></span>
</div>
<script>
const TXT = __TEXTO__;
const p = document.getElementById('p'), s = document.getElementById('s'), m = document.getElementById('m');
function puntaje(v) {
  const n = (v.name || '').toLowerCase(), l = (v.lang || '').replace('_', '-').toLowerCase();
  if (!l.startsWith('es')) return -1;
  let q = 0;
  if (/natural|online|neural|premium|enhanced/.test(n)) q += 100;
  else if (/google/.test(n)) q += 80;
  if (v.localService === false) q += 10;
  const pref = ['es-pe', 'es-419', 'es-mx', 'es-us', 'es-co', 'es-ar', 'es-cl', 'es-es'];
  const i = pref.findIndex(x => l.startsWith(x));
  return q + (i < 0 ? 0 : pref.length - i);
}
function mejorVoz(vs) {
  let b = null, bp = -1;
  for (const v of vs) { const x = puntaje(v); if (x > bp) { bp = x; b = v; } }
  return bp >= 0 ? b : null;
}
function cargarVoces() {
  return new Promise(res => {
    const v = speechSynthesis.getVoices();
    if (v.length) return res(v);
    let listo = false;
    const fin = () => { if (!listo) { listo = true; res(speechSynthesis.getVoices()); } };
    speechSynthesis.addEventListener('voiceschanged', fin, { once: true });
    setTimeout(fin, 1500);
  });
}
if ('speechSynthesis' in window) speechSynthesis.getVoices();
p.onclick = async () => {
  if (!('speechSynthesis' in window)) { m.textContent = 'Tu navegador no permite voz.'; return; }
  speechSynthesis.cancel();
  const v = mejorVoz(await cargarVoces());
  const partes = TXT.match(/[^.!?:;]+[.!?:;]*/g) || [TXT];
  partes.forEach((t, i) => {
    const u = new SpeechSynthesisUtterance(t.trim());
    if (v) { u.voice = v; u.lang = v.lang; } else { u.lang = 'es-419'; }
    u.rate = 0.95;
    if (i === 0) u.onstart = () => m.textContent = 'Reproduciendo…';
    if (i === partes.length - 1) u.onend = () => m.textContent = '';
    speechSynthesis.speak(u);
  });
};
s.onclick = () => { speechSynthesis.cancel(); m.textContent = ''; };
window.addEventListener('pagehide', () => speechSynthesis.cancel());
</script>
""".replace("__TEXTO__", json.dumps(texto))


def escuchar(clave, texto):
    ruta = ruta_audio(clave) if clave else None
    if ruta:
        mime = "audio/mpeg" if ruta.suffix == ".mp3" else "audio/wav"
        components.html(
            f'<audio controls preload="none" style="width:100%;height:40px" src="data:{mime};base64,{_audio_b64(str(ruta))}"></audio>',
            height=48,
        )
    else:
        components.html(_html_voz_dispositivo(limpiar(texto)), height=48)


def narracion_de(t, p):
    """(clave de audio, texto) de la tarjeta. La clave lleva una huella del texto."""
    tipo = t.get("tipo")
    if tipo == "ficha":
        texto = texto_ficha(p)
        return con_hash(clave_ficha(p["nombre"]), texto), texto
    if tipo == "marcacion":
        texto = texto_marcacion(p.get("marcacion"))
        return con_hash(clave_marcacion(p.get("marcacion")), texto), texto
    if tipo == "horario":
        gs = grupos_de(p["nombre"]) if ss.get("sede") in SEDES_HORARIO_2026 else []
        return None, texto_horario(gs)
    if tipo == "comite":
        texto = texto_comite(t, COMITE)
    else:
        texto = texto_tarjeta(t)
    return con_hash(clave_generica(ss.bloque, ss.card_i), texto), texto


def vista_tarjetas():
    barra_bloque()
    tarjetas = tarjetas_de(ss.bloque)
    total = len(tarjetas)
    ss.card_i = min(ss.card_i, total - 1)
    t = tarjetas[ss.card_i]

    st.caption(f"Tarjeta {ss.card_i + 1} de {total}")
    with st.container(border=True):
        tipo = t.get("tipo")
        escuchar(*narracion_de(t, puesto_actual()))
        if tipo == "ficha":
            card_ficha()
        elif tipo == "organigrama":
            card_organigrama(t)
        elif tipo == "horario":
            card_horario()
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
        with st.expander("Detalle técnico (para Capital Humano)"):
            st.write(ss.get("envio_detalle", ""))
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
        st.caption("Configuración detectada (solo si existe; no se muestran los valores):")
        for nombre in ("CLAVE_ADMIN", "HOJA_URL", "HOJA_TOKEN", "FORM_ENLACE", "GEMINI_API_KEY"):
            st.caption(f"{'✅' if _secreto(nombre) else '❌'} {nombre}")
        clave = clave_admin()
        if not clave:
            st.caption("Define CLAVE_ADMIN en los Secrets para activar este panel.")
            return
        if st.text_input("Clave", type="password", key="clave_admin") != clave:
            return
        if st.button("🤖 Probar el asistente (Gemini)", key="probar_gemini"):
            if not asistente_activo():
                st.error("Falta GEMINI_API_KEY en los Secrets.")
            else:
                r = asistente.preguntar("¿Cuánto dura el periodo de prueba?", "Chofer de Reparto", "Chimbote", _base_conocimiento(),
                                        _secreto("GEMINI_API_KEY"), modelo=_secreto("GEMINI_MODELO") or None,
                                        url_base=_secreto("GEMINI_URL_BASE") or asistente.URL_GEMINI, tope_dia=10**6)
                (st.success if r["tipo"] == "ia" else st.error)(f"Modelo: {r.get('modelo', '-')} · {r['texto'][:220]} {r.get('detalle', '')}")
        if st.button("🔌 Probar conexión con la hoja", key="probar_hoja"):
            for ok, texto in probar_conexion(_secreto("HOJA_URL"), _secreto("HOJA_TOKEN"), _secreto("FORM_ENLACE")):
                (st.success if ok else st.error)(texto)
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
