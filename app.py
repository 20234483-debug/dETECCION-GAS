"""FitRed · Entrenador ULima. Local Streamlit app; no external AI / network required."""
from __future__ import annotations
import csv
from io import StringIO
from pathlib import Path
import json
import random
import re
import streamlit as st
from engine import (money, compute_metrics, generated_case, health_case, fitred_case,
                    solution, grade_decision, generated_numeric_question)

st.set_page_config(page_title='Proyecto 20 · Entrenador ULima',page_icon='🎓',layout='wide',initial_sidebar_state='expanded')
BASE=Path(__file__).resolve().parent
@st.cache_data(show_spinner=False)
def get_bank():
    return json.loads((BASE/'data'/'questions.json').read_text(encoding='utf-8'))
BANK=get_bank()
KAHOOT=sum(x['source'].startswith('Kahoot profesor') for x in BANK)
BLACKBOARD=len(BANK)-KAHOOT

st.markdown('''<style>
:root { --indigo:#3154b3; --teal:#087e76; }
.block-container {max-width:1250px;padding-top:1.65rem;padding-bottom:3.4rem}
[data-testid="stSidebar"] {background:linear-gradient(160deg,rgba(49,84,179,.075),rgba(20,184,166,.045))}
h1,h2,h3 {letter-spacing:-.03em}
.main-hero {padding:25px 28px;border-radius:19px;background:linear-gradient(115deg,#112a54 0%,#26548f 68%,#168a9a 100%);color:white;margin-bottom:22px;box-shadow:0 12px 28px rgba(14,42,82,.15)}
.main-hero h1 {color:white;margin:0;font-size:2.25rem;font-weight:800}
.main-hero p {color:#d6e8ff;margin:8px 0 0;font-size:1rem}
.stat-grid {display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.stat-tile {border:1px solid #d6e2ed;border-radius:14px;padding:16px;background:rgba(70,125,180,.04)}
.stat-tile strong {display:block;font-size:1.55rem;color:#21519c}
.small-kicker {letter-spacing:.13em;text-transform:uppercase;font-size:12px;font-weight:700;color:#7087a9}
.hint {background:rgba(22,125,151,.075);border-left:4px solid #1d97ae;padding:12px 15px;border-radius:5px;margin:14px 0}
.stButton>button {border-radius:10px;min-height:40px;font-weight:650}
[data-testid="stMetric"] {border:1px solid rgba(130,155,183,.2);border-radius:14px;padding:12px}
@media(max-width:750px){.main-hero{padding:20px}.main-hero h1{font-size:1.7rem}.stat-grid{grid-template-columns:1fr}}
</style>''',unsafe_allow_html=True)


def init():
    defaults=dict(history=[], quiz_question=None,quiz_locked=False,quiz_done=False,quiz_seen=[],
                  quiz_round=0,quiz_deck=[],quiz_next_number=0,exam=None,exam_pos=0,exam_answers={},exam_done=False,
                  case_seed=3812,grades={})
    for k,v in defaults.items():
        if k not in st.session_state:st.session_state[k]=v
init()


def header(title:str,subtitle:str,eyebrow:str='ULIMA · EXAMEN ESCRITO 2'):
    st.markdown(f'<div class="main-hero"><div style="font-size:11px;letter-spacing:.18em;font-weight:750;color:#9ee3e4">{eyebrow}</div><h1>{title}</h1><p>{subtitle}</p></div>',unsafe_allow_html=True)


def source_note(q):
    return f"Semana {q['week']} · {q['source']}"


