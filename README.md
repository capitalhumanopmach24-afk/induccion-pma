# Inducción PMA (versión juego, v2)

## A. Probarla en tu laptop (Windows)
1. Instala Python 3.10+ (marca "Add Python to PATH").
2. Extrae esta carpeta en un lugar PROPIO (por ejemplo D:\Induccion), nunca dentro de la carpeta del dashboard de Asistencia.
3. Doble clic en `iniciar_induccion.bat`. La primera vez instala todo; luego abre directo en http://localhost:8502
   (el dashboard de Asistencia sigue en el 8501, así que pueden correr a la vez).

## B. Ponerla en línea para todos (celulares)
Necesitas: una cuenta de Google, una de GitHub y una de Streamlit Community Cloud (gratis, se entra con GitHub).

### B1. Hoja de Google donde llegan los resultados
1. Crea una hoja de cálculo nueva en Google Drive (ej. "Resultados inducción").
2. Extensiones > Apps Script. Borra lo que haya y pega el contenido de `apps_script_hoja_google.gs`. Cambia `cambia_esta_clave` por una clave tuya.
3. Implementar > Nueva implementación > tipo "Aplicación web". Ejecutar como: **Yo**. Quién tiene acceso: **Cualquier persona**. Implementar y autorizar.
4. Copia la URL que termina en `/exec`.

### B2. Subir el código a GitHub
1. Crea un repositorio **privado** (contiene fotos del comité y datos internos) llamado, por ejemplo, `induccion-pma`.
2. Add file > Upload files: arrastra TODO el contenido de esta carpeta (app.py debe quedar en la raíz del repositorio).

### B3. Publicar en Streamlit Community Cloud
1. En share.streamlit.io: New app, elige el repositorio, rama main y archivo `app.py`.
2. Advanced settings > Secrets, pega (con tus valores):
       HOJA_URL = "https://script.google.com/macros/s/XXXX/exec"
       HOJA_TOKEN = "la_misma_clave_del_script"
       CLAVE_ADMIN = "otra_clave"
3. Deploy. Te da una dirección tipo https://tu-app.streamlit.app. Genera un QR con esa dirección y listo.

Cada trabajador la abre en su celular y sus resultados llegan a la hoja de Google (pestañas `resultados` y `respuestas`).

## Qué editar
- `contenido_base.py`: textos y preguntas del PPT.
- `bloques.py`: orden de los 7 bloques, tarjetas, preguntas nuevas y comité.
- `puestos.json`: los 39 puestos extraídos del MOF.
- `examen_puesto.py`: cómo se arma el examen de cada puesto.
- `assets/`: imágenes de diapositivas, fotos del comité y dibujos de puestos.

## Notas
- Si no configuras HOJA_URL, los resultados se guardan solo en `data/` (útil en tu laptop). En la nube esa carpeta no es permanente.
- Si la app se queda sin visitas muchas horas, la nube la duerme: la primera persona verá un botón para despertarla (tarda unos segundos).
