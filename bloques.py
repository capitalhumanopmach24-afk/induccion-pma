# -*- coding: utf-8 -*-
"""
Los 7 bloques de la inducción. Reutiliza las tarjetas y preguntas de contenido_base.py
(texto tomado del PPT) y agrega lo nuevo. Para cambiar un texto o una pregunta, edita
contenido_base.py o las listas de este archivo.

Tipos especiales de tarjeta:
  "tipo": "marcacion"  -> texto distinto según el puesto (marca solo entrada o entrada y salida)
  "tipo": "ficha"      -> ficha interactiva del puesto elegido (bloque 6)
  "tipo": "comite"     -> fotos del Sub Comité de Hostigamiento Sexual
"""
from contenido_base import NIVELES

_T = {t["titulo"]: t for n in NIVELES for t in n["tarjetas"]}
_Q = {q["id"]: q for n in NIVELES for q in n["preguntas"]}


def T(titulo):
    return dict(_T[titulo])


def Q(*ids):
    return [dict(_Q[i]) for i in ids]


COMITE = [
    {"foto": "jackelin_cueva.jpg", "nombre": "Jackelin Cueva", "cargo": "Enfermera Ocupacional"},
    {"foto": "angel_del_junco.jpg", "nombre": "Angel Del Junco", "cargo": "Analista de Información"},
    {"foto": "selly_valverde.jpg", "nombre": "Selly Valverde", "cargo": "Asesor Universal"},
    {"foto": "paul_perez_torres.jpg", "nombre": "Paul Pérez Torres", "cargo": "Líder Comercial"},
]