def explain(q):
    if q.get('explanation'):
        return q['explanation']
    s=q['question'].lower()
    reference=q['options'][q['answer']]
    patterns=[
       (['ev =','valor ganado',' earned value','(ev)'], 'EV es el valor presupuestado del trabajo completado, no el costo real. En actividades: EV = BAC de actividad × porcentaje real.'),
       (['spi','cronograma'], 'SPI = EV/PV; menor que 1 indica atraso en valor ganado. Para cambiar una línea base se requiere aprobación según gobernanza.'),
       (['cpi'], 'CPI = EV/AC; si es menor que 1 hay ineficiencia de costos.'),
       (['eac'], 'EAC = BAC/CPI cuando se supone que continúa la eficiencia de costos actual.'),
       (['cost vari','variación de costo','(cv)'], 'CV = EV − AC. Si CV es positivo, hay eficiencia de costos relativa al valor ganado.'),
       (['lead time','cycle time'], 'Lead Time cubre de solicitud a entrega; Cycle Time cubre tiempo de trabajo activo.'),
       (['burndown'], 'Burndown muestra trabajo pendiente a lo largo del Sprint.'),
       (['velocity','velocidad'], 'Velocity compara trabajo comprometido/terminado o ritmo terminado según el gráfico empleado.'),
       (['product owner','product backlog'], 'El PO ordena el Product Backlog buscando valor para usuarios y negocio; Developers seleccionan trabajo en Sprint Planning.'),
       (['review'], 'La Sprint Review inspecciona el incremento y recoge retroalimentación; la retrospectiva mejora el proceso.'),
       (['retrospectiva','retrospectivas','retrospective'], 'En retrospectivas se identifican causas y se acuerdan acciones medibles; Scrum Master facilita.'),
       (['dod','definition of done','terminado','definición de hecho'], 'DoD define la calidad compartida requerida para contabilizar una historia como terminada.'),
       (['scrum master'], 'El Scrum Master facilita Scrum, elimina impedimentos y promueve que el equipo aprenda.'),
       (['tuckman','turbulencia','formación','desempeño del equipo','normalización','normativización'], 'Tuckman: formación → turbulencia → normalización → desempeño → disolución.'),
       (['conflicto','harvard','negociación'], 'Negociación de Harvard: separar personas del problema, explorar intereses, generar opciones y aplicar criterios objetivos.'),
       (['pmo','opm3'], 'Una PMO ayuda a alinear proyectos con la estrategia y generar valor: apoyo, control o dirección según su autoridad.'),
       (['cambio','línea base','configuration','configuración'], 'El cambio predictivo se registra, analiza y autoriza; se protege la referencia aprobada. En ágil se ordenan nuevas necesidades en backlog.'),
       (['contingencia','reserva','riesgo','amenaza'], 'Riesgo es un evento incierto; contingencia cubre riesgos identificados. Revisa disparador, saldo y autoridad antes de activar una respuesta.')]
    hint=next((hint for clues,hint in patterns if any(x in s for x in clues)), '')
    return f'La alternativa respaldada por el material es: **{reference}**.'+(f' {hint}' if hint else ' Relaciónala con las reglas y definiciones de la semana indicada.')


def csv_bytes(rows):
    out=StringIO();cols=list(rows[0]) if rows else ['Sin registros']
    w=csv.DictWriter(out,fieldnames=cols,extrasaction='ignore');w.writeheader();w.writerows(rows)
    return ('\ufeff'+out.getvalue()).encode('utf-8')


def topic_tip(week):
    return {7:'Riesgo incierto vs. issue ocurrido; reserva, disparador, límite de autorización.',
            9:'BAC/PV/EV/AC no son intercambiables. Practica CPI, SPI y EAC.',
            10:'PO ordena; Developers crean incremento; Scrum Master facilita; DoD manda.',
            11:'El cambio exige trazabilidad; crashing solo ayuda si toca la rama limitante.',
            12:'Tuckman, diálogo, seguridad psicológica y retrospectiva accionable.',
            13:'PMO moderna entrega valor; apoyo/control/directiva y OPM3.'}.get(week,'Repasar teoría integrada')

with st.sidebar:
    st.markdown('### 🎓 Proyecto 20')
    st.caption('Entrenador local · Gestión de Proyectos ULima')
    page=st.radio('Ir a', ['🏠 Inicio','📘 Teoría corta','✅ Preguntas ilimitadas','📝 Simulacro de 28','🧠 Casos explicados','✍️ Practicar casos','💡 Tips y progreso'],label_visibility='collapsed')
    st.divider()
    st.caption('BANCO VERIFICADO')
    st.metric('Preguntas base',len(BANK))
    st.caption(f'{KAHOOT} Kahoot · {BLACKBOARD} Blackboard · ejercicios numéricos ilimitados')
    st.caption('Los nuevos ejercicios y casos llevan su origen identificado; no son preguntas oficiales.')

if page=='🏠 Inicio':
    header('Entrena como te van a evaluar','Teoría breve, preguntas reales, cálculos nuevos y decisiones híbridas con feedback y rúbrica.')
    st.markdown(f'''<div class="stat-grid"><div class="stat-tile"><div class="small-kicker">Preguntas base</div><strong>{len(BANK)}</strong>Kahoot + Blackboard</div><div class="stat-tile"><div class="small-kicker">Casos híbridos</div><strong>6 decisiones</strong>Por simulacro</div><div class="stat-tile"><div class="small-kicker">Objetivo</div><strong>20/20</strong>14 alternativas + 6 casos</div></div>''',unsafe_allow_html=True)
    st.markdown('### Cómo aprovecharlo')
    st.markdown('''1. **Teoría corta:** repasa la idea, las fórmulas y el error típico de cada semana.
2. **Preguntas ilimitadas:** responde un ítem y recibe feedback al instante; la app recircula el banco e inventa nuevos cálculos con cifras distintas.
3. **Simulacro de 28:** no se muestran las soluciones hasta terminar, como Blackboard.
4. **Casos explicados:** estudia FitRed y Salud Digital con los seis dictámenes y cálculos.
5. **Practicar casos:** contesta un caso nuevo con dictamen, sustento y evidencia; obtén corrección orientativa y comparación con una solución modelo.''')
    st.info('La evaluación de respuestas escritas es **automática y orientativa**: reconoce términos y cifras, pero no sustituye la corrección semántica de un profesor.')
    if st.session_state['history']:
        his=st.session_state['history'];st.metric('Aciertos acumulados en preguntas',f"{sum(z['ok'] for z in his)}/{len(his)}")

