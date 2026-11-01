import unittest
from datetime import datetime,timezone
from source_audit import safe_https,audit
class AuditTests(unittest.TestCase):
 def test_url(self):
  self.assertTrue(safe_https('https://example.org/article'))
  self.assertFalse(safe_https('http://example.org/article'))
  self.assertFalse(safe_https('https://localhost/test'))
 def test_audit(self):
  a={'id':'x','article_url':'https://example.org/a','source':'A','related_sources':[{'source':'B'}],'published_at':datetime.now(timezone.utc).isoformat(),'image_url':'https://example.org/img.jpg','image_license':'CC BY 4.0','image_credit':'Autor'}
  self.assertEqual(audit(a)['issues'],[])
  a['image_credit']=''
  self.assertIn('imagem_sem_credito',audit(a)['issues'])
if __name__=='__main__':unittest.main()
