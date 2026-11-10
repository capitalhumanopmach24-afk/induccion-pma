# Inducción PMA (versión juego, v2)

## A. Probarla en tu laptop (Windows)
1. Instala Python 3.10+ (marca "Add Python to PATH").
2. Extrae esta carpeta en un lugar PROPIO (por ejemplo D:\Induccion), nunca dentro de la carpeta del dashboard de Asistencia.
3. Doble clic en `iniciar_induccion.bat` (abre en http://localhost:8502, así no choca con el dashboard de Asistencia en el 8501).

## B. Ponerla en línea (celulares)
Código en GitHub (repositorio privado) y publicación en Streamlit Community Cloud. Para actualizar: extrae el zip en una
carpeta limpia, en GitHub usa Add file > Upload files, arrastra TODO el contenido y Commit changes.

## C. Guardar los resultados en una hoja de cálculo
Elige UNA de las dos vías y pega el dato en Streamlit > tu app > Settings > Secrets.

### Vía 1 (recomendada): Google Forms
1. Crea un formulario de Google con 8 preguntas de «Respuesta corta», en este orden y con estos nombres:
   nombre, puesto, area, sede, puntos, porcentaje, examen_puesto, errores. Sin validaciones ni preguntas obligatorias.
2. Configuración > Respuestas: desactiva «Recopilar direcciones de correo» y «Limitar a 1 respuesta».
3. Menú ⋮ > «Obtener enlace prellenado». Escribe una «x» en las 8 preguntas, «Obtener enlace», «Copiar enlace».
4. Pestaña Respuestas > «Vincular a Hojas de cálculo»: ahí llegan los resultados.
5. En Secrets agrega:   FORM_ENLACE = "el_enlace_prellenado"

### Vía 2: Apps Script (guarda además cada respuesta en otra pestaña)
Pega `apps_script_hoja_google.gs` en Extensiones > Apps Script de tu hoja, impleméntalo como aplicación web
(Ejecutar como: Yo; Acceso: Cualquier persona) y en Secrets agrega:
   HOJA_URL = "la_url_que_termina_en_/exec"
   HOJA_TOKEN = "la_misma_clave_del_script"

### Para cualquiera de las dos
   CLAVE_ADMIN = "una_clave"
Luego abre la app, despliega la barra lateral > «Panel Capital Humano», escribe la clave y presiona
«Probar conexión con la hoja». Te dice si funcionó y, si no, qué revisar.

## D. Voz (gratis)
Cada tarjeta tiene un botón «🔊 Escuchar». Funciona en dos niveles:
1. **Audio natural pre-generado** (el mejor): se crea UNA vez con `generar_audios.py` en tu laptop, con voces neuronales en español
   (por defecto `es-PE-CamilaNeural`, acento peruano) y se guarda en `assets/audio`. La app solo reproduce los archivos:
   no depende de ningún servicio en línea ni tiene costo.
2. **Voz del celular o navegador**: si una tarjeta no tiene audio, la app la lee con la voz del dispositivo (gratis, sin internet).
Pasos (ventana negra dentro de esta carpeta):
   pip install -r requirements_audio.txt
   python generar_audios.py --listar    (voces en español disponibles)
   python generar_audios.py --comparar  (la misma frase con 4 voces en assets/audio, para que elijas la que te guste)
   python generar_audios.py --probar    (audio de prueba en assets/audio/_prueba.mp3; prueba otras voces con --voz)
   python generar_audios.py             (genera los que faltan; si falla por límites, repítelo más tarde: continúa donde quedó)
Luego sube todo (incluida assets/audio) a GitHub.
Nota: edge-tts usa el servicio de lectura en voz alta de Microsoft Edge, que NO es una API oficial. Por eso el script pide los audios
de uno en uno y con pausa, y por eso conviene generarlos una vez y guardarlos, en lugar de pedirlos en línea cada vez.
Si Microsoft limita tu conexión (error 403), espera o cambia de red (hotspot del celular).
Opción: `--motor gemini` usa la voz de Gemini (necesita tu clave: `set GEMINI_API_KEY=...` y `pip install -r requirements_audio_gemini.txt`).
Si cambias un texto, su audio anterior deja de usarse solo (el nombre del archivo lleva una huella del texto) y la tarjeta
vuelve a la voz del dispositivo hasta que vuelvas a ejecutar el generador. `--limpiar` borra los audios que ya no corresponden.

## E. Asistente «Pregúntale a PMA» (Gemini, plan gratuito)
Aparece en el mapa de bloques. Responde con el RIT 2026, el RISST 2026, la ficha del puesto y el cuadro de horarios (no usa el PPT, para no
contradecir al RIT aprobado). Cómo funciona: busca los fragmentos relacionados con la pregunta y solo esos se envían a Gemini, con la regla de
responder únicamente con ellos y citar la fuente.
Para activarlo, en Streamlit > tu app > Settings > Secrets agrega (la clave NUNCA va en el código ni en GitHub):
   GEMINI_API_KEY = "tu_clave"
Opcionales: GEMINI_MODELO = "nombre-del-modelo" (si no lo pones, elige solo el Flash-Lite más reciente que tu clave pueda usar) y
PREGUNTAS_POR_DIA = "300" (tope diario para cuidar la cuota gratuita).
Protecciones: máximo 8 preguntas por persona y 4 segundos de espera entre una y otra; se quitan números largos y correos antes de enviar; no se
envía el nombre del trabajador; los temas de hostigamiento, violencia o daño personal NO se envían a Gemini (se responde con un texto fijo que
orienta al canal correcto). En el «Panel Capital Humano» hay un botón para probar el asistente y ver qué modelo eligió.
Privacidad: en el plan gratuito de la API de Google, lo que se envía puede ser revisado por personas y usado para mejorar sus productos.
Por eso la pantalla avisa que no se escriban datos personales.
Si el RIT o el RISST cambian, envíalos para actualizar `conocimiento.json` (lo genera un script a partir de los documentos).

## Qué editar
- `puestos.json`: los 27 cargos activos de la base de datos de PMA, con su área y su ficha. Los que tienen `"provisional": true`
  muestran un aviso en pantalla; cuando valides una ficha, cámbialo a `false` y borra su `"nota"`.
- `horarios.json`: horarios 2026 de Chimbote y qué puesto usa cuál.
- `organigrama.json`: quién reporta a quién. Después de cambiarlo, `python generar_organigrama.py` redibuja la imagen (necesita matplotlib).
- `app.py`: al inicio están `SEDES`, `SEDES_HORARIO_2026` y `SEDES_COMITE`.
- `contenido_base.py` y `bloques.py`: textos, tarjetas y preguntas de los 7 bloques y datos del comité.
- `asistente.py` y `conocimiento.py`: el asistente; `conocimiento.json`: fragmentos del RIT, RISST, fichas y horarios.
- `examen_puesto.py`: cómo se arma el examen de cada puesto. `voz.py` y `generar_audios.py`: voz (textos de narración y generador de audios). `envio.py`: envío a Google.
- `assets/`: imágenes (diapositivas, organigrama, fotos del comité, dibujos de puestos) y `audio/`.

## Notas
- Si no configuras ninguna hoja, los resultados quedan solo en `data/` (en la nube esa carpeta no es permanente).
- Si la app se queda muchas horas sin visitas, la nube la duerme: la primera persona verá un botón para despertarla.
