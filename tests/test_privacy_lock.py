import unittest
from app.services.privacy import make_pin_hash,verify_pin
class PrivacyTests(unittest.TestCase):
 def test_pin_is_salted_and_verified(self):
  h,s=make_pin_hash('4321'); self.assertNotEqual(h,'4321'); self.assertTrue(verify_pin('4321',h,s)); self.assertFalse(verify_pin('1234',h,s))
if __name__=='__main__': unittest.main()
