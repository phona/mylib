import unittest
from datetime import datetime

from lib import var, Declared


class InnerJSONTestClass(Declared):
	ia = var(int)
	ib = var(int)


class CombineJSONTestClass(Declared):
	a = var(int)
	b = var(str)
	json = var('JSONTestClass')


class JSONTestClass(Declared):
	a = var(int)
	b = var(float)
	c = var(bytes)
	d = var(str)
	e = var(bool)
	f = var(list)
	g = var(dict)


class InheritedJSONTestClass(JSONTestClass, InnerJSONTestClass):
	iia = var(int)


class NewVarJsonTestClass(Declared):
	a = var(int, field_name="na")
	b = var(int, field_name="nb")
	c = var(datetime)


class NewVarDeclaredTestCase(unittest.TestCase):

	def test_str(self):
		json_obj = NewVarJsonTestClass(1, 2)
		self.assertEqual(str(json_obj), "NewVarJsonTestClass(a=1,b=2)")

	def test_to_dict(self):
		json_obj = NewVarJsonTestClass(1, 2)
		self.assertEqual(json_obj.to_dict(), {"na": 1, "nb": 2})

	def test_to_json(self):
		json_obj = NewVarJsonTestClass(1, 2)
		self.assertEqual(json_obj.to_json(), "{\"na\": 1, \"nb\": 2}")

	def test_from_dict(self):
		dct = {"na": 1, "nb": 2}
		json_obj = NewVarJsonTestClass.from_dict(dct)
		self.assertEqual(str(json_obj), "NewVarJsonTestClass(a=1,b=2)")

	def test_hash(self):
		dct_1 = {"na": 1, "nb": 2}
		dct_2 = {"na": 2, "nb": 1}
		json_obj_1 = NewVarJsonTestClass.from_dict(dct_1)
		json_obj_2 = NewVarJsonTestClass.from_dict(dct_1)
		json_obj_3 = NewVarJsonTestClass.from_dict(dct_2)
		self.assertEqual(hash(json_obj_1), hash(json_obj_2))
		self.assertNotEqual(hash(json_obj_1), hash(json_obj_3))

	def test_eq(self):
		dct_1 = {"na": 1, "nb": 2}
		dct_2 = {"na": 2, "nb": 1}
		json_obj_1 = NewVarJsonTestClass.from_dict(dct_1)
		json_obj_2 = NewVarJsonTestClass.from_dict(dct_1)
		json_obj_3 = NewVarJsonTestClass.from_dict(dct_2)
		self.assertNotEqual(json_obj_1, 1)
		self.assertEqual(json_obj_1, json_obj_2)
		self.assertNotEqual(json_obj_1, json_obj_3)


