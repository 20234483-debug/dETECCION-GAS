# Proyecto 20 — Entrenador de Gestión de Proyectos ULima

Una aplicación **local de Streamlit** para estudiar los temas de las semanas **7 a 13** y practicar el formato del segundo examen: **28 preguntas de alternativas (14 puntos) + seis decisiones de caso (6 puntos)**.

## Cómo abrirla

**Requisitos:** Python **3.10 o superior** y conexión a internet **solo para instalar Streamlit la primera vez**.

### Windows

1. Descomprime el ZIP en una carpeta.
2. Haz doble clic en `INICIAR_WINDOWS.bat` (instala los paquetes la primera vez y después abre Streamlit), o abre PowerShell en esa carpeta.
3. Si lo haces manualmente:

```powershell
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

4. El navegador abrirá la app. Si no, entra a **http://localhost:8501**.

Si el archivo `.bat` es bloqueado por políticas de seguridad, usa PowerShell con los comandos manuales.

### macOS / Linux

Abre Terminal en la carpeta que descomprimiste:

```bash
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

También puedes usar `bash INICIAR_MAC_LINUX.sh`.

**Cerrar:** vuelve a la terminal y presiona `Ctrl + C`.

## Qué contiene

| Sección | Función |
| --- | --- |
| **Teoría corta** | Riesgos, EVM, Scrum, cambios, Tuckman, PMO y fórmulas |
| **Preguntas ilimitadas** | 116 preguntas base + preguntas nuevas de cálculo con números cambiantes, sin tope de práctica |
| **Simulacro** | 10, 20, 28, 40, 60, 80 o 100 preguntas; respuestas ocultas hasta el final |
| **Casos explicados** | FitRed y Salud Digital con seis decisiones resueltas cada uno |
| **Practicar casos** | Caso híbrido nuevo cada vez: escribir dictamen, teoría y evidencias, obtener feedback por rúbrica |
| **Tips y progreso** | Errores típicos, indicadores de acierto por semana y descarga CSV |

### Origen del banco

- **60 Kahoot originales**: diez preguntas por semana, de las semanas **7, 9, 10, 11, 12 y 13**.
- **56 preguntas de evaluaciones Blackboard** compartidas: 28 de un estudiante y 28 de una compañera.
- **Preguntas numéricas generadas** de EVM, ruta crítica, reservas, Scrum y presupuesto: se identifican como **generadas**, NO oficiales.
- Los ítems originales conservan la redacción principal y alternativas, aunque se limpiaron etiquetas sueltas de Blackboard como `Correct:` y prefijos redundantes `A)` dentro de opciones.
- Cuando se detectó una clave o redacción discutible en la evaluación (como Velocity frente a Burndown), la app advierte de ello sin modificar la clave proporcionada.

### Los casos

- **FitRed**: caso del archivo `Caso_4_Gimnasios.docx` compartido. Las seis respuestas, calculadas de los datos del enunciado, son: **D1 no, D2 sí, D3 sí, D4 no, D5 no, D6 sí**.
- **Salud Digital**: modelo de profesor compartido en capturas; **D1 no, D2 no, D3 sí, D4 no, D5 no, D6 no**.
- **Generador de casos**: nuevos proyectos con cifras y decisiones distintas. Debes evaluar cada decisión independientemente y seguir las reglas escritas en cada caso.

**IMPORTANTE sobre las notas en casos:** el programa usa una evaluación **heurística, sin IA externa**: verifica el dictamen y busca palabras teóricas y valores calculados. Puede ser demasiado estricto o demasiado flexible con respuestas equivalentes. Se muestra una **solución modelo** después de responder para autoevaluarte. No se envía nada a un servidor ni requiere claves de API.

### Exportación para Excel

En **Practicar casos**, después de corregir, pulsa **Exportar mis respuestas para Excel (CSV)**. El archivo se abre en Excel y contiene tu dictamen, teoría, evidencias, nota estimada y clave por decisión. En **Tips y progreso** también puedes exportar el historial de preguntas.

### Conservación de progreso

La información se guarda en la sesión de Streamlit mientras esté abierta. **Descarga tu CSV** si quieres conservar un registro permanente; al reiniciar la app la sesión puede perderse.

## Estructura técnica

- `app.py`: interfaz Streamlit.
- `engine.py`: cálculos y corrector independientes de Streamlit.
- `data/questions.json`: preguntas, alternativas, claves y procedencia.
- `tests/test_engine.py`: pruebas de consistencia, casos, preguntas numéricas y corrección.
- `requirements.txt`: dependencias.

## Ejecutar pruebas (opcional)

```bash
python -m unittest discover -s tests -v
```

## Nota académica

Material educativo de práctica basado en contenido compartido por estudiantes. No es una plataforma de la Universidad de Lima ni una garantía de que las mismas preguntas se repitan en una evaluación.
