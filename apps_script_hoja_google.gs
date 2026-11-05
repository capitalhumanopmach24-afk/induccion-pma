// Pega este código en Apps Script (Extensiones > Apps Script) de tu hoja de Google.
// Cambia la clave por una tuya y usa la MISMA en HOJA_TOKEN de la app.
const TOKEN = "cambia_esta_clave";

function doPost(e) {
  const d = JSON.parse(e.postData.contents);
  if (d.token !== TOKEN) return ContentService.createTextOutput("no autorizado");
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  d.envios.forEach(function (x) {
    const h = ss.getSheetByName(x.hoja) || ss.insertSheet(x.hoja);
    if (h.getLastRow() === 0) h.appendRow(x.encabezado);
    if (x.filas.length) {
      h.getRange(h.getLastRow() + 1, 1, x.filas.length, x.filas[0].length).setValues(x.filas);
    }
  });
  return ContentService.createTextOutput("ok");
}