class CombineDeclaredTestCase(unittest.TestCase):

	def test_str(self):
		json_obj = CombineJSONTestClass(1, "123", JSONTestClass(1, 1.2, b"123", "123", True, [1, 2, 3], {"a": 1}))
		self.assertEqual(str(json_obj), "CombineJSONTestClass(a=1,b=123,json=JSONTestClass(a=1,b=1.2,c=b'123',d=123,e=True,f=[1, 2, 3],g={'a': 1}))")

	def test_to_dict(self):
		json_obj = CombineJSONTestClass(1, "123", JSONTestClass(1, 1.2, b"123", "123", True, [1, 2, 3], {"a": 1}))
		self.assertEqual(json_obj.to_dict(), {"a": 1, "b": "123", "json": {"a": 1, "b": 1.2, "c": [49, 50, 51], "d": "123", "e": True, "f": [1, 2, 3], "g": {"a": 1}}})

	def test_to_json(self):
		json_obj = CombineJSONTestClass(1, "123", JSONTestClass(1, 1.2, b"123", "123", True, [1, 2, 3], {"a": 1}))
		self.assertEqual(json_obj.to_json(), "{\"a\": 1, \"b\": \"123\", \"json\": {\"a\": 1, \"b\": 1.2, \"c\": [49, 50, 51], \"d\": \"123\", \"e\": true, \"f\": [1, 2, 3], \"g\": {\"a\": 1}}}")

	def test_from_dict(self):
		dct = {"a": 1, "b": "123", "json": {"a": 1, "b": 1.2, "c": b'123', "d": "123", "e": True, "f": [1, 2, 3], "g": {"a": 1}}}
		json_obj = CombineJSONTestClass.from_dict(dct)
		self.assertEqual(str(json_obj), "CombineJSONTestClass(a=1,b=123,json=JSONTestClass(a=1,b=1.2,c=b'123',d=123,e=True,f=[1, 2, 3],g={'a': 1}))")

	def test_hash(self):
		dct_1 = {"a": 1, "b": "123", "json": {"a": 1, "b": 1.2, "c": b'123', "d": "123", "e": True, "f": [1, 2, 3], "g": {"a": 1}}}
		dct_2 = {"a": 12, "b": "21123", "json": {"a": 1, "b": 2.2, "c": b'123', "d": "123", "e": True, "f": [1, 2, 3], "g": {"a": 1}}}
		json_obj_1 = CombineJSONTestClass.from_dict(dct_1)
		json_obj_2 = CombineJSONTestClass.from_dict(dct_1)
		json_obj_3 = CombineJSONTestClass.from_dict(dct_2)
		self.assertEqual(hash(json_obj_1), hash(json_obj_2))
		self.assertNotEqual(hash(json_obj_1), hash(json_obj_3))

	def test_eq(self):
		dct_1 = {"a": 1, "b": "123", "json": {"a": 1, "b": 1.2, "c": b'123', "d": "123", "e": True, "f": [1, 2, 3], "g": {"a": 1}}}
		dct_2 = {"a": 12, "b": "21123", "json": {"a": 1, "b": 2.2, "c": b'123', "d": "123", "e": True, "f": [1, 2, 3], "g": {"a": 1}}}
		json_obj_1 = CombineJSONTestClass.from_dict(dct_1)
		json_obj_2 = CombineJSONTestClass.from_dict(dct_1)
		json_obj_3 = CombineJSONTestClass.from_dict(dct_2)
		self.assertNotEqual(json_obj_1, 1)
		self.assertEqual(json_obj_1, json_obj_2)
		self.assertNotEqual(json_obj_1, json_obj_3)


class InheritedDeclaredTestCase(unittest.TestCase):

	def test_str(self):
		json_obj = InheritedJSONTestClass(100, 1, 1.2, b"123", "123", True, [1, 2, 3], {"a": 1}, 10, 11)
		self.assertEqual(str(json_obj), "InheritedJSONTestClass(iia=100,a=1,b=1.2,c=b'123',d=123,e=True,f=[1, 2, 3],g={'a': 1},ia=10,ib=11)")

	def test_to_dict(self):
		json_obj = InheritedJSONTestClass(100, 1, 1.2, b"123", "123", True, [1, 2, 3], {"a": 1}, 10, 11)
		self.assertEqual(json_obj.to_dict(), {"iia": 100, "a": 1, "b": 1.2, "c": [49, 50, 51], "d": "123", "e": True, "f": [1, 2, 3], "g": {"a": 1}, "ia": 10, "ib": 11})

	def test_to_json(self):
		json_obj = InheritedJSONTestClass(100, 1, 1.2, b"123", "123", True, [1, 2, 3], {"a": 1}, 10, 11)
		self.assertEqual(json_obj.to_json(), "{\"iia\": 100, \"a\": 1, \"b\": 1.2, \"c\": [49, 50, 51], \"d\": \"123\", \"e\": true, \"f\": [1, 2, 3], \"g\": {\"a\": 1}, \"ia\": 10, \"ib\": 11}")

	def test_from_dict(self):
		dct = {"iia": 100, "a": 1, "b": 1.2, "c": b'123', "d": "123", "e": True, "f": [1, 2, 3], "g": {"a": 1}, "ia": 10, "ib": 11}
		json_obj = InheritedJSONTestClass.from_dict(dct)
		self.assertEqual(str(json_obj), "InheritedJSONTestClass(iia=100,a=1,b=1.2,c=b'123',d=123,e=True,f=[1, 2, 3],g={'a': 1},ia=10,ib=11)")

	def test_hash(self):
		dct_1 = {"iia": 100, "a": 1, "b": 1.2, "c": b'123', "d": "123", "e": True, "f": [1, 2, 3], "g": {"a": 1}, "ia": 10, "ib": 11}
		dct_2 = {"iia": 11, "a": 12, "b": 1.2, "c": b'123', "d": "1123", "e": True, "f": [1, 2, 3], "g": {"a": 1}, "ia": 10, "ib": 11}
		json_obj_1 = InheritedJSONTestClass.from_dict(dct_1)
		json_obj_2 = InheritedJSONTestClass.from_dict(dct_1)
		json_obj_3 = InheritedJSONTestClass.from_dict(dct_2)
		self.assertEqual(hash(json_obj_1), hash(json_obj_2))
		self.assertNotEqual(hash(json_obj_1), hash(json_obj_3))

	def test_eq(self):
		dct_1 = {"iia": 100, "a": 1, "b": 1.2, "c": b'123', "d": "123", "e": True, "f": [1, 2, 3], "g": {"a": 1}, "ia": 10, "ib": 11}
		dct_2 = {"iia": 11, "a": 12, "b": 1.2, "c": b'123', "d": "1123", "e": True, "f": [1, 2, 3], "g": {"a": 1}, "ia": 10, "ib": 11}
		json_obj_1 = InheritedJSONTestClass.from_dict(dct_1)
		json_obj_2 = InheritedJSONTestClass.from_dict(dct_1)
		json_obj_3 = InheritedJSONTestClass.from_dict(dct_2)
		self.assertNotEqual(json_obj_1, 1)
		self.assertEqual(json_obj_1, json_obj_2)
		self.assertNotEqual(json_obj_1, json_obj_3)


