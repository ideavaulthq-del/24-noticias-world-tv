import unittest
from pathlib import Path
class DraftTests(unittest.TestCase):
 def test_drafts_are_not_automatically_approved(self):
  code=(Path(__file__).parent/'draft_ai.py').read_text()
  self.assertNotIn("editorial_overrides.json",code)
  self.assertIn('PENDENTE_REVISAO_HUMANA',code)
if __name__=='__main__':unittest.main()