elif page=='📘 Teoría corta':
    header('Teoría que sí necesitas','Semanas 7–13 · definiciones, comparaciones y fórmulas para responder alternativas y casos.')
    theory=[
('7 · Riesgos y contingencias',r'''**Riesgo:** evento incierto que puede perjudicar (amenaza) o beneficiar (oportunidad). **Issue:** ya ocurrió. Un **disparador** es la señal prevista que activa una respuesta. **RBS** organiza fuentes de riesgos; **matriz P×I** prioriza probabilidad e impacto.

**Amenazas:** evitar = eliminar exposición; mitigar = reducir; transferir = trasladar parte del impacto (seguro); aceptar = asumir. **Oportunidades:** explotar = asegurar, mejorar = potenciar, compartir = asociarse, aceptar = aprovechar si aparece.

**Reserva de contingencia:** riesgos identificados. **Reserva de gestión:** imprevistos no identificados. En casos, mira **disparador + saldo + límite delegado** antes de autorizar un gasto. Una respuesta prevista no exige automáticamente CCB, depende del caso.'''),
('9 · Métricas y valor ganado',r'''**PV:** valor presupuestado que *debía* completarse al corte. **EV:** valor presupuestado del trabajo *realmente completado*. **AC:** gasto real. **BAC:** presupuesto total aprobado.

- EV = suma de (**BAC de actividad × avance real**).
- PV = suma de (**BAC de actividad × avance planificado**).
- **CPI = EV / AC**: menor que 1 indica ineficiencia en costos.
- **SPI = EV / PV**: menor que 1 indica atraso en valor ganado.
- **EAC = BAC / CPI**: costo total proyectado si el CPI actual se mantiene.
- **CV = EV − AC** y **SV = EV − PV**; negativo indica desviación desfavorable.

**Leading:** anticipa problemas; **Lagging:** muestra resultados ocurridos; métricas **accionables** facilitan decisiones. **Burndown:** trabajo restante. **Velocity:** ritmo/terminación por Sprint. **Lead Time:** solicitud a entrega. **Cycle Time:** tiempo de ejecución.'''),
('10 · Scrum y métodos ágiles',r'''**Predictivo:** planifica un alcance y controla cambios contra líneas base. **Ágil:** prioriza valor y adapta Product Backlog entre iteraciones. **Scrum:** transparencia, inspección, adaptación.

- **Product Owner:** ordena backlog según valor.
- **Developers:** planifican su trabajo del Sprint y crean incrementos usables.
- **Scrum Master:** facilita, no impone soluciones.
- **Product Backlog:** lista ordenada del producto. **Sprint Backlog:** objetivo, ítems seleccionados y plan. **Incremento:** resultado usable que cumple **DoD**.
- **Planning:** plan del Sprint; **Daily (15 min):** inspección y ajuste diario; **Review:** producto/interesados; **Retrospective:** mejora del proceso.

**Velocidad histórica** = promedio de puntos con DoD; **Capacidad normal** = Developers × días; **disponible** = normal − días no trabajados; **velocidad ajustada** = promedio × disponible/normal (*regla de los casos del profesor*).'''),
('11 · Cambios, calidad y cronograma',r'''**Línea base:** referencia formal aprobada de alcance, tiempo o costo. **CCB:** evalúa solicitudes y puede aprobar/rechazar/posponer/pedir información. **Change Log:** registro de decisiones. **Configuración:** control de versiones de artefactos. No cambies una línea base solo para esconder una desviación.

**Controlar Calidad** verifica técnicamente; **Validar Alcance** formaliza la aceptación del cliente.

**Ruta crítica:** secuencia de actividades con holgura total cero en el cronograma base. Relación **Fin-Inicio (FS):** la sucesora espera a que finalice la predecesora. Si F depende de D y E, espera a la **más tardía**. **Crashing:** más recursos para reducir duración; solo adelanta el final si toca el cuello de botella. **Fast tracking:** solapar actividades y aceptar más riesgo.'''),
('12 · Equipo, Tuckman y retrospectivas',r'''**Tuckman:** Formación (conocerse), Turbulencia (fricciones), Normalización (normas y confianza), Desempeño (autonomía y alto rendimiento) y Disolución (fin de equipo).

**Negociación Harvard:** separar personas del problema; centrarse en intereses; generar opciones de beneficio mutuo; usar criterios objetivos. Resolver problemas/confrontar es colaborativo. **Seguridad psicológica** fomenta expresar ideas sin miedo; acuerdos de equipo reducen conflictos.

**Retrospectiva Derby & Larsen:** armar escenario → recolectar datos → indagar → decidir acciones → cerrar. **Mad/Sad/Glad:** emociones. **5 porqués:** causas raíz. **SMART:** mejoras medibles.'''),
('13 · PMO orientada al valor',r'''**PMO:** oficina organizacional que da soporte, gobernanza y alineación a distintos proyectos; **Project Manager:** dirige un proyecto concreto.

- **PMO de Apoyo:** asesorías, plantillas, capacitación; bajo control.
- **PMO de Control:** cumplimiento de estándares y auditorías.
- **PMO Directiva:** dirige proyectos y asigna Project Managers.
- **PMO Corporativa:** nivel organización y estrategia; **funcional:** dentro de un área.
- PMO moderna: **socio centrado en el cliente y valor**, no burocracia sin utilidad.
- **OPM3:** Estandarizado → Medido → Controlado → Mejora continua.

PMO y su cliente maduro: pasar de hacer reportes a apoyar decisiones estratégicas y asesoría.''')]
    for title,body in theory:
        with st.expander('Semana '+title,expanded=title.startswith('9')):
            st.markdown(body)
    st.markdown('### Tarjeta de fórmulas')
    c1,c2=st.columns(2)
    with c1:st.code('EV = Σ (BAC_i × % real_i)\nPV = Σ (BAC_i × % plan_i)\nCPI = EV / AC\nSPI = EV / PV',language='text')
    with c2:st.code('EAC = BAC / CPI\nCV = EV - AC\nSV = EV - PV\nVel. ajust. = Vel. hist. × (disponible / normal)',language='text')
    st.caption('Semana 8 se trata aquí como integración de la planificación, sin inventar una evaluación específica.')

