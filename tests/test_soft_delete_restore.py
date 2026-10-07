import unittest
from tests.common import temp_db
class TrashTests(unittest.TestCase):
 def test_soft_delete_and_restore(self):
  td,db=temp_db(); self.addCleanup(td.cleanup); now=db.now(); rid=db.execute('INSERT INTO tasks(title,created_at,updated_at) VALUES(?,?,?)',('x',now,now)); db.soft_delete('tasks',rid); self.assertEqual(db.one('SELECT deleted FROM tasks WHERE id=?',(rid,))[0],1); db.restore('tasks',rid); self.assertEqual(db.one('SELECT deleted FROM tasks WHERE id=?',(rid,))[0],0)
if __name__=='__main__': unittest.main()
