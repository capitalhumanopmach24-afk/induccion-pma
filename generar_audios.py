# -*- coding: utf-8 -*-
"""
Genera los audios de la inducción (se ejecuta UNA vez, en tu laptop). Se guardan en assets/audio y la app los
reproduce sola; lo que no tenga audio se lee con la voz del celular. Una vez generados, la app no vuelve a
llamar a ningún servicio de voz: no hay costo ni dependencia en línea.

Motor por defecto: edge-tts (voces neuronales de Microsoft; gratis, sin clave ni tarjeta).
    pip install -r requirements_audio.txt
Motor opcional:    --motor gemini  (necesita tu clave: set GEMINI_API_KEY=... y pip install -r requirements_audio_gemini.txt)

Comandos (en la ventana negra, dentro de esta carpeta):
    python generar_audios.py --listar      muestra las voces en español disponibles
    python generar_audios.py --probar      genera un audio de prueba (assets/audio/_prueba.mp3)
    python generar_audios.py               genera los audios que faltan (puedes repetirlo: continúa donde quedó)

Opciones: --voz, --velocidad (edge, por ejemplo -5%), --pausa (segundos entre pedidos), --max (cuántos en esta corrida),
          --solo b2_ (solo los que empiecen así), --limpiar (borra audios que ya no corresponden al contenido).

Importante: edge-tts usa el servicio de lectura en voz alta de Microsoft Edge, que NO es una API oficial. Por eso este
script pide los audios de uno en uno y con pausa. Si Microsoft limita tu conexión (error 403), espera un rato o cambia
de red (por ejemplo, el hotspot del celular) y vuelve a ejecutarlo.
"""
import argparse
import asyncio
import io
import os
import re
import shutil
import subprocess
import sys
import time
import wave
from pathlib import Path

BASE = Path(__file__).parent
sys.path.insert(0, str(BASE))

from bloques import BLOQUES, COMITE  # noqa: E402
from examen_puesto import PUESTOS  # noqa: E402
import voz  # noqa: E402

VOZ_EDGE = "es-PE-CamilaNeural"
VELOCIDAD_EDGE = "-5%"
MODELO_GEMINI = "gemini-3.8-flash-lite-tts"
VOZ_GEMINI = "Kore"
ESTILO_GEMINI = ("Narra en español latinoamericano neutro, con voz cálida, clara y cercana, "
                 "a un ritmo pausado y natural, como un capacitador amable")


class LimiteTemporal(Exception):
    """El servicio limitó la conexión: hay que esperar o cambiar de red."""


class CuotaDiaria(LimiteTemporal):
    pass


def salir(msg):
    print("\n" + msg)
    sys.exit(1)


# ====================================================================== motor edge-tts
def _importar_edge():
    try:
        import edge_tts
    except ImportError:
        salir("Falta instalar edge-tts. Escribe:  pip install -r requirements_audio.txt")
    return edge_tts


def listar_edge():
    edge_tts = _importar_edge()
    voces = asyncio.run(edge_tts.list_voices())
    es = sorted((v for v in voces if v.get("Locale", "").lower().startswith("es-")), key=lambda v: (v["Locale"], v["ShortName"]))
    print("Voces en español disponibles:")
    for v in es:
        marca = "  <- acento peruano" if v["Locale"] == "es-PE" else ""
        print(f"   {v['ShortName'].ljust(26)} {v['Locale'].ljust(7)} {v.get('Gender', '')}{marca}")
    if not es:
        print("   (no se obtuvo ninguna; revisa tu conexión a internet)")


async def _edge_guardar(edge_tts, texto, voz_nombre, velocidad, destino):
    await asyncio.wait_for(edge_tts.Communicate(texto, voz_nombre, rate=velocidad).save(str(destino)), timeout=90)


def sintetizar_edge(texto, voz_nombre, velocidad, destino):
    """Genera un MP3 en `destino`. Reintenta con pausas; si Microsoft sigue respondiendo 403, levanta LimiteTemporal."""
    edge_tts = _importar_edge()
    tmp = destino.with_name(destino.name + ".tmp")
    ultimo = ""
    for intento in range(1, 4):
        try:
            asyncio.run(_edge_guardar(edge_tts, texto, voz_nombre, velocidad, tmp))
            if tmp.exists() and tmp.stat().st_size > 1000:
                os.replace(tmp, destino)
                return destino
            ultimo = "audio vacío"
        except Exception as e:  # noqa: BLE001
            ultimo = str(e)
        if tmp.exists():
            tmp.unlink()
        limitado = "403" in ultimo or "Invalid response status" in ultimo or "429" in ultimo
        if intento < 3:
            espera = (30 if limitado else 5) * intento
            print(f"   {'Microsoft limitó la conexión' if limitado else 'No se pudo generar'}; espero {espera} segundos y reintento…")
            time.sleep(espera)
    if "403" in ultimo or "Invalid response status" in ultimo or "429" in ultimo:
        raise LimiteTemporal(ultimo)
    raise RuntimeError(ultimo or "error desconocido")


