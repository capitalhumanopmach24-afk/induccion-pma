# -*- coding: utf-8 -*-
"""
Los 7 bloques de la inducción. Reutiliza las tarjetas y preguntas de contenido_base.py
(texto tomado del PPT) y agrega lo nuevo. Para cambiar un texto o una pregunta, edita
contenido_base.py o las listas de este archivo.

Tipos especiales de tarjeta:
  "tipo": "organigrama" -> imagen del organigrama y línea de mando del puesto elegido
  "tipo": "horario"    -> tu horario real según el cuadro de horarios 2026 del puesto elegido
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
            {
                "tipo": "organigrama",
                "titulo": "Organigrama general",
                "icono": "🧭",
                "puntos": ["Así se organiza PMA. Ubica tu puesto y a quién reportas."],
                "imagen": "organigrama.jpg",
            },
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
            },
            {
                "id": "B1-6",
                "texto": "Según el organigrama general, ¿a quién reporta el Asesor Universal?",
                "opciones": ["Al Administrador", "Al Líder Comercial", "Al Monitor de Distribución", "Al Supervisor de Almacén"],
                "correcta": 1,
                "explicacion": "El Asesor Universal reporta al Líder Comercial, del área de Ventas.",
            },
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
            T("Horario laboral"),
            {"tipo": "horario", "titulo": "Tu horario", "icono": "🕘", "puntos": []},
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
                ],
            },
        ],
        "preguntas": Q("N5-2", "N5-3", "N5-4", "N5-5")
        + [
            {
                "id": "B4-5",
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
        "preguntas": Q("N6-1", "N6-2")
        + [
            {
                "id": "B7-4",
                "texto": "Tu jefe te niega permisos desde que rechazaste su invitación a salir. Según la inducción, esto…",
                "opciones": [
                    "Es una decisión normal de un jefe",
                    "Es un problema personal entre ustedes",
                    "Es una afectación en tus condiciones de trabajo y puede ser hostigamiento sexual",
                    "No tiene relación con el trabajo",
                ],
                "correcta": 2,
                "explicacion": "Negar permisos, licencias o vacaciones porque no te sometes es una afectación en las condiciones de trabajo que genera el hostigamiento sexual.",
            },
            {
                "id": "B7-5",
                "texto": "Un compañero te hace comentarios de contenido sexual y te incomodan. ¿Qué convierte esa conducta en hostigamiento sexual?",
                "opciones": [
                    "Que quien lo dice afirme que era una broma",
                    "Que no es deseada por la persona a la que se dirige",
                    "Que ocurra fuera del horario de trabajo",
                    "Que lo diga una persona de mayor cargo",
                ],
                "correcta": 1,
                "explicacion": "Es una conducta de naturaleza o connotación sexual o sexista NO deseada por la persona a la que se dirige. Es una forma de violencia.",
            },
            {
                "id": "B7-6",
                "texto": "Si dices «sí» porque temes perder tu trabajo, ¿hay consentimiento?",
                "opciones": [
                    "Sí, porque dijiste que sí",
                    "Sí, mientras no lo repitas",
                    "No, porque el consentimiento debe darse libremente",
                    "Depende de lo que decida el jefe",
                ],
                "correcta": 2,
                "explicacion": "El consentimiento debe ser dado libremente, reversible, entusiasta y específico. Un «sí» dado por miedo o presión no es consentimiento.",
            },
            {
                "id": "B7-7",
                "texto": "¿Cuál de estas es una afectación en la remuneración que puede generar el hostigamiento sexual?",
                "opciones": [
                    "Que te paguen en la fecha acordada",
                    "No acceder a un incremento o mejora remunerativa",
                    "Que te entreguen tu boleta de pago",
                    "Que recibas tu gratificación completa",
                ],
                "correcta": 1,
                "explicacion": "Entre las afectaciones están no acceder a un incremento o mejora remunerativa y no gozar de un complemento remunerativo (asignación, bonificación, gratificación, etc.).",
            },
        ],
    },
]
