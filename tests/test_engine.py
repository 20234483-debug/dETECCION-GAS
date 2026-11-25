import unittest
import sys
import json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from engine import (fitred_case,health_case,generated_case,compute_metrics,
                    solution,grade_decision,generated_numeric_question,numeric_mentions,has_number)
BASE=Path(__file__).resolve().parent.parent

class CasesTest(unittest.TestCase):
 def test_bank_all_key_options(self):
  bank=json.loads((BASE/'data'/'questions.json').read_text(encoding='utf-8'))
  self.assertEqual(116,len(bank))
  self.assertEqual(60,len([x for x in bank if x['source'].startswith('Kahoot')]))
  self.assertEqual(56,len([x for x in bank if 'Blackboard' in x['source']]))
  ids=[x['id'] for x in bank]
  self.assertEqual(len(ids),len(set(ids)))
  for q in bank:
   self.assertEqual(4,len(q['options']))
   self.assertIn(q['answer'],range(4))
   self.assertTrue(all(q['options']))
 def test_fitred_actual(self):
  c=fitred_case();m=compute_metrics(c)
  self.assertEqual(m['pv'],40000)
  self.assertEqual(m['ev'],34000)
  self.assertEqual(m['ac'],37400)
  self.assertAlmostEqual(m['cpi'],34000/37400)
  self.assertAlmostEqual(m['eac'],88000)
  self.assertEqual(m['threshold'],84000)
  self.assertEqual(m['finish'],20)
  self.assertEqual(m['after_crash_e'],19)
  self.assertEqual(m['reserve_left'],2800)
  self.assertEqual(m['available'],35)
  self.assertAlmostEqual(m['vel_adj'],19.25)
  self.assertEqual(m['balance'],900)
  self.assertEqual([solution(c,i)['correct'] for i in range(6)],
   ['EN DESACUERDO','DE ACUERDO','DE ACUERDO','EN DESACUERDO','EN DESACUERDO','DE ACUERDO'])
 def test_health_case(self):
  c=health_case();m=compute_metrics(c)
  self.assertEqual(m['ev'],53000)
  self.assertEqual(m['pv'],62000)
  self.assertEqual(m['ac'],59000)
  self.assertAlmostEqual(m['eac'],111320.7547,places=2)
  self.assertEqual([solution(c,i)['correct'] for i in range(6)],
   ['EN DESACUERDO','EN DESACUERDO','DE ACUERDO','EN DESACUERDO','EN DESACUERDO','EN DESACUERDO'])
 def test_generated_cases_valid_all(self):
  all_solutions=[]
  for seed in range(100):
   c=generated_case(seed);m=compute_metrics(c)
   self.assertEqual(sum(r['bac'] for r in c['predictive']['work']),c['predictive']['bac'])
   self.assertTrue(m['eac']>0)
   self.assertTrue(m['finish']>=c['predictive']['base_finish'])
   self.assertEqual(len(c['decisions']),6)
   sol=[solution(c,i) for i in range(6)]
   self.assertTrue(all(x['correct'] in ['DE ACUERDO','EN DESACUERDO'] for x in sol))
   all_solutions.extend(x['correct'] for x in sol)
  self.assertIn('DE ACUERDO',all_solutions)
  self.assertIn('EN DESACUERDO',all_solutions)
 def test_numeric_questions(self):
  for seed in range(400):
   q=generated_numeric_question(seed)
   self.assertEqual(len(q['options']),4)
   self.assertIn(q['answer'],range(4))
   self.assertEqual(len(set(q['options'])),4,seed)
 def test_evidence_parse(self):
  n=numeric_mentions('EAC S/ 88,000.00; CPI 0.9091; saldo S/ 2.800,00; punto 19')
  for x in [88000,0.9091,2800,19]:self.assertIn(x,n)
  self.assertTrue(has_number('CPI = 0,91',0.9090909))
  self.assertFalse(has_number('CPI = 0,75',0.9090909))
 def test_feedback(self):
  c=fitred_case();answer=solution(c,0)
  res=grade_decision(c,0,'EN DESACUERDO',answer['theory'],answer['evidence'])
  self.assertEqual(1.0,res['points'])
  wrong=grade_decision(c,0,'DE ACUERDO','porque sí','no hice cálculos')
  self.assertEqual(0,wrong['points'])

if __name__=='__main__':unittest.main()
