# How to write them?

## What a Basic Regression Test Looks Like
Below is what a minimal regression test should look like:

```python
import unittest

class SomeTest(unittest.TestCase):
	def setUp(self):
    	# test setup code goes here
		# it runs before every test

	def tearDown(self):
		# test tear down code goes here
		# it runs after every test

	def test_something(self):
		# test code here
		self.assertEqual(1 + 1, 2)
		
	def test_something_else(self):
		# test code here
		self.assertEqual(1 + 1 + 1, 2)