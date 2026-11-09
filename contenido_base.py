# -*- coding: utf-8 -*-
"""
Contenido de la inducción general de Capital Humano - Distribuidora PMA E.I.R.L.
Todo el texto proviene del PPT "PROCESO DE INDUCCIÓN GENERAL - CAPITAL HUMANO".
Para cambiar una pregunta, un monto o una fecha, edita solo este archivo.

Estructura:
  NIVELES: lista de niveles. Cada nivel tiene tarjetas (contenido) y preguntas.
  Una tarjeta puede llevar una imagen de las diapositivas (carpeta assets/slides).
  En cada pregunta, "correcta" es la posición (0, 1, 2...) de la opción correcta.
"""

NIVELES = [
    # ------------------------------------------------------------------ NIVEL 1
    {
        "titulo": "Conoce PMA",
        "icono": "🏭",
        "insignia": "Conocedor de PMA",
        "tarjetas": [
            {
                "titulo": "Arca Continental Lindley",
                "icono": "🥤",
                "puntos": [
                    "Embotellador exclusivo de The Coca-Cola Company en Perú.",
                    "Parte del Grupo Arca Continental, el tercer embotellador más importante del sistema Coca-Cola a nivel mundial.",
                ],
                "imagen": "slide_02.jpg",
            },
            {
                "titulo": "¿Quiénes somos?",
                "icono": "🏢",
                "puntos": [
                    "Distribuidora PMA E.I.R.L. es uno de los Socios Estratégicos de Arca Continental Lindley.",
                    "Fue creada el 01 de marzo del año 2001 en la ciudad de Chiclayo.",
                    "El 10 de mayo del 2004 fue trasladada a la ciudad de Trujillo.",
                    "El nombre deriva de las iniciales de los hijos del dueño, Sr. Adolfo Castillo Acuña.",
                ],
            },
            {
                "titulo": "Misión y visión",
                "icono": "🎯",
                "puntos": [
                    "Misión: distribuir y vender bebidas gaseosas en canales mayoristas y minoristas, con buena atención al cliente y calidad hasta la entrega, bajo políticas de liderazgo y mejoramiento continuo.",
                    "Visión: ser la empresa distribuidora de bebidas gaseosas líder a nivel nacional, reconocida por su servicio oportuno y eficiente.",
                ],
            },
            {
                "titulo": "Nuestros valores",
                "icono": "❤️",
                "puntos": [
                    "Honradez · Compromiso · Lealtad",
                    "Trabajo en equipo · Eficiencia · Orientación al servicio",
                ],
                "imagen": "slide_08.jpg",
            },
            {
                "titulo": "Proceso industrial",
                "icono": "⚙️",
                "puntos": [
                    "Abastecimiento: recaudar los insumos necesarios.",
                    "Almacenamiento de insumos: guardarlos para su posterior preparación.",
                    "Preparación: mezclar cuidadosamente los insumos.",
                    "Envasado: se vierte el preparado en botellas de plástico o de vidrio.",
                    "Almacenamiento: se reúnen las botellas en cajas para ser distribuidas.",
                    "Distribución: expedición de los productos al mercado, primaria o secundaria.",
                ],
            },
            {
                "titulo": "Proceso comercial",
                "icono": "🚚",
                "puntos": [
                    "Tenemos dos canales comerciales.",
                    "Atención a Distribuidor: Distribución Primaria (T1).",
                    "Atención a Mercado: Distribución Secundaria (T2).",
                ],
                "imagen": "slide_04.jpg",
            },
        ],
        "preguntas": [
            {
                "id": "N1-1",
                "texto": "¿En qué año y ciudad fue creada Distribuidora PMA?",
                "opciones": ["2004, Trujillo", "2001, Chiclayo", "2001, Trujillo", "2004, Chiclayo"],
                "correcta": 1,
                "explicacion": "PMA fue creada el 01 de marzo del 2001 en Chiclayo. En el 2004 se trasladó a Trujillo.",
            },
            {
                "id": "N1-2",
                "texto": "¿De dónde deriva el nombre PMA?",
                "opciones": [
                    "De las iniciales de los hijos del dueño",
                    "De una marca de gaseosas",
                    "De la ciudad donde nació",
                    "De las iniciales de Arca Continental",
                ],
                "correcta": 0,
                "explicacion": "El nombre deriva de las iniciales de los hijos del dueño, Sr. Adolfo Castillo Acuña.",
            },
            {
                "id": "N1-3",
                "texto": "¿Cuál de estos NO es uno de los valores de PMA?",
                "opciones": ["Honradez", "Lealtad", "Puntualidad", "Trabajo en equipo"],
                "correcta": 2,
                "explicacion": "Los valores son: Honradez, Compromiso, Lealtad, Trabajo en equipo, Eficiencia y Orientación al servicio.",
            },
            {
                "id": "N1-4",
                "texto": "La Distribución Secundaria (T2) corresponde a la atención a…",
                "opciones": ["Distribuidor", "Mercado", "Proveedores", "Embotelladoras"],
                "correcta": 1,
                "explicacion": "T1 es Atención a Distribuidor (primaria) y T2 es Atención a Mercado (secundaria).",
            },
            {
                "id": "N1-5",
                "texto": "¿En qué etapa del proceso industrial se vierte el preparado en las botellas?",
                "opciones": ["Preparación", "Abastecimiento", "Envasado", "Distribución"],
                "correcta": 2,
                "explicacion": "En el envasado se vierte el preparado en botellas de plástico o de vidrio.",
            },
        ],
    },
    # ------------------------------------------------------------------ NIVEL 2
    {
        "titulo": "Tu día a día",
        "icono": "⏰",
        "insignia": "Puntual y profesional",
        "tarjetas": [
            {
                "titulo": "Buenas prácticas: imagen personal",
                "icono": "🦺",
                "puntos": [
                    "Adecuado uso del uniforme y EPPs (en caso aplique).",
                    "Higiene personal y limpieza de la vestimenta.",
                    "Orden en nuestros documentos y herramientas de trabajo.",
                    "Evitar los malos hábitos (escupir, arrojar basura, morderse las uñas, etc.).",
                    "Respetar las marcas que se representan (no consumir otras marcas).",
                    "Cuidar del mobiliario en el PDV.",
                ],
            },
            {
                "titulo": "Buenas prácticas: atención al cliente",
                "icono": "🤝",
                "puntos": [
                    "Escuchar, escuchar y escuchar.",
                    "Muestra interés en resolver el problema.",
                    "Ejecuta la comunicación con los responsables.",
                    "Muestra seguridad y dominio.",
                    "Recuerda los nombres de tus clientes.",
                    "Da seguimiento al problema y encuentra una solución.",
                ],
            },
            {
                "titulo": "Horario laboral",
                "icono": "🕗",
                "puntos": [
                    "La puntualidad es uno de los principales indicadores de evaluación.",
                    "El tiempo de tolerancia solo aplica en situaciones excepcionales y debidamente justificadas.",
                    "La impuntualidad reiterada es motivo de separación del equipo de trabajo.",
                    "Si marcas tu salida, la puntualidad rige tanto para el inicio como para el fin de la jornada.",
                    "Los horarios se entregan de acuerdo al puesto de trabajo.",
                ],
            },
            {
                "titulo": "Marcación de asistencia",
                "icono": "🖐️",
                "puntos": [
                    "Debes registrar tu ingreso y salida del centro de trabajo. Si no registras tu asistencia se considera una falta pasible de descuento.",
                    "La marcación es personal: marcar, modificar o suplantar a otro trabajador es una falta grave.",
                    "Si hay algún problema con la marcación, avisa de inmediato a Recursos Humanos, en un plazo de 24 horas.",
                    "El personal de Ventas y Distribución no está sujeto a fiscalización horaria.",
                ],
            },
        ],
        "preguntas": [
            {
                "id": "N2-1",
                "texto": "El tiempo de tolerancia en el horario aplica…",
                "opciones": [
                    "Todos los días",
                    "Solo en situaciones excepcionales y justificadas",
                    "Solo los lunes",
                    "Cuando mi supervisor no está",
                ],
                "correcta": 1,
                "explicacion": "La tolerancia solo aplica en situaciones excepcionales y debidamente justificadas.",
            },
            {
                "id": "N2-2",
                "texto": "Un compañero llegó tarde y te pide que marques por él. ¿Qué pasa si lo haces?",
                "opciones": [
                    "Nada, es un favor",
                    "Es una falta grave",
                    "Solo recibes una advertencia verbal",
                    "Se descuenta una hora",
                ],
                "correcta": 1,
                "explicacion": "La marcación es personal. Marcar, modificar o suplantar a otro trabajador es una falta grave.",
            },
            {
                "id": "N2-3",
                "texto": "Si tienes un problema con tu marcación, ¿en qué plazo debes avisar a Recursos Humanos?",
                "opciones": ["24 horas", "48 horas", "Una semana", "Fin de mes"],
                "correcta": 0,
                "explicacion": "Debes avisar inmediatamente a Recursos Humanos, en un plazo de 24 horas.",
            },
            {
                "id": "N2-4",
                "texto": "¿Quiénes NO están sujetos a fiscalización horaria?",
                "opciones": ["Almacén", "Ventas y Distribución", "Administrativos", "Seguridad"],
                "correcta": 1,
                "explicacion": "El personal de Ventas y Distribución no está sujeto a fiscalización horaria.",
            },
            {
                "id": "N2-5",
                "texto": "Sobre las marcas que representamos, ¿cuál es la buena práctica?",
                "opciones": [
                    "Consumir cualquier marca en el PDV",
                    "Respetar las marcas que se representan y no consumir otras",
                    "Probar la competencia",
                    "Recomendar otras marcas",
                ],
                "correcta": 1,
                "explicacion": "Se debe respetar las marcas que se representan (no consumir otras marcas).",
            },
        ],
    },
    # ------------------------------------------------------------------ NIVEL 3
    {
        "titulo": "Contrato y pagos",
        "icono": "💵",
        "insignia": "Cuentas claras",
        "tarjetas": [
            {
                "titulo": "Tipos de contrato",
                "icono": "📄",
                "puntos": [
                    "Contrato de tiempo indefinido.",
                    "Contrato de tiempo definido.",
                    "Luego de superar los 3 meses de periodo de prueba, se inicia el periodo de renovación de contrato.",
                    "Luego de cumplir 3 años de renovación de contrato de tiempo definido, tu vinculación con la empresa se da de manera automática (tiempo indefinido).",
                ],
            },
            {
                "titulo": "Adelanto quincenal",
                "icono": "1️⃣5️⃣",
                "puntos": [
                    "Se paga el 40% de tu básico y la Asignación Familiar (si corresponde).",
                    "Se descuenta el porcentaje general del fondo pensionario.",
                ],
            },
            {
                "titulo": "Fin de mes",
                "icono": "3️⃣0️⃣",
                "puntos": [
                    "Se paga el 60% de tu básico.",
                    "Se suma la remuneración adicional (comisiones, pasajes, etc.).",
                    "Se regularizan los descuentos pendientes (si corresponde).",
                ],
            },
        ],
        "preguntas": [
            {
                "id": "N3-1",
                "texto": "¿Cuánto dura el periodo de prueba?",
                "opciones": ["1 mes", "3 meses", "6 meses", "1 año"],
                "correcta": 1,
                "explicacion": "Luego de superar los 3 meses de periodo de prueba se inicia el periodo de renovación de contrato.",
            },
            {
                "id": "N3-2",
                "texto": "Después de 3 años de renovación de contrato de tiempo definido, tu vinculación con la empresa…",
                "opciones": [
                    "Termina automáticamente",
                    "Se da de manera automática",
                    "Vuelve al periodo de prueba",
                    "Depende del supervisor",
                ],
                "correcta": 1,
                "explicacion": "Tras 3 años de renovación, la vinculación se da de manera automática.",
            },
            {
                "id": "N3-3",
                "texto": "¿Qué porcentaje del básico se paga en el adelanto quincenal?",
                "opciones": ["60%", "50%", "40%", "30%"],
                "correcta": 2,
                "explicacion": "En el adelanto quincenal se paga el 40% del básico y la Asignación Familiar (si corresponde).",
            },
            {
                "id": "N3-4",
                "texto": "En el pago de fin de mes se paga el 60% del básico, más…",
                "opciones": [
                    "La CTS",
                    "La remuneración adicional (comisiones, pasajes, etc.)",
                    "Las vacaciones",
                    "La gratificación",
                ],
                "correcta": 1,
                "explicacion": "A fin de mes se paga el 60% del básico más la remuneración adicional, y se regularizan los descuentos pendientes.",
            },
        ],
    },
    # ------------------------------------------------------------------ NIVEL 4
    {
        "titulo": "Tus beneficios",
        "icono": "🎁",
        "insignia": "Experto en beneficios",
        "tarjetas": [
            {
                "titulo": "¿Qué beneficios tienes por estar en planilla?",
                "icono": "📋",
                "puntos": ["Mira el resumen de tus beneficios."],
                "imagen": "slide_16.jpg",
            },
            {
                "titulo": "Gratificación",
                "icono": "💰",
                "puntos": [
                    "Equivale a 1 sueldo: haber básico, variable, asignación familiar, horas extras u otros conceptos definidos por ley.",
                    "Se paga en la quincena de julio y en la quincena de diciembre.",
                ],
            },
            {
                "titulo": "CTS",
                "icono": "🐷",
                "puntos": [
                    "Se paga cada 6 meses, en la quincena de mayo y en la quincena de noviembre.",
                    "Equivale a 1/2 sueldo e incluye el promedio de tus variables.",
                ],
            },
            {
                "titulo": "Vacaciones",
                "icono": "🏖️",
                "puntos": [
                    "Derecho ganado de 30 días de vacaciones por 1 año de trabajo continuo.",
                    "Es un monto de dinero pagado durante el goce del periodo vacacional.",
                ],
            },
            {
                "titulo": "Seguro gratuito EsSalud",
                "icono": "🏥",
                "puntos": [
                    "Puedes tramitar la inscripción de tu hijo menor de edad, de tu cónyuge o de tu concubina(o).",
                    "Solicita los formularios a la Trabajadora Social.",
                ],
            },
            {
                "titulo": "Seguro Vida Ley",
                "icono": "🛡️",
                "puntos": [
                    "Según el Decreto Legislativo 688, todo trabajador empleado y obrero tiene derecho a un seguro de vida a cargo de su empleador.",
                    "Muerte natural: 16 sueldos.",
                    "Beneficio por muerte accidental: 32 sueldos.",
                    "Invalidez total y permanente por accidente: 32 sueldos.",
                ],
            },
            {
                "titulo": "Licencias por maternidad y paternidad",
                "icono": "👶",
                "puntos": [
                    "La trabajadora gestante goza de 49 días de descanso prenatal y 49 días de descanso postnatal.",
                    "El padre trabajador goza de 10 días hábiles consecutivos.",
                ],
            },
        ],
        "preguntas": [
            {
                "id": "N4-1",
                "texto": "¿En qué meses se paga la gratificación?",
                "opciones": ["Mayo y noviembre", "Julio y diciembre", "Marzo y septiembre", "Enero y junio"],
                "correcta": 1,
                "explicacion": "La gratificación se paga en la quincena de julio y en la de diciembre. Equivale a 1 sueldo.",
            },
            {
                "id": "N4-2",
                "texto": "¿En qué meses se paga la CTS?",
                "opciones": ["Julio y diciembre", "Mayo y noviembre", "Abril y octubre", "Febrero y agosto"],
                "correcta": 1,
                "explicacion": "La CTS se paga cada 6 meses, en la quincena de mayo y noviembre.",
            },
            {
                "id": "N4-3",
                "texto": "La CTS equivale a…",
                "opciones": ["1 sueldo", "1/2 sueldo", "2 sueldos", "1/4 de sueldo"],
                "correcta": 1,
                "explicacion": "La CTS equivale a 1/2 sueldo e incluye el promedio de tus variables.",
            },
            {
                "id": "N4-4",
                "texto": "¿Cuántos días de vacaciones ganas por 1 año de trabajo continuo?",
                "opciones": ["15 días", "20 días", "30 días", "45 días"],
                "correcta": 2,
                "explicacion": "Tienes derecho ganado a 30 días de vacaciones por 1 año de trabajo continuo.",
            },
            {
                "id": "N4-5",
                "texto": "¿Cuántos sueldos cubre el Seguro Vida Ley por muerte accidental?",
                "opciones": ["16 sueldos", "24 sueldos", "32 sueldos", "12 sueldos"],
                "correcta": 2,
                "explicacion": "Por muerte natural son 16 sueldos y por muerte accidental, 32 sueldos.",
            },
            {
                "id": "N4-6",
                "texto": "Quieres inscribir a tu cónyuge en EsSalud. ¿A quién le pides los formularios?",
                "opciones": ["Al chofer", "A la Trabajadora Social", "Al cliente", "Al jefe de almacén"],
                "correcta": 1,
                "explicacion": "Los formularios se solicitan a la Trabajadora Social.",
            },
            {
                "id": "N4-7",
                "texto": "¿Cuántos días hábiles consecutivos de licencia tiene el padre trabajador?",
                "opciones": ["3 días", "5 días", "10 días", "15 días"],
                "correcta": 2,
                "explicacion": "El padre trabajador goza de 10 días hábiles consecutivos.",
            },
        ],
    },
    # ------------------------------------------------------------------ NIVEL 5
    {
        "titulo": "Reglas del juego",
        "icono": "⚖️",
        "insignia": "Cumplidor de reglas",
        "tarjetas": [
            {
                "titulo": "Reglamento Interno de Trabajo (RIT)",
                "icono": "📘",
                "puntos": [
                    "Es una norma elaborada por la empresa donde se determinan las condiciones a las que deben sujetarse todos los trabajadores.",
                    "Está sujeto a las normas laborales vigentes (TUO del Decreto Legislativo 728, regulado por el D.S. 003-97/TR).",
                ],
            },
            {
                "titulo": "Proceso sancionador",
                "icono": "🚦",
                "puntos": [
                    "Artículo 71° del Reglamento Interno de Trabajo (RIT 2026): la Distribuidora establece cuatro tipos de medidas disciplinarias.",
                    "1. Amonestación verbal.",
                    "2. Amonestación escrita.",
                    "3. Suspensión de labores sin goce de haber.",
                    "4. Despido por falta grave.",
                ],
            },
            {
                "titulo": "Si faltas, ¿qué debes hacer?",
                "icono": "🤒",
                "puntos": [
                    "Si es por enfermedad, comunícate con tu supervisor y/o Asistente de Capital Humano.",
                    "Entrega el Descanso Médico original, a más tardar al 2.º día de tu incorporación al trabajo. Solo así tus faltas se consideran justificadas.",
                    "Después de 3 días de inasistencias injustificadas se considera abandono de trabajo y la empresa procede al cese efectivo del colaborador.",
                    "Las faltas injustificadas reducen los días contables de beneficios sociales como Gratificación y CTS.",
                ],
            },
            {
                "titulo": "¿Qué pasa cuando falto al trabajo por salud?",
                "icono": "🗺️",
                "puntos": ["Revisa los dos flujogramas: atención en EsSalud o en un centro médico particular."],
                "imagen": "slide_19.jpg",
                "imagen2": "slide_20.jpg",
            },
        ],
        "preguntas": [
            {
                "id": "N5-1",
                "texto": "¿Cuál de estas NO es una de las cuatro sanciones del artículo 71° del RIT?",
                "opciones": [
                    "Amonestación verbal",
                    "Descuento del 50% del sueldo",
                    "Suspensión de labores sin goce de haber",
                    "Despido por falta grave",
                ],
                "correcta": 1,
                "explicacion": "Las sanciones son: amonestación verbal, amonestación escrita, suspensión sin goce de haber y despido por falta grave.",
            },
            {
                "id": "N5-2",
                "texto": "Amaneciste con fiebre y no puedes ir a trabajar. ¿Qué haces primero?",
                "opciones": [
                    "Nada, ya avisaré cuando regrese",
                    "Comunicarme con mi supervisor y/o el Asistente de Capital Humano",
                    "Pedirle a un compañero que marque por mí",
                    "Esperar a que me llamen",
                ],
                "correcta": 1,
                "explicacion": "Debes comunicarte con tu supervisor y/o el Asistente de Capital Humano.",
            },
            {
                "id": "N5-3",
                "texto": "¿Hasta cuándo debes entregar el Descanso Médico original para que tus faltas sean justificadas?",
                "opciones": [
                    "Hasta fin de mes",
                    "A más tardar al 2.º día de tu incorporación",
                    "A los 15 días",
                    "No es necesario entregarlo",
                ],
                "correcta": 1,
                "explicacion": "El Descanso Médico original se entrega a más tardar al 2.º día de tu incorporación al trabajo.",
            },
            {
                "id": "N5-4",
                "texto": "¿Después de cuántos días de inasistencias injustificadas se considera abandono de trabajo?",
                "opciones": ["1 día", "2 días", "3 días", "10 días"],
                "correcta": 2,
                "explicacion": "Después de 3 días de inasistencias injustificadas se considera abandono de trabajo.",
            },
            {
                "id": "N5-5",
                "texto": "Las faltas injustificadas reducen los días contables de…",
                "opciones": [
                    "Tu uniforme y EPPs",
                    "Gratificación y CTS",
                    "Tu horario",
                    "Tu marcación",
                ],
                "correcta": 1,
                "explicacion": "Las faltas injustificadas reducen los días contables de beneficios sociales como Gratificación y CTS.",
            },
        ],
    },
    # ------------------------------------------------------------------ NIVEL 6
    {
        "titulo": "Respeto y ética",
        "icono": "🤝",
        "insignia": "Respeto en acción",
        "tarjetas": [
            {
                "titulo": "Política salarial",
                "icono": "⚖️",
                "puntos": [
                    "Conjunto de orientaciones para distribuir equitativamente las cantidades asignadas a retribuir al personal.",
                    "Según la Ley 30709, que prohíbe la discriminación remunerativa entre varones y mujeres, PMA promueve la no discriminación remunerativa: igualdad de remuneración por igual trabajo.",
                ],
            },
            {
                "titulo": "Código de Ética y Conducta",
                "icono": "📕",
                "puntos": ["Revisa el Código de Ética y Conducta de Distribuidora PMA."],
                "imagen": "slide_35.jpg",
            },
            {
                "titulo": "Hostigamiento sexual laboral",
                "icono": "🚫",
                "puntos": ["Es una forma de violencia. Revisa con atención estas diapositivas."],
                "imagen": "slide_37.jpg",
                "imagen2": "slide_38.jpg",
                "imagen3": "slide_39.jpg",
            },
            {
                "titulo": "Sub comité de hostigamiento sexual laboral 2026-2028",
                "icono": "🛑",
                "puntos": ["Conoce a las personas del Sub Comité. Trabaja sin acoso."],
                "imagen": "slide_40.jpg",
            },
        ],
        "preguntas": [
            {
                "id": "N6-1",
                "texto": "La Ley 30709 prohíbe la discriminación remunerativa entre…",
                "opciones": ["Sedes", "Varones y mujeres", "Puestos de almacén", "Turnos"],
                "correcta": 1,
                "explicacion": "La Ley 30709 prohíbe la discriminación remunerativa entre varones y mujeres.",
            },
            {
                "id": "N6-2",
                "texto": "El hostigamiento sexual es una conducta de naturaleza o connotación sexual o sexista que es…",
                "opciones": [
                    "Aceptada si es en broma",
                    "No deseada por la persona a la que se dirige",
                    "Permitida entre compañeros",
                    "Permitida fuera del horario de trabajo",
                ],
                "correcta": 1,
                "explicacion": "Es una forma de violencia: conducta de naturaleza o connotación sexual o sexista, NO deseada por la persona a la que se dirige.",
            },
            {
                "id": "N6-3",
                "texto": "¿Cuál NO es una característica del consentimiento?",
                "opciones": ["Dado libremente", "Reversible", "Obligatorio", "Entusiasta"],
                "correcta": 2,
                "explicacion": "El consentimiento es dado libremente, reversible, entusiasta y específico.",
            },
        ],
    },
    # ------------------------------------------------------------------ NIVEL 7
    {
        "titulo": "Tu puesto",
        "icono": "🚚",
        "insignia": "Profesional de tu puesto",
        "tarjetas": [],   # se genera según el puesto elegido
        "preguntas": [],  # se genera según el puesto elegido
    },
]
