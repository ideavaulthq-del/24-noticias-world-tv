import unittest,tempfile,json
from pathlib import Path
from editorial import related,enrich
class EditorialTests(unittest.TestCase):
 def test_topic(self):
  self.assertTrue(related('Governo anuncia novas medidas para habitação em Lisboa','Novas medidas de habitação anunciadas pelo Governo em Lisboa'))
 def test_no_false_verification(self):
  a=[dict(id='a',source='A',original_title='Governo anuncia novas medidas para habitação em Lisboa',article_url='https://a',title='a'),dict(id='b',source='B',original_title='Novas medidas de habitação anunciadas pelo Governo em Lisboa',article_url='https://b',title='b')]
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'overrides.json';p.write_text('{}');out=enrich(a,p)
  self.assertEqual(out[0]['verification_status'],'fontes_relacionadas_nao_verificadas')
  self.assertTrue(out[0]['related_sources'])
if __name__=='__main__':unittest.main()
