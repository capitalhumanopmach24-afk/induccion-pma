# -*- coding: utf-8 -*-
"""
Envío de resultados a una hoja de cálculo de Google. Dos vías (se usa la que esté configurada):

  1) Google Forms  (FORM_ENLACE)  -> la más simple: no hay scripts ni permisos que configurar.
  2) Apps Script   (HOJA_URL + HOJA_TOKEN) -> guarda también cada respuesta en una pestaña aparte.

Cada función devuelve (ok, mensaje). Si algo falla, el mensaje explica qué revisar.
No depende de Streamlit, así que se puede probar por separado.
"""
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime

# Orden de las 8 preguntas "Respuesta corta" que debe tener el formulario de Google.
CAMPOS_FORM = ["nombre", "puesto", "area", "sede", "puntos", "porcentaje", "examen_puesto", "errores"]


def _post(url, cuerpo, content_type, timeout=25):
    """POST sencillo. Devuelve (estado_http, texto, error, url_final). estado 0 = sin conexión."""
    req = urllib.request.Request(
        url, data=cuerpo, headers={"Content-Type": content_type, "User-Agent": "Mozilla/5.0 (induccion-pma)"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "ignore"), "", r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "ignore")[:600], f"HTTP {e.code}", url
    except Exception as e:  # sin internet, tiempo agotado, dirección mal escrita...
        return 0, "", f"{type(e).__name__}: {e}", url


def _pide_login(url_final, texto):
    t = texto.lower()
    return "accounts.google.com" in url_final or "servicelogin" in t or "iniciar sesión" in t[:3000]


# ------------------------------------------------------------------ Apps Script
def enviar_apps_script(url, token, envios):
    cuerpo = json.dumps({"token": token, "envios": envios}).encode("utf-8")
    estado, texto, err, final = _post(url, cuerpo, "text/plain; charset=utf-8")
    t = texto.strip().lower()
    if estado == 0:
        return False, f"No hubo conexión con la hoja ({err})."
    if t.startswith("ok"):
        return True, "ok"
    if "no autorizado" in t:
        return False, "La clave HOJA_TOKEN no es igual a la clave TOKEN escrita dentro del script de Google."
    if _pide_login(final, texto):
        return False, ("El script pide iniciar sesión. En Apps Script: Implementar > Administrar implementaciones > "
                       "editar, y en «Quién tiene acceso» elige «Cualquier persona».")
    if estado == 404 or "no se puede abrir el archivo" in t:
        return False, "La dirección HOJA_URL no existe o la implementación fue eliminada. Copia otra vez la URL que termina en /exec."
    if estado in (401, 403):
        return False, "Google rechazó el acceso al script. Revisa «Ejecutar como: Yo», «Quién tiene acceso: Cualquier persona» y vuelve a autorizar."
    return False, f"Respuesta inesperada del script (HTTP {estado}): {texto.strip()[:150]!r}"


# ------------------------------------------------------------------ Google Forms
def parsear_enlace_form(enlace):
    """Del «enlace prellenado» saca la dirección de envío y los códigos de las preguntas."""
    enlace = (enlace or "").strip().strip('"').strip("'")
    if "forms.gle" in enlace:
        return None, [], "Pegaste el enlace corto (forms.gle). Necesitas el «enlace prellenado», que contiene /viewform?usp=pp_url&entry.…"
    m = re.match(r"(https?://[^?#]*?)/(viewform|formResponse)", enlace)
    if not m:
        return None, [], "FORM_ENLACE no parece un enlace de Google Forms (debe contener /viewform?usp=pp_url&entry.…)."
    consulta = urllib.parse.urlparse(enlace).query
    ids = []
    for k, _ in urllib.parse.parse_qsl(consulta, keep_blank_values=True):
        if k.startswith("entry.") and not k.endswith("_sentinel") and k not in ids:
            ids.append(k)
    if len(ids) != len(CAMPOS_FORM):
        return None, ids, (f"El enlace trae {len(ids)} preguntas y se esperaban {len(CAMPOS_FORM)}. "
                           "Rellena las 8 preguntas (con una «x») antes de copiar el enlace prellenado.")
    return m.group(1) + "/formResponse", ids, ""


def enviar_formulario(enlace, valores):
    url, ids, err = parsear_enlace_form(enlace)
    if err:
        return False, err
    datos = urllib.parse.urlencode(dict(zip(ids, valores))).encode("utf-8")
    estado, texto, e, final = _post(url, datos, "application/x-www-form-urlencoded")
    t = texto.lower()
    if estado == 0:
        return False, f"No hubo conexión con Google ({e})."
    if estado in (401, 403) or _pide_login(final, texto):
        return False, ("El formulario pide iniciar sesión. En el formulario: Configuración > Respuestas, desactiva "
                       "«Limitar a 1 respuesta» y «Recopilar direcciones de correo electrónico».")
    if estado == 404:
        return False, "No se encontró el formulario. Revisa que FORM_ENLACE sea el enlace prellenado correcto."
    if "ya no acepta" in t or "ya no se aceptan" in t or "no longer accepting" in t:
        return False, "El formulario no está aceptando respuestas. En la pestaña Respuestas activa «Aceptar respuestas»."
    if estado == 400:
        return False, ("Google rechazó los datos (HTTP 400). Revisa que las 8 preguntas sean «Respuesta corta», "
                       "sin validaciones y que no haya preguntas obligatorias extra.")
    if 200 <= estado < 300:
        return True, "ok"
    return False, f"Respuesta inesperada de Google (HTTP {estado})."


# ------------------------------------------------------------------ prueba de conexión
def probar_conexion(url, token, enlace):
    """Envía una fila de prueba por cada vía configurada. Devuelve lista de (ok, texto)."""
    out = []
    if url:
        ahora = datetime.now().isoformat(timespec="seconds")
        ok, msg = enviar_apps_script(url, token, [
            {"hoja": "prueba", "encabezado": ["fecha", "mensaje"], "filas": [[ahora, "Prueba de conexión desde la app"]]}
        ])
        out.append((ok, "Apps Script: " + ("conexión correcta (revisa la pestaña «prueba» de tu hoja)." if ok else msg)))
    if enlace:
        ok, msg = enviar_formulario(enlace, ["PRUEBA DE CONEXIÓN", "-", "-", "-", "0", "0", "0", "prueba"])
        out.append((ok, "Google Forms: " + ("conexión correcta (revisa la hoja de respuestas del formulario)." if ok else msg)))
    if not out:
        out.append((False, "No hay ninguna hoja configurada: faltan FORM_ENLACE o HOJA_URL en los Secrets de Streamlit."))
    return out