# ====================================================================== motor Gemini (opcional)
def crear_cliente_gemini():
    clave = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not clave:
        salir("No encontré tu clave de Gemini. En esta ventana escribe primero:  set GEMINI_API_KEY=tu_clave")
    try:
        from google import genai
    except ImportError:
        salir("Falta instalar la librería de Google. Escribe:  pip install -r requirements_audio_gemini.txt")
    return genai.Client(api_key=clave)


def pedir_audio_gemini(client, modelo, voz_nombre, estilo, texto):
    if modelo.startswith("gemini-3.8"):
        contents = [{"role": "user", "parts": [{"text": texto, "speech_metadata": {"style": estilo}}]}]
        config = {"response_modalities": ["AUDIO"], "speech_config": {"voice_config": {"voice": voz_nombre}}}
    else:
        from google.genai import types
        contents = f"Di en español, con voz cálida, clara y pausada: {texto}"
        config = types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voz_nombre))),
        )
    r = client.models.generate_content(model=modelo, contents=contents, config=config)
    parte = r.candidates[0].content.parts[0]
    return parte.inline_data.data, (getattr(parte.inline_data, "mime_type", "") or "")


def _espera_sugerida(msg):
    m = re.search(r"retry in ([\d.]+)\s*s", msg, re.I) or re.search(r"retryDelay\W+(\d+)\s*s", msg, re.I)
    return int(float(m.group(1))) + 2 if m else None


def sintetizar_gemini(client, a, texto, destino):
    for intento in range(1, 5):
        try:
            data, mime = pedir_audio_gemini(client, a.modelo, a.voz, a.estilo, texto)
            break
        except Exception as e:  # noqa: BLE001
            msg = str(e)
            limite = "429" in msg or "RESOURCE_EXHAUSTED" in msg or "quota" in msg.lower()
            if limite and re.search(r"per ?day|daily|PerDay", msg, re.I):
                raise CuotaDiaria(msg)
            if limite and intento < 4:
                espera = _espera_sugerida(msg) or 60 * intento
                print(f"   Límite de solicitudes por minuto. Espero {espera} segundos…")
                time.sleep(espera)
                continue
            if any(x in msg for x in ("500", "503", "UNAVAILABLE", "INTERNAL")) and intento < 4:
                time.sleep(10 * intento)
                continue
            raise
    pcm, rate, canales = _a_pcm(data, mime)
    return _guardar_mp3(pcm, rate, canales, destino)


def _a_pcm(data, mime):
    if data[:4] == b"RIFF":
        with wave.open(io.BytesIO(data)) as w:
            return w.readframes(w.getnframes()), w.getframerate(), w.getnchannels()
    m = re.search(r"rate=(\d+)", mime or "")
    return data, int(m.group(1)) if m else 24000, 1


def _guardar_mp3(pcm, rate, canales, destino):
    try:
        import lameenc
        enc = lameenc.Encoder()
        enc.set_bit_rate(48 if canales == 1 else 96)
        enc.set_in_sample_rate(rate)
        enc.set_channels(canales)
        enc.set_quality(2)
        destino.write_bytes(enc.encode(pcm) + enc.flush())
        return destino
    except ImportError:
        pass
    if shutil.which("ffmpeg"):
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "s16le", "-ar", str(rate), "-ac", str(canales),
                        "-i", "-", "-b:a", "48k", str(destino)], input=pcm, check=True)
        return destino
    destino = destino.with_suffix(".wav")
    with wave.open(str(destino), "wb") as w:
        w.setnchannels(canales); w.setsampwidth(2); w.setframerate(rate); w.writeframes(pcm)
    print("   Aviso: no encontré lameenc ni ffmpeg; guardé WAV (pesa mucho). Instala lameenc: pip install lameenc")
    return destino


# ====================================================================== comandos
def sintetizar(a, client, texto, destino):
    if a.motor == "edge":
        return sintetizar_edge(texto, a.voz, a.velocidad, destino)
    return sintetizar_gemini(client, a, texto, destino)