elif page=='✅ Preguntas ilimitadas':
    header('Preguntas ilimitadas','Pregunta aleatoria, marca A–D y conoce la respuesta explicada. Puedes seguir indefinidamente.')
    c1,c2,c3=st.columns([1.3,1,1])
    with c1:source=st.selectbox('Origen', ['Mixto (reales y nuevos cálculos)','Solo Kahoot original','Solo Blackboard real','Solo cálculos nuevos'],key='quiz_source')
    with c2:week=st.selectbox('Semana', ['Todas',7,9,10,11,12,13],key='quiz_week')
    with c3:
        st.write(' ')
        if st.button('🔀 Nueva ronda',use_container_width=True):
            st.session_state.quiz_deck=[];st.session_state.quiz_question=None;st.session_state.quiz_locked=False;st.session_state.quiz_round+=1;st.rerun()
    config=(source,str(week))
    if st.session_state.get('quiz_config')!=config:
        st.session_state.quiz_config=config;st.session_state.quiz_deck=[];st.session_state.quiz_question=None;st.session_state.quiz_locked=False
    valid=[q for q in BANK if (week=='Todas' or q['week']==week) and (source.startswith('Mixto') or (source=='Solo Kahoot original' and q['source'].startswith('Kahoot')) or (source=='Solo Blackboard real' and 'Blackboard' in q['source']))]
    def new_question():
        make_numeric = source=='Solo cálculos nuevos' or (source.startswith('Mixto') and random.random()<.32 and (week=='Todas' or week in [7,9,10,11]))
        if make_numeric:
            for tries in range(200):
                s=random.SystemRandom().randint(100_000,999_999_999)
                q=generated_numeric_question(s)
                if week=='Todas' or week==q['week']:return q
        if not valid:
            return None
        if not st.session_state.quiz_deck:
            st.session_state.quiz_deck=random.sample(valid,len(valid))
        return st.session_state.quiz_deck.pop()
    if st.session_state.quiz_question is None:
        st.session_state.quiz_question=new_question();st.session_state.quiz_locked=False
    q=st.session_state.quiz_question
    if q is None:st.warning('No hay preguntas para esa combinación de filtros. Prueba “Todas”.')
    else:
        st.caption(source_note(q))
        st.subheader(q['question'])
        locked=st.session_state.quiz_locked
        options=[f'{chr(65+i)}. {o}' for i,o in enumerate(q['options'])]
        choice=st.radio('Marca una alternativa',options,index=None,disabled=locked,key=f'quick_answer_{st.session_state.quiz_round}_{q["id"]}')
        if not locked:
            if st.button('Corregir respuesta',type='primary',disabled=choice is None):
                ans=options.index(choice)
                ok=ans==q['answer'];st.session_state.quiz_locked=True
                st.session_state.quiz_given=ans
                st.session_state.history.append(dict(id=q['id'],week=q['week'],source=q['source'],ok=int(ok),question=q['question'],selected=chr(65+ans),correct=chr(65+q['answer'])))
                st.rerun()
        else:
            if st.session_state.quiz_given==q['answer']:st.success('✅ ¡Correcto!')
            else:st.error(f'❌ Respuesta correcta: {chr(65+q["answer"])}. {q["options"][q["answer"]]}')
            st.markdown('**¿Por qué?**')
            st.write(explain(q))
            if q.get('note'):st.warning('Nota del material: '+q['note'])
            if st.button('Siguiente pregunta ➜',type='primary'):
                st.session_state.quiz_question=new_question();st.session_state.quiz_locked=False;st.session_state.quiz_round+=1;st.rerun()
    hist=st.session_state.history
    if hist:
        col1,col2,col3=st.columns(3)
        col1.metric('Respondidas',len(hist));col2.metric('Correctas',sum(h['ok'] for h in hist));col3.metric('Precisión',f"{100*sum(h['ok'] for h in hist)/len(hist):.1f}%")
        st.download_button('Descargar historial CSV',csv_bytes(hist),'historial_preguntas.csv','text/csv')

