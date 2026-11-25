"""Pure (UI-independent) project management practice engine."""
from __future__ import annotations
import math
import random
import re
import unicodedata
from typing import Any


def money(n: float) -> str:
    return f"S/ {n:,.2f}"


def clean(s: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFD',str(s).lower()) if unicodedata.category(c) != 'Mn')


def numeric_mentions(text: str) -> list[float]:
    """Recognize 1,200 / 1.200 / 1,200.50 / 1.200,50 / 23.83 / 23,83."""
    nums=[]
    for raw in re.findall(r'(?<![\w])\d+(?:[.,]\d+)*(?!\w)',str(text)):
        if ',' in raw and '.' in raw:
            x=raw.replace(',','') if raw.rfind('.') > raw.rfind(',') else raw.replace('.','').replace(',','.')
        elif ',' in raw or '.' in raw:
            sep=',' if ',' in raw else '.'
            chunks=raw.split(sep)
            if len(chunks)>2 or (len(chunks)==2 and len(chunks[-1])==3 and len(chunks[0])<=3):
                x=''.join(chunks)
            else:
                x=raw.replace(',','.')
        else:x=raw
        try:nums.append(float(x))
        except ValueError:pass
    return nums


def has_number(text:str, value:float)->bool:
    return any(abs(n-value)<=(.015 if abs(value)<10 else max(.11, abs(value)*.0006)) for n in numeric_mentions(text))


def compute_metrics(case:dict)->dict:
    p=case['predictive']; a=case['agile']
    ev=sum(r['bac']*r['actual_pct']/100 for r in p['work'])
    pv=sum(r['bac']*r['planned_pct']/100 for r in p['work'])
    ac=sum(r['ac'] for r in p['work'])
    cpi=ev/ac if ac else 0.0
    eac=p['bac']/cpi if cpi else math.inf
    threshold=p['bac']+p['reserve']
    last=p['d_finish']; e_end=p['e_actual_start']+p['e_duration']-1
    current_finish=max(last,e_end)+p['f_duration']+p['g_duration']
    after_crash_e=max(last,e_end-1)+p['f_duration']+p['g_duration']
    after_crash_d=max(last-1,e_end)+p['f_duration']+p['g_duration']
    spent=sum(a['spent_sprints'])
    normal=a['developers']*a['days_per_sprint']
    available=normal-a['leave_days']
    v_hist=sum(a['done_points'])/len(a['done_points'])
    v_projected=v_hist*available/normal
    next_cost=a['next_sprint_budget']-a['leave_days']*a['leave_rate']
    total=spent+next_cost
    available_balance=a['budget']-total
    reserve_left=p['reserve']-p['reserve_used']
    return dict(pv=pv,ev=ev,ac=ac,cpi=cpi,spi=(ev/pv if pv else 0),eac=eac,threshold=threshold,
                finish=current_finish, after_crash_e=after_crash_e, after_crash_d=after_crash_d,
                reserve_left=reserve_left,normal=normal,available=available,vel_hist=v_hist,
                vel_adj=v_projected,sprint_spent=spent,sprint4_cost=next_cost,projected_total=total,
                balance=available_balance)


def fitred_case()->dict:
    return dict(id='fitred',title='FitRed Conectado',kind='Modelo original FitRed',
     summary='La cadena FitRed moderniza seis gimnasios: torniquetes con lector QR (predictivo) y la app ClaseYa para reservar clases (Scrum). La salida es conjunta.',
     predictive=dict(bac=80000,reserve=4000,reserve_used=1200,approval_limit=2000,base_finish=19,
       cut_day=11,d_finish=13,e_actual_start=10,e_duration=5,f_duration=4,g_duration=2,
       crash_cost=1400,risk_cost=1600,risk_trigger=True,
       work=[
       dict(id='A',name='Relevamiento de sedes',bac=4000,planned_pct=100,actual_pct=100,ac=4300),
       dict(id='B',name='Diseño del control de acceso',bac=8000,planned_pct=100,actual_pct=100,ac=8500),
       dict(id='C',name='Permisos y licencias',bac=3000,planned_pct=100,actual_pct=100,ac=3900),
       dict(id='D',name='Fabricación de torniquetes',bac=25000,planned_pct=60,actual_pct=60,ac=16600),
       dict(id='E',name='Obras civiles y eléctricas',bac=10000,planned_pct=100,actual_pct=40,ac=4100),
       dict(id='F',name='Instalación de torniquetes',bac=20000,planned_pct=0,actual_pct=0,ac=0),
       dict(id='G',name='Pruebas y puesta en marcha',bac=10000,planned_pct=0,actual_pct=0,ac=0)]),
     agile=dict(title='ClaseYa',developers=4,days_per_sprint=10,leave_days=5,leave_rate=300,
       started_points=[28,24,25],done_points=[25,19,22],sprint_goals=['Sí','No','Sí'],
       budget=64000,spent_sprints=[15200,16800,16600],next_sprint_budget=16000,
       proposal_points=22,extra_test_cost=1000,user_count=40,discovery_count=22,
       second_evidence=15,desired_feature='Ver aforo en tiempo real',
       feature_origin='22 de 40 socios pidieron conocer el aforo y 15 llegaron a clases llenas',
       admin_feature='Notificaciones push de promociones',admin_origin='pedido comercial sin datos de uso',
       proposed_evidence_priority=True,product_goal='Reservar cupos desde el celular sin llegar a clases llenas'),
     d2_crash_target='E',
     decisions=[
       'El director propone no elevar la situación al Comité de Cambios y solo informar al patrocinador, porque considera que el EAC se mantendrá dentro del BAC más la reserva.',
       'Para recuperar la fecha de fin de la línea base (día 19), el director propone comprimir la actividad E en un día a un costo autorizado de S/ 1,400. Evalúe solo si recupera la fecha.',
       'El director propone activar la respuesta prevista de R3 (instaladores certificados externos, S/ 1,600) con cargo a la reserva, sin consultar al CCB.',
       'Los Developers proponen comprometer 22 puntos en el Sprint 4.',
       'El Product Owner propone contratar una prueba externa de usabilidad de S/ 1,000 durante el Sprint 4, sin ampliar presupuesto.',
       'El Product Owner propone crear “Ver aforo en tiempo real” en el Product Backlog y ordenarlo por encima de las notificaciones de promociones; explicará al gerente comercial la evidencia de la Sprint Review.'
     ])


def health_case()->dict:
    return dict(id='salud',title='Salud Digital',kind='Modelo del profesor (datos compartidos)',
     summary='Red de centros de salud: componente A instala kioscos en cinco sedes (predictivo); componente B es una app de citas SaludYa (Scrum).',
     predictive=dict(bac=100000,reserve=8000,reserve_used=2000,approval_limit=3000,base_finish=19,cut_day=12,
       d_finish=14,e_actual_start=12,e_duration=4,f_duration=3,g_duration=2,crash_cost=1500,risk_cost=2500,risk_trigger=True,
       work=[
       dict(id='A',name='Relevamiento técnico',bac=6000,planned_pct=100,actual_pct=100,ac=6400),
       dict(id='B',name='Diseño',bac=9000,planned_pct=100,actual_pct=100,ac=9500),
       dict(id='C',name='Permisos y licencias',bac=5000,planned_pct=100,actual_pct=100,ac=6200),
       dict(id='D',name='Fabricación e importación',bac=40000,planned_pct=75,actual_pct=75,ac=33000),
       dict(id='E',name='Cableado',bac=12000,planned_pct=100,actual_pct=25,ac=3900),
       dict(id='F',name='Montaje',bac=18000,planned_pct=0,actual_pct=0,ac=0),
       dict(id='G',name='Pruebas',bac=10000,planned_pct=0,actual_pct=0,ac=0)]),
     agile=dict(title='SaludYa',developers=6,days_per_sprint=10,leave_days=5,leave_rate=200,
       started_points=[28,30,32],done_points=[24,28,26],sprint_goals=['Sí','Sí','Sí'],
       budget=80000,spent_sprints=[19000,20500,20500],next_sprint_budget=20000,
       proposal_points=28,extra_test_cost=2500,user_count=50,discovery_count=30,
       second_evidence=25,desired_feature='Cita en 2 pasos',
       feature_origin='30 de 50 no completaron una cita; 25 de esos 30 son adultos mayores',
       admin_feature='Módulo de Reportes de Prensa',admin_origin='presión política sin evidencia de uso',
       proposed_evidence_priority=False,product_goal='Permitir agendar 1,500 citas el primer mes'),
     d2_crash_target='D',
     decisions=[
       'El director propone NO elevar la situación al CCB y únicamente informar al patrocinador porque cree que EAC no supera BAC + reserva.',
       'Para recuperar el día 19, propone comprimir D un día por S/ 1,500 (costo autorizado). Evalúe solo si recupera la fecha.',
       'El director propone contratar una cuadrilla eléctrica alterna por S/ 2,500, activando el riesgo R3 con la reserva, sin autorización previa del CCB.',
       'Los Developers proponen comprometer 28 puntos en el Sprint 4.',
       'El Product Owner propone gastar S/ 2,500 en una prueba de usabilidad externa sin ampliar el presupuesto.',
       'El Product Owner propone priorizar el módulo de reportes de prensa sobre «Cita en 2 pasos» porque la autoridad política tiene más poder.'
     ])


def generated_case(seed:int)->dict:
    rnd=random.Random(seed)
    contexts=[('Red de bibliotecas','LibroYa','reservar préstamos y consultar disponibilidad','Búsqueda accesible','Reporte institucional','usuarios'),
              ('Red de colegios','AulaYa','inscribir estudiantes a talleres sin colas','Inscripción simplificada','Módulo de prensa','familias'),
              ('Red de centros deportivos','DeporteYa','reservar canchas sin sobreocupación','Cupos en tiempo real','Promociones VIP','socios'),
              ('Red de municipalidades','CitaCiudad','obtener citas de atención municipal','Trámite en dos pasos','Reporte político','ciudadanos'),
              ('Cadena de clínicas','TurnoYa','reservar consultas médicas sin esperas','Disponibilidad en tiempo real','Noticias corporativas','pacientes')]
    name,app,goal,discovery,admin,people=rnd.choice(contexts)
    a_d=rnd.randint(2,3); b_d=rnd.randint(3,5); c_d=rnd.randint(2,4)
    d_d=rnd.randint(4,7); e_d=rnd.randint(3,5); f_d=rnd.randint(2,4); g_d=rnd.randint(1,3)
    d_end=a_d+b_d+d_d
    base_e_end=a_d+c_d+e_d
    # Baseline d-end limits the launch (fixed approved baseline)
    if base_e_end>d_end:
        d_d+=base_e_end-d_end
        d_end=base_e_end
    lag=rnd.choice([1,1,2,3])
    e_actual_end=d_end+lag
    e_actual_start=e_actual_end-e_d+1
    cut_day=e_actual_start
    budgets=[rnd.choice([4000,5000,6000]),rnd.choice([6500,8000,9000]),rnd.choice([2500,3000,5000]),
             rnd.choice([22000,27000,30000]),rnd.choice([9000,11000,12000]),rnd.choice([16000,18000]),rnd.choice([7500,9000])]
    bac=sum(budgets)
    pct=[100,100,100,60,40,0,0];planned=[100,100,100,60,100,0,0]
    ev=sum(b*pc/100 for b,pc in zip(budgets,pct))
    reserve=rnd.choice([4000,6000,8000])
    ratio= rnd.choice([1.02,1.03,1.14,1.17])
    ac_goal=round(ev*ratio)
    ac_vec=[int(round(ac_goal*x/sum([5,7,4,17,4]))) for x in [5,7,4,17,4]]+[0,0]
    ac_vec[4]+=ac_goal-sum(ac_vec)
    work=[dict(id=x,name=y,bac=b,planned_pct=p,actual_pct=r,ac=cost) for x,y,b,p,r,cost in zip(
      'ABCDEFG',['Levantamiento','Diseño','Permisos','Fabricación','Instalaciones previas','Integración','Pruebas'],budgets,planned,pct,ac_vec)]
    limit=rnd.choice([1500,2000,2500]);risk_cost=rnd.choice([1200,1600,1900,2600]);spent_reserve=rnd.choice([800,1200,1800]);
    dev=rnd.choice([4,5,6]);leave=rnd.choice([3,4,5,6]);v=[rnd.randint(17,27) for _ in range(3)]
    hist=sum(v)/3; proj=hist*(dev*10-leave)/(dev*10)
    propose_points=math.floor(proj)-rnd.choice([1,2]) if rnd.random()<.42 else math.ceil(proj)+rnd.choice([1,3,4]);propose_points=max(10,propose_points)
    sprint_budget=rnd.choice([12000,15000,18000,20000]); agile_budget=sprint_budget*4
    leave_rate=rnd.choice([150,200,250,300]);
    cost_spents=[sprint_budget+rnd.choice([-800,-400,0,300,600,1000]) for _ in range(3)]
    next_cost=sprint_budget-leave*leave_rate
    budget_balance=agile_budget-sum(cost_spents)-next_cost
    # Guarantee some positive / some negative balances: if no available budget, extra cannot be approved
    test_cost=rnd.choice([600,900,1000,1500,2000,2500])
    user_count=rnd.choice([30,40,50]);discovery_count=rnd.randint(user_count//2,user_count*4//5)
    second=rnd.randint(7,17)
    priority_good=rnd.choice([True,False])
    case=dict(id=f'gen-{seed}',title=f'{name} · Caso {seed}',kind='Simulacro generado (no oficial)',
       summary=f'{name} moderniza servicios con un componente A predictivo de equipamiento y un componente B Scrum llamado {app}. Ambos deben lanzar juntos.',
       predictive=dict(bac=bac,reserve=reserve,reserve_used=spent_reserve,approval_limit=limit,
         base_finish=d_end+f_d+g_d,cut_day=cut_day,a_duration=a_d,b_duration=b_d,c_duration=c_d,d_duration=d_d,d_finish=d_end,e_actual_start=e_actual_start,
         e_duration=e_d,f_duration=f_d,g_duration=g_d,crash_cost=rnd.choice([800,1200,1500]),risk_cost=risk_cost,risk_trigger=True,work=work),
       agile=dict(title=app,developers=dev,days_per_sprint=10,leave_days=leave,leave_rate=leave_rate,
         started_points=[v[0]+3,v[1]+3,v[2]+3],done_points=v,sprint_goals=['Sí','Sí','No'],
         budget=agile_budget,spent_sprints=cost_spents,next_sprint_budget=sprint_budget,proposal_points=propose_points,
         extra_test_cost=test_cost,user_count=user_count,discovery_count=discovery_count,second_evidence=second,
         desired_feature=discovery,feature_origin=f'{discovery_count} de {user_count} {people} reportaron dificultad',
         admin_feature=admin,admin_origin='pedido de directivo sin validación con usuarios',
         proposed_evidence_priority=priority_good,product_goal=goal),
       d2_crash_target='E')
    d=case['predictive'];ag=case['agile']
    case['decisions']=[
      'El Director propone NO elevar la situación al Comité de Cambios y solo informar al patrocinador, pues estima que EAC no supera BAC + reserva.',
      f'Para recuperar la fecha base (día {d["base_finish"]}), propone hacer crashing de E por un día (S/ {d["crash_cost"]}, costo autorizado). Evalúa solo si recupera la fecha.',
      f'Ante el disparador del riesgo R3, el Director propone activar una respuesta prevista por S/ {d["risk_cost"]} con la reserva, sin solicitar aprobación al Comité.',
      f'Los Developers proponen comprometer {ag["proposal_points"]} puntos en el Sprint 4.',
      f'El Product Owner propone una prueba externa por S/ {ag["extra_test_cost"]}, sin ampliar presupuesto.',
      (f'El Product Owner propone agregar y priorizar «{discovery}» por encima de «{admin}», justificándolo con las pruebas con usuarios.' if priority_good else
      f'El Product Owner propone priorizar «{admin}» por encima de «{discovery}» porque lo pide un directivo de alto poder, aunque no aporte evidencia de uso.')]
    return case


THEORY=[
 ('EVM y escalamiento',['ev','cpi','eac','control de costos','umbral','comite de cambios','cc b','cc b','gobernanza']),
 ('Ruta crítica y crashing',['ruta critica','dependencia','fin-inicio','crashing','predecesora','cuello de botella']),
 ('Riesgos y delegación',['riesgo','disparador','contingencia','reserva','limite','delegacion','autoridad']),
 ('Velocidad y capacidad Scrum',['velocidad','capacidad','puntos','scrum','dod','dias-persona','historica']),
 ('Saldo presupuestal',['presupuesto','saldo','costos','gastos','aprobacion','licencia','financiero']),
 ('Valor y Product Backlog',['product backlog','valor','prioriz','review','usuarios','evidencia','product owner'])]


def solution(case:dict,which:int)->dict:
    m=compute_metrics(case);p=case['predictive'];a=case['agile'];crash=case['d2_crash_target']
    if which==0:
        correct=m['eac']<=m['threshold']
        theory='La regla particular del proyecto exige escalar al CCB cuando EAC supera BAC + reserva de contingencia. EAC = BAC / CPI y CPI = EV / AC.'
        evidence=f'EV = {money(m["ev"])}; AC = {money(m["ac"])}; PV = {money(m["pv"])}. CPI = EV / AC = {m["cpi"]:.4f}. EAC = {money(m["eac"])}. Umbral = {money(m["threshold"])}. '
        evidence+=('No lo supera; informar al patrocinador cumple la regla.' if correct else 'Lo supera; omitir el CCB incumple la regla.')
        nums=[('EV',m['ev']),('AC',m['ac']),('CPI',m['cpi']),('EAC',m['eac']),('Umbral',m['threshold'])]
    elif which==1:
        end=m['after_crash_e'] if crash=='E' else m['after_crash_d']
        correct=end<=p['base_finish']
        theory='En dependencias fin-inicio, F debe esperar la terminación de ambas predecesoras D y E. Crashing solo recupera el hito si reduce la rama que controla la fecha final.'
        evidence=f'D acaba día {p["d_finish"]}. E acaba día {p["e_actual_start"]+p["e_duration"]-1}. Sin crashing, F+G concluyen día {m["finish"]}. Al comprimir {crash} un día, concluyen día {end}; línea base día {p["base_finish"]}. '
        evidence+=('Se recupera la fecha.' if correct else 'No se recupera la fecha.')
        nums=[('Fin actual',m['finish']),('Fin con crashing',end),('Línea base',p['base_finish'])]
    elif which==2:
        correct=p['risk_trigger'] and p['risk_cost']<=p['approval_limit'] and p['risk_cost']<=m['reserve_left']
        theory='Una respuesta de contingencia para un riesgo identificado puede activarse sin CCB cuando se cumple el disparador, el límite delegado y la disponibilidad de reserva.'
        evidence=f'El disparador {"ocurrió" if p["risk_trigger"] else "NO ocurrió"}. Reserva disponible = {money(p["reserve"])} - {money(p["reserve_used"])} = {money(m["reserve_left"])}. Respuesta = {money(p["risk_cost"])}. Límite por evento = {money(p["approval_limit"])}.'
        nums=[('Reserva disponible',m['reserve_left']),('Respuesta R3',p['risk_cost']),('Límite PM',p['approval_limit'])]
    elif which==3:
        correct=a['proposal_points']<=m['vel_adj']+.001
        theory='Para planificar un Sprint se usa el ritmo de trabajo aceptado conforme a DoD y se ajusta por capacidad real disponible, según la regla del caso.'
        evidence=f'Velocidad histórica = {a["done_points"]} / 3 = {m["vel_hist"]:.2f} puntos. Capacidad normal = {m["normal"]} días-persona; disponible = {m["available"]}. Velocidad ajustada = {m["vel_hist"]:.2f} × {m["available"]}/{m["normal"]} = {m["vel_adj"]:.2f}; propuesta = {a["proposal_points"]}.'
        nums=[('Promedio',m['vel_hist']),('Capacidad',m['available']),('Proyección',m['vel_adj']),('Compromiso',a['proposal_points'])]
    elif which==4:
        correct=a['extra_test_cost']<=m['balance']
        theory='Según las reglas particulares del caso, el PO solo puede aprobar gastos extra con saldo libre no comprometido. La licencia no remunerada reduce el costo estimado del Sprint 4.'
        evidence=f'Sprints 1–3 = {money(m["sprint_spent"])}. Ahorro licencia = {a["leave_days"]} × {money(a["leave_rate"])} = {money(a["leave_days"]*a["leave_rate"])}. Sprint 4 ajustado = {money(m["sprint4_cost"])}. Total proyectado = {money(m["projected_total"])}; saldo libre = {money(m["balance"])} frente a gasto de {money(a["extra_test_cost"])}.'
        nums=[('Sprint 4',m['sprint4_cost']),('Total',m['projected_total']),('Saldo',m['balance']),('Costo adicional',a['extra_test_cost'])]
    else:
        correct=a['proposed_evidence_priority']
        theory='El Product Owner ordena el Product Backlog buscando el mayor valor y apoyándose en evidencias de la Sprint Review, sin confundir poder jerárquico con valor de uso.'
        evidence=f'{a["discovery_count"]} de {a["user_count"]} usuarios ({100*a["discovery_count"]/a["user_count"]:.1f}%) pidieron «{a["desired_feature"]}»; el objetivo del producto es {a["product_goal"]}. «{a["admin_feature"]}» carece de validación de uso.'
        nums=[('Usuarios afectados',a['discovery_count']),('Muestra',a['user_count'])]
    return dict(correct='DE ACUERDO' if correct else 'EN DESACUERDO', theory=theory,evidence=evidence,numbers=nums,topic=THEORY[which][0],keywords=THEORY[which][1])


def grade_decision(case:dict,which:int,dictamen:str,theory:str,evidence:str)->dict:
    sol=solution(case,which)
    verdict=.25 if dictamen==sol['correct'] else 0.0
    norm=clean(theory)
    matched=[x for x in sol['keywords'] if clean(x) in norm]
    theory_pts=.25 if matched else 0
    hit=[(label,num) for label,num in sol['numbers'] if has_number(evidence,num)]
    fraction=len(hit)/len(sol['numbers'])
    evidence_pts= .5 if fraction>=.75 else (.25 if fraction>=.35 else 0.0)
    feedback=[]
    if not verdict:feedback.append(f'Dictamen: lo sustentado por el caso es {sol["correct"]}.')
    if not theory_pts:feedback.append('Teoría: nombra el concepto/regla que gobierna esta decisión, no solo una opinión.')
    if fraction<.75:feedback.append('Evidencias aún no detectadas: '+', '.join(f'{label} ({num:g})' for label,num in sol['numbers'] if not has_number(evidence,num)))
    if fraction>=.75 and theory_pts and verdict:feedback.append('Bien: el dictamen, la regla y la mayoría de cifras esperadas aparecen en tu respuesta.')
    return dict(points=round(verdict+theory_pts+evidence_pts,2),verdict=verdict,theory=theory_pts,evidence=evidence_pts,feedback=feedback,reference=sol,auto=True)


def generated_numeric_question(seed:int)->dict:
    rnd=random.Random(seed)
    type_=rnd.randrange(8)
    a=rnd.randint(10,32)*1000
    b=rnd.randint(33,60)*1000
    c=rnd.randint(66,99)*1000
    if type_==0:
        pct=rnd.choice([20,35,40,50,60,75,80]);correct=a*pct/100
        q=f'Una actividad tiene BAC de {money(a)} y está completada al {pct}%. ¿Cuál es su EV?'
        opts=[correct,a,a*(100-pct)/100,correct*.8]
        why=f'EV = BAC × avance real = {a:,} × {pct}% = {money(correct)}.'
        topic='Medición y EVM';week=9
    elif type_==1:
        ev=rnd.randrange(25000,50000,1000);ac=ev+rnd.randrange(2000,13000,1000)
        correct=round(ev/ac,3);q=f'Si EV = {money(ev)} y AC = {money(ac)}, ¿cuál es el CPI?'
        opts=[correct,round(ac/ev,3),round(ev/(ac+8000),3),round((ac-ev)/ac,3)]
        why=f'CPI = EV / AC = {ev:,}/{ac:,} = {correct:.3f}; menor que 1 indica ineficiencia de costos.'
        topic='Medición y EVM';week=9
    elif type_==2:
        ev=rnd.randrange(30000,60000,1000);pv=ev+rnd.randrange(2000,12000,1000)
        correct=round(ev/pv,3);q=f'Con EV = {money(ev)} y PV = {money(pv)}, ¿cuánto es SPI?'
        opts=[correct,round(pv/ev,3),round(ev/(pv+10000),3),round((pv-ev)/pv,3)]
        why=f'SPI = EV / PV = {ev:,}/{pv:,} = {correct:.3f} (retraso en términos de valor ganado).'
        topic='Medición y EVM';week=9
    elif type_==3:
        ev=rnd.randrange(24000,40000,1000);ac=ev+rnd.choice([5000,6000,8000]);bac=rnd.choice([70000,90000,100000]);
        correct=round(bac*ac/ev,2);q=f'Proyecto con BAC {money(bac)}, EV {money(ev)}, AC {money(ac)}. Si EAC = BAC / CPI, ¿cuál es EAC?'
        opts=[correct,bac,round(bac*(ev/ac),2),round(bac+(ac-ev),2)]
        why=f'CPI={ev}/{ac}={ev/ac:.4f}; EAC={bac}/CPI={money(correct)}.'
        topic='Medición y EVM';week=9
    elif type_==4:
        hist=rnd.randint(18,32); dev=rnd.randint(4,7); leave=rnd.randint(2,6)
        correct=round(hist*(dev*10-leave)/(dev*10),2)
        q=f'La velocidad histórica es {hist} puntos. Hay {dev} Developers × 10 días, pero uno tendrá {leave} días de licencia. ¿Qué velocidad ajustada proyecta la regla proporcional?'
        opts=[correct,hist,round(hist*(dev-1)/dev,2),round(hist*(dev*10+leave)/(dev*10),2)]
        why=f'Capacidad normal={dev*10}, disponible={dev*10-leave}; velocidad={hist}×({dev*10-leave}/{dev*10})={correct:.2f} pt.'
        topic='Scrum';week=10
    elif type_==5:
        initial=rnd.choice([4000,5000,8000]);spent=rnd.choice([1000,1500,2000]);reply=rnd.choice([1300,1800,2400,3200]);limit=2000
        cond=reply<=limit and reply<=initial-spent
        q=f'Reserva = {money(initial)}; ya se gastó {money(spent)}; límite delegado al PM = {money(limit)}. El riesgo se activó y su respuesta cuesta {money(reply)}. ¿Puede ejecutarse sin CCB?'
        opts=['Sí, porque hay un plan de riesgos','No, porque no existe ninguna reserva','Sí, si cumple límite y saldo','No, porque supera el límite o saldo']
        answer=2 if cond else 3
        return dict(id=f'N-{seed}',source='Pregunta numérica generada',week=7,topic='Gestión de riesgos',question=q,options=opts,answer=answer,explanation=f'Saldo={initial-spent:,}; respuesta={reply:,}; límite={limit:,}. '+('Cumple las dos reglas.' if cond else 'No cumple al menos una regla.'))
    elif type_==6:
        budget=rnd.choice([48000,64000,80000]);spent=budget-rnd.choice([14000,18000,20000]);planned=rnd.choice([13000,15000,18000]);saving=rnd.choice([500,1000,1500]);
        free=budget-spent-(planned-saving)
        correct=free
        q=f'Presupuesto ágil = {money(budget)}, Sprints anteriores = {money(spent)}, próximo Sprint planeado = {money(planned)} y ahorro por licencia = {money(saving)}. ¿Cuál es el saldo libre?'
        opts=[free,free+saving,free-saving,budget-spent]
        why=f'Saldo = {budget} − {spent} − ({planned} − {saving}) = {money(free)}.'
        topic='Scrum';week=10
    else:
        d=rnd.randint(10,15);e=d+rnd.randint(1,3);f=rnd.randint(2,4);g=rnd.randint(1,3)
        correct=e+f+g
        q=f'F inicia después de que terminen D (día {d}) y E (día {e}); F dura {f} días y G, sucesora FS de F, dura {g} días. ¿En qué día termina G?'
        opts=[correct,d+f+g,e+f+g-1,e+f+g+1]
        why=f'F comienza día {e+1} y termina {e+f}; G termina {e+f+g}. Siempre esperar a la predecesora más tardía.'
        topic='Control de cambios';week=11
    # Distinct answers for numerical questions; do not show ambiguous duplicates.
    if len(set(opts))<4:
        candidates=[correct+10,correct-10,correct+20,correct-20] if correct>100 else [correct+0.1,correct-0.1,correct+0.2,correct-0.2]
        for j in range(1,4):
            if opts[j]==correct or opts.count(opts[j])>1:
                opts[j]=next(x for x in candidates if x not in opts[:j] and x!=correct)
    ans=0
    opts_text=[money(float(v)) if abs(v)>=1000 else (f'{float(v):.3f}' if type_ in (1,2) else f'{float(v):.2f}' if type_==4 else str(int(v)) if v==int(v) else f'{float(v):.2f}') for v in opts]
    order=list(range(4));rnd.shuffle(order)
    return dict(id=f'N-{seed}',source='Pregunta numérica generada',week=week,topic=topic,
                question=q,options=[opts_text[i] for i in order],answer=order.index(ans),explanation=why)