BLOQUES = [
    # --------------------------------------------------------------- 1
    {
        "titulo": "Identidad y cultura corporativa",
        "icono": "🏭",
        "insignia": "Conocedor de PMA",
        "tarjetas": [
            T("Arca Continental Lindley"),
            T("¿Quiénes somos?"),
            T("Misión y visión"),
            T("Nuestros valores"),
            {
                "titulo": "Nuestro portafolio",
                "icono": "🥤",
                "puntos": ["Estos son los productos de The Coca-Cola Company que distribuimos."],
                "imagen": "slide_42.jpg",
            },
            T("Buenas prácticas: imagen personal"),
            T("Buenas prácticas: atención al cliente"),
        ],
        "preguntas": Q("N1-1", "N1-2", "N1-3", "N2-5")
        + [
            {
                "id": "B1-5",
                "texto": "¿Quién es el embotellador exclusivo de The Coca-Cola Company en el Perú?",
                "opciones": ["Distribuidora PMA", "Arca Continental Lindley", "Backus", "Gloria"],
                "correcta": 1,
                "explicacion": "Arca Continental Lindley es el embotellador exclusivo de The Coca-Cola Company en Perú. PMA es uno de sus socios estratégicos.",
            }
        ],
    },
    # --------------------------------------------------------------- 2
    {
        "titulo": "Procesos core",
        "icono": "⚙️",
        "insignia": "Experto en procesos",
        "tarjetas": [
            {**T("Proceso industrial"), "imagen": "slide_03.jpg"},
            T("Proceso comercial"),
        ],
        "preguntas": Q("N1-4", "N1-5")
        + [
            {
                "id": "B2-3",
                "texto": "¿Cuántas etapas tiene el proceso industrial, desde el abastecimiento hasta la distribución?",
                "opciones": ["4 etapas", "5 etapas", "6 etapas", "8 etapas"],
                "correcta": 2,
                "explicacion": "Son 6: abastecimiento, almacenamiento de insumos, preparación, envasado, almacenamiento y distribución.",
            },
            {
                "id": "B2-4",
                "texto": "La Distribución Primaria (T1) corresponde a la atención a…",
                "opciones": ["Mercado", "Distribuidor", "Clientes finales", "Proveedores"],
                "correcta": 1,
                "explicacion": "T1 es Atención a Distribuidor (distribución primaria) y T2 es Atención a Mercado (distribución secundaria).",
            },
        ],
    },
    # --------------------------------------------------------------- 3
    {
        "titulo": "Condiciones laborales y RIT",
        "icono": "📘",
        "insignia": "Puntual y profesional",
        "tarjetas": [
            T("Tipos de contrato"),
            T("Horario laboral 2026"),  # Corregido aquí
            {"tipo": "marcacion", "titulo": "Marcación de asistencia", "icono": "🖐️", "puntos": []},
            T("Reglamento Interno de Trabajo (RIT)"),
            T("Proceso sancionador"),
        ],
        # La pregunta sobre marcación se agrega según el puesto (ver app.py).
        "preguntas": Q("N3-1", "N3-2", "N2-1", "N2-2", "N2-3", "N5-1"),
    },
    # --------------------------------------------------------------- 4
    {
        "titulo": "Gestión de faltas y salud",
        "icono": "🤒",
        "insignia": "Salud primero",
        "tarjetas": [
            T("Si faltas, ¿qué debes hacer?"),
            T("¿Qué pasa cuando falto al trabajo por salud?"),
            {
                "titulo": "Si me atiendo en un centro médico particular",
                "icono": "🩺",
                "puntos": [
                    "Si te dieron Descanso Médico (DM): informa y envía la documentación al encargado de área y a Capital Humano. Presenta el DM particular, el recibo por honorarios al médico, los análisis o pruebas solicitadas, la receta y la boleta de compra de medicamentos. Tu falta se justifica SIN descuento.",
                    "Si fue solo atención (sin DM): informa y envía la documentación al encargado de área y a Capital Humano. Si retornas a laborar, se justifica como permiso SIN descuento. Si no retornas a laborar, se justifica como permiso pero SÍ hay descuento.",
                    "IMPORTANTE: si llegas a acumular 20 días de DM particular durante el año, deberás canjearlo al Seguro.",
                ],
            },
        ],
        "preguntas": Q("N5-2", "N5-3", "N5-4", "N5-5")
        + [
            {
                "id": "B4-5",
                "texto": "Si acumulas 20 días de descanso médico (DM) particular durante el año, ¿qué debes hacer?",
                "opciones": [
                    "Nada, no hay límite",
                    "Canjearlo al Seguro",
                    "Pedir vacaciones",
                    "Presentar una carta al jefe",
                ],
                "correcta": 1,
                "explicacion": "Si se llega a acumular 20 días de DM particular durante el año, deberá canjearse al Seguro.",
            },
            {
                "id": "B4-6",
                "texto": "Fuiste a una clínica y solo te atendieron (sin DM). Si NO regresas a laborar ese día, tu falta…",
                "opciones": [
                    "Se justifica como permiso, pero SÍ hay descuento",
                    "Se justifica sin descuento",
                    "Se considera abandono de trabajo",
                    "No se registra",
                ],
                "correcta": 0,
                "explicacion": "Con solo atención y sin retorno a laborar, se justifica como permiso pero sí hay descuento. Si retornas a laborar, es permiso sin descuento.",
            },
        ],
    },
    # --------------------------------------------------------------- 5
    {
        "titulo": "Remuneración y beneficios",
        "icono": "💵",
        "insignia": "Experto en beneficios",
        "tarjetas": [
            T("Adelanto quincenal"),
            T("Fin de mes"),
            T("¿Qué beneficios tienes por estar en planilla?"),
            T("Gratificación"),
            T("CTS"),
            T("Vacaciones"),
            T("Seguro Vida Ley"),
            T("Seguro gratuito EsSalud"),
            T("Licencias por maternidad y paternidad"),
        ],
        "preguntas": Q("N3-3", "N3-4", "N4-1", "N4-2", "N4-4", "N4-5", "N4-7"),
    },
    # --------------------------------------------------------------- 6 (según el puesto)
    {
        "titulo": "Tu puesto",
        "icono": "🧑‍🏭",
        "insignia": "Profesional de tu puesto",
        "tarjetas": [{"tipo": "ficha", "titulo": "Ficha de tu puesto", "icono": "🪪", "puntos": []}],
        "preguntas": [],  # examen generado desde el MOF (ver examen_puesto.py)
    },
    # --------------------------------------------------------------- 7
    {
        "titulo": "Ética y cumplimiento",
        "icono": "🤝",
        "insignia": "Respeto en acción",
        "tarjetas": [
            T("Política salarial"),
            T("Código de Ética y Conducta"),
            T("Hostigamiento sexual laboral"),
            {
                "tipo": "comite",
                "titulo": "Conoce al Sub Comité 2026-2028",
                "icono": "🛑",
                "puntos": [
                    "Ganadores de las elecciones del Comité de Hostigamiento Sexual Laboral, Chimbote 2026-2028.",
                    "Si vives o ves una situación de hostigamiento, estas son las personas a quienes puedes acudir.",
                ],
            },
        ],
        "preguntas": Q("N6-1", "N6-2", "N6-3")
        + [
            {
                "id": "B7-4",
                "texto": "¿Quién del Sub Comité de Hostigamiento Sexual es la Enfermera Ocupacional?",
                "opciones": ["Selly Valverde", "Jackelin Cueva", "Paul Pérez Torres", "Angel Del Junco"],
                "correcta": 1,
                "explicacion": "Jackelin Cueva es la Enfermera Ocupacional del Sub Comité.",
            },
            {
                "id": "B7-5",
                "texto": "¿Qué cargo tiene Paul Pérez Torres en el Sub Comité?",
                "opciones": ["Asesor Universal", "Analista de Información", "Líder Comercial", "Enfermero Ocupacional"],
                "correcta": 2,
                "explicacion": "Paul Pérez Torres es Líder Comercial. Selly Valverde es Asesor Universal y Angel Del Junco, Analista de Información.",
            },
        ],
    },
]