def listar(a, client):
    if a.motor == "edge":
        listar_edge()
        return
    print("Modelos de voz disponibles para tu clave:")
    n = 0
    for m in client.models.list():
        nombre = getattr(m, "name", str(m))
        if "tts" in nombre.lower():
            print("  ", nombre.replace("models/", ""))
            n += 1
    if not n:
        print("   (ninguno con «tts» en el nombre; revisa tu clave en Google AI Studio)")


def probar(a, client):
    texto = ("Hola, te damos la bienvenida a Distribuidora PMA. En esta inducción conocerás la empresa, "
             "tus beneficios y las funciones de tu puesto.")
    print(f"Generando prueba con el motor {a.motor} y la voz {a.voz}…")
    voz.AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    try:
        print("Listo:", sintetizar(a, client, texto, voz.AUDIO_DIR / "_prueba.mp3"))
    except LimiteTemporal as e:
        salir(f"El servicio limitó tu conexión ({str(e)[:120]}). Espera un rato o cambia de red y vuelve a intentarlo.")
    print("Escúchalo. Si no te gusta la voz, prueba otra con --voz (usa --listar para ver las disponibles).")


def generar(a, client):
    voz.AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    todos = voz.elementos_audio(BLOQUES, PUESTOS, COMITE)
    elementos = [(c, t) for c, t in todos if c.startswith(a.solo)] if a.solo else todos
    if a.limpiar:
        vigentes = {c for c, _ in todos} | {"_prueba"}
        for f in voz.AUDIO_DIR.glob("*.*"):
            if f.stem not in vigentes:
                f.unlink()
                print("Borrado (ya no corresponde):", f.name)
    pendientes = [(c, t) for c, t in elementos if not voz.ruta_audio(c)]
    print(f"Audios en total: {len(elementos)} | ya generados: {len(elementos) - len(pendientes)} | pendientes: {len(pendientes)}")
    hechos = 0
    for k, (clave, texto) in enumerate(pendientes, 1):
        if a.max and hechos >= a.max:
            break
        print(f"[{k}/{len(pendientes)}] {clave} ({len(texto)} caracteres)")
        try:
            sintetizar(a, client, texto, voz.AUDIO_DIR / f"{clave}.mp3")
        except CuotaDiaria:
            print("\nSe alcanzó el límite diario de tu cuenta. Vuelve a ejecutar este comando mañana: continúa donde quedó.")
            break
        except LimiteTemporal as e:
            print(f"\nEl servicio limitó tu conexión ({str(e)[:100]}).")
            print("Espera entre 30 y 60 minutos, o cambia de red (por ejemplo, el hotspot del celular), y vuelve a ejecutar: continúa donde quedó.")
            break
        except Exception as e:  # noqa: BLE001
            print(f"   No se pudo generar este audio: {str(e)[:200]}")
            continue
        hechos += 1
        if a.pausa:
            time.sleep(a.pausa)
    faltan = len(pendientes) - hechos
    print(f"\nGenerados en esta corrida: {hechos}. Faltan: {faltan}.")
    if not faltan:
        print("Todo listo. Sube la carpeta assets/audio a tu repositorio de GitHub junto con el resto de la app.")


def main():
    ap = argparse.ArgumentParser(description="Genera los audios de la inducción.")
    ap.add_argument("--motor", choices=["edge", "gemini"], default="edge")
    ap.add_argument("--listar", action="store_true")
    ap.add_argument("--probar", action="store_true")
    ap.add_argument("--limpiar", action="store_true")
    ap.add_argument("--voz", default=None)
    ap.add_argument("--velocidad", default=VELOCIDAD_EDGE, help="solo edge, por ejemplo -5%% o +10%%")
    ap.add_argument("--modelo", default=MODELO_GEMINI, help="solo gemini")
    ap.add_argument("--estilo", default=ESTILO_GEMINI, help="solo gemini")
    ap.add_argument("--pausa", type=float, default=None)
    ap.add_argument("--max", type=int, default=0)
    ap.add_argument("--solo", default="")
    a = ap.parse_args()
    if a.voz is None:
        a.voz = VOZ_EDGE if a.motor == "edge" else VOZ_GEMINI
    if a.pausa is None:
        a.pausa = 5.0 if a.motor == "edge" else 6.0
    client = crear_cliente_gemini() if a.motor == "gemini" else None
    if a.listar:
        listar(a, client)
    elif a.probar:
        probar(a, client)
    else:
        generar(a, client)


if __name__ == "__main__":
    main()