elif page=='📝 Simulacro de 28':
    header('Simulacro de alternativas','28 preguntas por 14 puntos: responde sin conocer la corrección hasta terminar.')
    if st.session_state.exam is None:
        n=st.select_slider('Cantidad de preguntas',options=[10,20,28,40,60,80,100],value=28)
        qtype=st.selectbox('Composición',['Mix: base + cálculos','Solo banco real','Solo Kahoot original'])
        st.caption('Las preguntas tienen la redacción original del material cuando provienen del banco real.')
        if st.button('Iniciar simulacro',type='primary'):
            candidates=[q for q in BANK if qtype!='Solo Kahoot original' or q['source'].startswith('Kahoot')]
            picks=random.sample(candidates,min(len(candidates),n))
            if qtype=='Mix: base + cálculos':
                generated=[generated_numeric_question(random.SystemRandom().randint(1_000_000,999_999_999)) for _ in range(max(2,n//4))]
                picks=picks[:max(0,n-len(generated))]+generated
                random.shuffle(picks)
            st.session_state.exam=picks;st.session_state.exam_answers={};st.session_state.exam_pos=0;st.session_state.exam_done=False;st.rerun()
    else:
        questions=st.session_state.exam;total=len(questions)
        if not st.session_state.exam_done:
            pos=st.session_state.exam_pos;q=questions[pos]
            st.progress((pos+1)/total,text=f'Pregunta {pos+1} de {total} · Respondidas: {len(st.session_state.exam_answers)}')
            st.caption(source_note(q));st.subheader(q['question'])
            opts=[f'{chr(65+i)}. {x}' for i,x in enumerate(q['options'])]
            old=st.session_state.exam_answers.get(pos)
            pick=st.radio('Marca una alternativa',opts,index=old if old is not None else None,key=f'exam_{pos}',on_change=None)
            if pick is not None:st.session_state.exam_answers[pos]=opts.index(pick)
            prev,next_,finish=st.columns([1,1,1])
            with prev:
                if st.button('◀ Anterior',disabled=pos==0,use_container_width=True):st.session_state.exam_pos-=1;st.rerun()
            with next_:
                if st.button('Siguiente ▶',disabled=pos==total-1,use_container_width=True):st.session_state.exam_pos+=1;st.rerun()
            with finish:
                if st.button('Entregar',type='primary',use_container_width=True):
                    st.session_state.exam_done=True
                    for i,q2 in enumerate(questions):
                        a=st.session_state.exam_answers.get(i)
                        st.session_state.history.append(dict(id=q2['id'],week=q2['week'],source=q2['source'],ok=int(a==q2['answer']),question=q2['question'],selected=chr(65+a) if a is not None else '-',correct=chr(65+q2['answer'])))
                    st.rerun()
        else:
            good=sum(st.session_state.exam_answers.get(i)==q['answer'] for i,q in enumerate(questions))
            grade=14*good/total
            c1,c2,c3=st.columns(3);c1.metric('Correctas',f'{good}/{total}');c2.metric('Nota equivalente de alternativas',f'{grade:.2f}/14');c3.metric('Porcentaje',f'{100*good/total:.1f}%')
            for i,q in enumerate(questions):
                a=st.session_state.exam_answers.get(i);correct=(a==q['answer'])
                with st.expander(f"{'✅' if correct else '❌'} {i+1}. {q['question'][:105]}",expanded=False):
                    st.write('**Tu respuesta:** '+(q['options'][a] if a is not None else 'Sin responder'))
                    st.write('**Correcta:** '+q['options'][q['answer']])
                    st.write(explain(q))
                    if q.get('note'):st.warning(q['note'])
            if st.button('Generar otro simulacro',type='primary'):
                st.session_state.exam=None;st.session_state.exam_answers={};st.session_state.exam_done=False;st.rerun()


def render_context(case,show_calcs=False):
    p=case['predictive'];a=case['agile'];m=compute_metrics(case)
    st.markdown(f'### {case["title"]}')
    st.caption(case['kind'])
    st.write(case['summary'])
    with st.expander('A · Predictivo — cronograma, EVM, gobernanza y riesgos',expanded=True):
        st.markdown(f'**Corte: día {p["cut_day"]}. Línea base: día {p["base_finish"]}.** D terminará día **{p["d_finish"]}**; E empezó día **{p["e_actual_start"]}**, durará **{p["e_duration"]}** días. F (duración {p["f_duration"]}) depende de **D y E**, y G (duración {p["g_duration"]}) depende de F; todas son fin-inicio.')
        st.dataframe([{'Actividad':x['id']+' · '+x['name'],'BAC (S/)':x['bac'],'Plan (%)':x['planned_pct'],'Real (%)':x['actual_pct'],'AC (S/)':x['ac']} for x in p['work']],use_container_width=True,hide_index=True)
        st.markdown(f'**Reglas del caso:** BAC = {money(p["bac"])}. Reserva de contingencia aparte del BAC: {money(p["reserve"])}. Ya se gastaron {money(p["reserve_used"])} en R1 (sin incluir ese uso en AC). Si **EAC > BAC + reserva**, escalar al CCB; si no, solo informar al patrocinador. Director puede activar respuesta prevista de hasta **{money(p["approval_limit"])} por evento**, si hay saldo; montos mayores o cambio de línea base requieren CCB.')
        st.write(f'**R3:** disparador {"ocurrió" if p["risk_trigger"] else "no ocurrió"}; respuesta prevista cuesta {money(p["risk_cost"])}. El crashing de una jornada en {case["d2_crash_target"]} cuesta {money(p["crash_cost"])} y se supone autorizado (solo evaluar efecto en plazo).')
    with st.expander('B · Ágil — Sprints, costos, interesados y backlog',expanded=True):
        st.write(f'**App {a["title"]}**: 4 Sprints de {a["days_per_sprint"]} días, {a["developers"]} Developers. Product Goal: {a["product_goal"]}. Solo se cuentan puntos que cumplieron DoD.')
        st.dataframe([{'Sprint':f'Sprint {i+1}','Puntos iniciados':a['started_points'][i],'Puntos DoD':a['done_points'][i],'Goal cumplido':a['sprint_goals'][i],'Costo real (S/)':a['spent_sprints'][i]} for i in range(3)],hide_index=True,use_container_width=True)
        st.markdown(f'En el **Sprint 4**, un Developer tendrá **{a["leave_days"]} días** sin remuneración; tarifa de {money(a["leave_rate"])} por día. Costo planeado del Sprint 4 antes de licencia: {money(a["next_sprint_budget"])}. Presupuesto total del componente: {money(a["budget"])}. El PO solo puede aprobar un gasto extra si existe saldo libre; no hay ampliación disponible.')
        st.write(f'**Sprint Review:** {a["discovery_count"]} de {a["user_count"]} usuarios solicitaron «{a["desired_feature"]}». Otro hallazgo: {a["second_evidence"]} usuarios manifestaron un problema relacionado. El requerimiento de «{a["admin_feature"]}» viene de dirección, sin evidencia de uso.')
        st.dataframe([{'Producto / Feature':a['desired_feature'],'Origen':a['feature_origin']},{'Producto / Feature':a['admin_feature'],'Origen':a['admin_origin']}],hide_index=True,use_container_width=True)
        st.info('Regla ágil del caso: velocidad proyectada = promedio de los 3 Sprints terminados × (capacidad disponible / capacidad normal).')
    if show_calcs:
        st.markdown(f'**Valores resueltos:** PV {money(m["pv"])}, EV {money(m["ev"])}, AC {money(m["ac"])}, CPI {m["cpi"]:.4f}, EAC {money(m["eac"])}; velocidad {m["vel_adj"]:.2f} puntos; saldo {money(m["balance"])}.')


if page=='🧠 Casos explicados':
    header('Casos explicados','Primero lee los datos y las seis decisiones. Despliega una solución cuando quieras comprobarla.')
    selected=st.selectbox('Modelo a estudiar',['FitRed Conectado · caso recibido','Salud Digital · modelo anterior'])
    case=fitred_case() if selected.startswith('FitRed') else health_case()
    render_context(case)
    st.markdown('### Decisiones con solución paso a paso')
    for i,description in enumerate(case['decisions']):
        with st.expander(f'D{i+1} · {description[:115]}',expanded=False):
            st.write('**Propuesta:** '+description)
            sol=solution(case,i)
            st.markdown('**Dictamen correcto:** '+sol['correct'])
            st.write('**Sustento teórico:** '+sol['theory'])
            st.write('**Evidencias y operaciones:** '+sol['evidence'])
    st.caption('Son soluciones de estudio derivadas de los datos del material compartido. Comprueba fórmulas y razones; no memorices el patrón de acuerdo/desacuerdo.')

elif page=='✍️ Practicar casos':
    header('Practica como en el Excel','Seis decisiones independientes · Dictamen 0.25, sustento 0.25, evidencias 0.50 puntos.')
    left,right=st.columns([3,1])
    with left:selection=st.selectbox('Caso a resolver',['Nuevo caso generado','FitRed original','Salud Digital'])
    with right:
        if st.button('🎲 Generar otro',use_container_width=True):
            st.session_state.case_seed=random.SystemRandom().randint(10_000,999_999_999);st.rerun()
    case=generated_case(st.session_state.case_seed) if selection=='Nuevo caso generado' else (fitred_case() if selection=='FitRed original' else health_case())
    render_context(case)
    st.markdown('### Hoja de respuestas · estilo Excel')
    st.caption('El profesor califica cada decisión de forma independiente. Completa las tres columnas antes de presionar “Corregir”.')
    st.dataframe([{'N°':f'D{i+1}','Tema':solution(case,i)['topic'],'Decisión propuesta':d,'Puntaje máx.':1.0} for i,d in enumerate(case['decisions'])],hide_index=True,use_container_width=True)
    earned=0.;rows=[];graded_count=0
    for i,desc in enumerate(case['decisions']):
        result_key=f'grade_{case["id"]}_{i}'
        result=st.session_state.grades.get(result_key)
        with st.expander(f'D{i+1} · {solution(case,i)["topic"]}'+(f'  |  {result["points"]:.2f}/1' if result else ''),expanded=i==0):
            st.write('**Decisión a evaluar:** '+desc)
            with st.form(f'case_form_{case["id"]}_{i}'):
                verdict=st.selectbox('Dictamen',['Selecciona…','DE ACUERDO','EN DESACUERDO'],key=f'v_{case["id"]}_{i}')
                reasoning=st.text_area('Sustento teórico (0.25 pt)',height=90,placeholder='Concepto, regla y por qué se aplica a esta decisión...',key=f't_{case["id"]}_{i}')
                numbers=st.text_area('Evidencias del caso y cálculos (0.50 pt)',height=128,placeholder='Escribe operaciones, valores numéricos, comparación con límites/umbral...',key=f'e_{case["id"]}_{i}')
                send=st.form_submit_button(f'Corregir D{i+1}',type='primary')
            if send:
                if verdict=='Selecciona…' or not reasoning.strip() or not numbers.strip():st.warning('Completa dictamen, teoría y evidencias antes de corregir.')
                else:
                    result=grade_decision(case,i,verdict,reasoning,numbers)
                    st.session_state.grades[result_key]=result
            if result:
                graded_count+=1;earned+=result['points']
                st.metric('Puntaje orientativo',f'{result["points"]:.2f} / 1.00')
                st.write(f'**Desglose:** dictamen {result["verdict"]:.2f}/0.25 · teoría {result["theory"]:.2f}/0.25 · evidencias {result["evidence"]:.2f}/0.50')
                for msg in result['feedback']:st.info(msg)
                with st.expander('Ver corrección y respuesta modelo'):
                    s=result['reference']
                    st.write('**Dictamen:** '+s['correct']);st.write('**Teoría:** '+s['theory']);st.write('**Evidencias:** '+s['evidence'])
                    st.caption('La puntuación de texto libre usa reconocimiento de palabras y números; puede no detectar demostraciones equivalentes. Contrasta siempre con la solución.')
                rows.append({'Caso':case['title'],'Decisión':f'D{i+1}','Propuesta':desc,'Mi dictamen':st.session_state.get(f'v_{case["id"]}_{i}'),'Sustento teórico':st.session_state.get(f't_{case["id"]}_{i}'),'Evidencias':st.session_state.get(f'e_{case["id"]}_{i}'),'Nota orientativa /1':result['points'],'Clave':result['reference']['correct']})
    if graded_count:
        st.divider()
        c1,c2=st.columns(2);c1.metric('Decisiones corregidas',f'{graded_count}/6');c2.metric('Puntos orientativos acumulados',f'{earned:.2f}/6')
        st.download_button('📥 Exportar mis respuestas para Excel (CSV)',data=csv_bytes(rows),file_name=f'respuestas_{case["id"]}.csv',mime='text/csv')
    st.warning('La calificación automática es aproximada: detecta criterios/valores relevantes, pero no puede verificar todos los razonamientos escritos. Usa la solución modelo como referencia final.')

elif page=='💡 Tips y progreso':
    header('Tips para subir tu nota','Atajos mentales, errores típicos, práctica y diagnóstico de debilidades.')
    with st.expander('Antes del examen: seis reglas de oro',expanded=True):
        st.markdown('''1. **Primero identifica el componente:** predictivo (EVM, ruta crítica, riesgos) o ágil (velocidad, presupuesto, backlog).
2. **Nunca confundas EV y AC:** EV es valor presupuestado ejecutado; AC es gasto real.
3. **Escribe fórmulas y números, no solo conclusiones:** los cálculos valen la mitad del punto del caso.
4. **Crashing no siempre adelanta el proyecto:** busca qué predecesora termina última.
5. **Para reservas:** verifica tres condiciones: disparador, saldo libre y tope delegado.
6. **No adivines las seis decisiones:** pueden ser correctas o incorrectas; cada una se juzga independientemente.''')
    st.markdown('### Respuestas que suelen confundirse')
    st.table([
       {'Confusión':'EV vs AC','Lo correcto':'EV = valor ganado; AC = costo real'},
       {'Confusión':'CPI vs SPI','Lo correcto':'CPI = costo; SPI = tiempo/avance'},
       {'Confusión':'Controlar Calidad vs Validar Alcance','Lo correcto':'Verificación técnica vs aceptación formal'},
       {'Confusión':'Sprint Review vs Retrospective','Lo correcto':'Inspeccionar producto vs mejorar proceso'},
       {'Confusión':'Product Owner vs Developers','Lo correcto':'PO ordena backlog; Developers planifican ejecución Sprint'},
       {'Confusión':'PMO Apoyo / Control / Directiva','Lo correcto':'Asesorar / exigir estándares / dirigir proyectos'},
       {'Confusión':'Burndown vs Velocity','Lo correcto':'Pendiente vs ritmo de entrega'},
       {'Confusión':'Riesgo vs problema','Lo correcto':'Incierto vs ya ocurrido'},
    ])
    st.markdown('### Tu desempeño en preguntas')
    his=st.session_state.history
    if not his:
        st.info('Todavía no hay resultados. Haz 10 preguntas ilimitadas o un simulacro y vuelve aquí para ver tus semanas débiles.')
    else:
        st.metric('Aciertos',f"{sum(x['ok'] for x in his)}/{len(his)}")
        stats=[]
        for w in [7,9,10,11,12,13]:
            attempts=[h for h in his if h['week']==w]
            if attempts:stats.append({'Semana':w,'Correctas':sum(h['ok'] for h in attempts),'Intentos':len(attempts),'Precisión (%)':round(100*sum(h['ok'] for h in attempts)/len(attempts),1),'Qué repasar':topic_tip(w)})
        st.dataframe(stats,hide_index=True,use_container_width=True)
        weak=sorted(stats,key=lambda x:x['Precisión (%)'])[:2]
        st.markdown('**Enfócate ahora en:** '+', '.join(f"semana {x['Semana']}" for x in weak))
        st.download_button('Exportar resultados CSV',csv_bytes(his),'mi_progreso.csv',mime='text/csv')
        if st.button('Borrar resultados de esta sesión'):
            st.session_state.history=[];st.rerun()
    st.caption('Los datos se guardan en la sesión del navegador durante el uso. Descarga el CSV si quieres conservar tu historial entre reinicios.')

st.divider()
st.caption('Material educativo basado en Kahoot y evaluaciones compartidas por estudiantes, más casos generados con fines de práctica. No es un examen oficial ni una garantía de nota. Funciona localmente, sin clave API ni envío de respuestas a servicios externos.')