class SimpleDeclaredTestCase(unittest.TestCase):

	def test_str(self):
		json_obj = JSONTestClass(1, 1.2, b"123", "123", True, [1, 2, 3], {"a": 1})
		self.assertEqual(str(json_obj), "JSONTestClass(a=1,b=1.2,c=b'123',d=123,e=True,f=[1, 2, 3],g={'a': 1})")

	def test_to_dict(self):
		json_obj = JSONTestClass(1, 1.2, b"123", "123", True, [1, 2, 3], {"a": 1})
		self.assertEqual(json_obj.to_dict(), {"a": 1, "b": 1.2, "c": [49, 50, 51], "d": "123", "e": True, "f": [1, 2, 3], "g": {"a": 1}})
		json_obj_1 = JSONTestClass(a=1, b=1.2, f=[1, 2, 3])
		self.assertRaises(TypeError, JSONTestClass, 1.2)
		self.assertRaises(AttributeError, json_obj_1.to_dict)
		self.assertEqual(json_obj_1.to_dict(use_strict=False), {"a": 1, "b": 1.2, "f": [1, 2, 3]})

	def test_to_json(self):
		json_obj = JSONTestClass(1, 1.2, b"123", "123", True, [1, 2, 3], {"a": 1})
		self.assertEqual(json_obj.to_json(), "{\"a\": 1, \"b\": 1.2, \"c\": [49, 50, 51], \"d\": \"123\", \"e\": true, \"f\": [1, 2, 3], \"g\": {\"a\": 1}}")

	def test_from_dict(self):
		dct = {"a": 1, "b": 1.2, "c": b'123', "d": "123", "e": True, "f": [1, 2, 3], "g": {"a": 1}}
		json_obj = JSONTestClass.from_dict(dct)
		self.assertEqual(str(json_obj), "JSONTestClass(a=1,b=1.2,c=b'123',d=123,e=True,f=[1, 2, 3],g={'a': 1})")

	def test_hash(self):
		dct_1 = {"a": 1, "b": 1.2, "c": b'123', "d": "123", "e": True, "f": [1, 2, 3], "g": {"a": 1}}
		dct_2 = {"a": 2, "b": 1.2, "c": b'123', "d": "12333", "e": True, "f": [1, 2, 3], "g": {"a": 1}}
		json_obj_1 = JSONTestClass.from_dict(dct_1)
		json_obj_2 = JSONTestClass.from_dict(dct_1)
		json_obj_3 = JSONTestClass.from_dict(dct_2)
		self.assertEqual(hash(json_obj_1), hash(json_obj_2))
		self.assertNotEqual(hash(json_obj_1), hash(json_obj_3))

	def test_eq(self):
		dct_1 = {"a": 1, "b": 1.2, "c": b'123', "d": "123", "e": True, "f": [1, 2, 3], "g": {"a": 1}}
		dct_2 = {"a": 2, "b": 1.2, "c": b'123', "d": "12333", "e": True, "f": [1, 2, 3], "g": {"a": 1}}
		json_obj_1 = JSONTestClass.from_dict(dct_1)
		json_obj_2 = JSONTestClass.from_dict(dct_1)
		json_obj_3 = JSONTestClass.from_dict(dct_2)
		self.assertNotEqual(json_obj_1, 1)
		self.assertNotEqual(json_obj_1, json_obj_3)
		self.assertEqual(json_obj_1, json_obj_2)


if __name__ == "__main__":
	unittest.main()
