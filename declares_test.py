import unittest
from datetime import datetime, timezone

from declares import var, Declared, NamingStyle, new_list_type


class QueryStringTestCase(unittest.TestCase):

    def test_simple_use(self):
        query_string = "crcat=test&crsource=test&crkw=buy-a-lot&crint=1&crfloat=1.2"

        class Example(Declared):
            crcat = var(str)
            crsource = var(str)
            crkw = var(str)
            crint = var(int)
            crfloat = var(float)

        example = Example.from_query_string(query_string)
        self.assertEqual(example.crint, 1)
        self.assertEqual(example.crfloat, 1.2)
        self.assertEqual(example.to_query_string(), query_string)


class FormDataTestCase(unittest.TestCase):

    def test_simple_use(self):
        form_data = "crcat=test&crsource=test&crkw=buy-a-lot&crint=1&crfloat=1.2"

        class Example(Declared):
            crcat = var(str)
            crsource = var(str)
            crkw = var(str)
            crint = var(int)
            crfloat = var(float)

        example = Example.from_form_data(form_data)
        self.assertEqual(example.crint, 1)
        self.assertEqual(example.crfloat, 1.2)
        self.assertEqual(example.to_form_data(), form_data)


class DeclaredXmlSerializeTestCase(unittest.TestCase):

    def test_simple_use(self):
        xml_string = """
        <?xml version="1.0" encoding="utf-8"?>
        <data>
            <country name="Liechtenstein">
                <rank>1</rank>
                <year>2008</year>
                <gdppc>141100</gdppc>
                <neighbor name="Austria" direction="E"/>
            </country>
            <country name="Singapore">
                <rank>4</rank>
                <year>2011</year>
                <gdppc>59900</gdppc>
                <neighbor name="Malaysia" direction="N"/>
            </country>
            <country name="Panama">
                <rank>68</rank>
                <year>2011</year>
                <gdppc>13600</gdppc>
                <neighbor name="Costa Rica" direction="W"/>
            </country>
        </data>
        """.strip()

        class Neighbor(Declared):
            name = var(str, as_xml_attr=True)
            direction = var(str, as_xml_attr=True)

        class Country(Declared):
            rank = var(str)
            year = var(int)
            gdppc = var(int)
            name = var(str, as_xml_attr=True)
            neighbor = var(Neighbor)

        Data = new_list_type(Country)
        data = Data.from_xml_string(xml_string)
        self.assertEqual(
            data.to_xml_bytes(skip_none_field=True).decode(),
            '<data><country name="Liechtenstein"><rank>1</rank><year>2008</year><gdppc>141100</gdppc><neighbor direction="E" name="Austria" /></country><country name="Singapore"><rank>4</rank><year>2011</year><gdppc>59900</gdppc><neighbor direction="N" name="Malaysia" /></country><country name="Panama"><rank>68</rank><year>2011</year><gdppc>13600</gdppc><neighbor direction="W" name="Costa Rica" /></country></data>'
        )
        self.assertEqual(
            data.to_json(),
            '[{"rank": "1", "year": 2008, "gdppc": 141100, "name": "Liechtenstein", "neighbor": {"name": "Austria", "direction": "E"}}, {"rank": "4", "year": 2011, "gdppc": 59900, "name": "Singapore", "neighbor": {"name": "Malaysia", "direction": "N"}}, {"rank": "68", "year": 2011, "gdppc": 13600, "name": "Panama", "neighbor": {"name": "Costa Rica", "direction": "W"}}]'
        )

    def test_other_simple_use(self):
        xml_string = """
        <?xml version="1.0" encoding="utf-8"?>
        <resources>
            <style name="AppTheme" parent="Theme.AppCompat.Light.DarkActionBar">
                <item name="colorPrimary">@color/colorPrimary</item>
                <item name="colorPrimaryDark">@color/colorPrimaryDark</item>
                <item name="colorAccent">@color/colorAccent</item>
            </style>

            <style name="AppTheme.NoActionBar">
                <item name="windowActionBar">false</item>
                <item name="windowNoTitle">true</item>
            </style>

            <style name="AppTheme.AppBarOverlay" parent="ThemeOverlay.AppCompat.Dark.ActionBar" />
            <style name="AppTheme.PopupOverlay" parent="ThemeOverlay.AppCompat.Light" />

            <style name="ratingBarStyle" parent="@android:style/Widget.RatingBar">
                <item name="android:progressDrawable">@drawable/ratingbar_drawable</item>
                <item name="android:minHeight">48dip</item>
                <item name="android:maxHeight">48dip</item>
            </style>
        </resources>
        """.strip()

        class Item(Declared):
            name = var(str, as_xml_attr=True)
            text = var(str, as_xml_text=True)

        class Style(Declared):
            name = var(str, as_xml_attr=True)
            parent = var(str, as_xml_attr=True, default=None)
            items = var(new_list_type(Item), field_name="item")

        Resource = new_list_type(Style)
        data = Resource.from_xml_string(xml_string)
        self.assertEqual(
            data.to_xml_bytes(skip_none_field=True).decode(),
            '<resources><style name="AppTheme" parent="Theme.AppCompat.Light.DarkActionBar"><item name="colorPrimary">@color/colorPrimary</item><item name="colorPrimaryDark">@color/colorPrimaryDark</item><item name="colorAccent">@color/colorAccent</item></style><style name="AppTheme.NoActionBar"><item name="windowActionBar">false</item><item name="windowNoTitle">true</item></style><style name="AppTheme.AppBarOverlay" parent="ThemeOverlay.AppCompat.Dark.ActionBar" /><style name="AppTheme.PopupOverlay" parent="ThemeOverlay.AppCompat.Light" /><style name="ratingBarStyle" parent="@android:style/Widget.RatingBar"><item name="android:progressDrawable">@drawable/ratingbar_drawable</item><item name="android:minHeight">48dip</item><item name="android:maxHeight">48dip</item></style></resources>'
        )
        self.assertEqual(
            data.to_json(),
            '[{"name": "AppTheme", "parent": "Theme.AppCompat.Light.DarkActionBar", "item": [{"name": "colorPrimary", "text": "@color/colorPrimary"}, {"name": "colorPrimaryDark", "text": "@color/colorPrimaryDark"}, {"name": "colorAccent", "text": "@color/colorAccent"}]}, {"name": "AppTheme.NoActionBar", "parent": null, "item": [{"name": "windowActionBar", "text": "false"}, {"name": "windowNoTitle", "text": "true"}]}, {"name": "AppTheme.AppBarOverlay", "parent": "ThemeOverlay.AppCompat.Dark.ActionBar", "item": []}, {"name": "AppTheme.PopupOverlay", "parent": "ThemeOverlay.AppCompat.Light", "item": []}, {"name": "ratingBarStyle", "parent": "@android:style/Widget.RatingBar", "item": [{"name": "android:progressDrawable", "text": "@drawable/ratingbar_drawable"}, {"name": "android:minHeight", "text": "48dip"}, {"name": "android:maxHeight", "text": "48dip"}]}]'
        )

    def test_declared_to_xml(self):
        xml_string = """
        <?xml version="1.0" encoding="utf-8"?>
        <person valid="true">
            <name>John</name>
            <age>18</age>
        </person>
        """.strip()

        class Person(Declared):
            valid = var(str, as_xml_attr=True)
            name = var(str)
            age = var(int)

        one_person = Person.from_xml_string(xml_string)
        self.assertEqual(one_person.name, "John")
        self.assertEqual(one_person.valid, "true")
        self.assertEqual(one_person.age, 18)
        self.assertEqual(one_person.to_xml_bytes().decode(),
                         '<person valid="true"><name>John</name><age>18</age></person>')
        self.assertEqual(one_person.to_json(), '{"valid": "true", "name": "John", "age": 18}')


class NamingStyleTestCase(unittest.TestCase):

    def test_snake_case(self):

        class Klass(Declared):
            test_var_a = var(int)

        struct = Klass(1)
        self.assertEqual(struct.to_dict(), {"test_var_a": 1})

        class Klass1(Declared):
            testVarB = var(int)

        struct = Klass1(1)
        self.assertEqual(struct.to_dict(), {"test_var_b": 1})

        class Klass3(Declared):
            TestVarD = var(int)

        struct = Klass3(1)
        self.assertEqual(struct.to_dict(), {"test_var_d": 1})

    def test_camel_case(self):

        class Klass(Declared):
            test_var_a = var(int, naming_style=NamingStyle.camelcase)

        struct = Klass(1)
        self.assertEqual(struct.to_dict(), {"testVarA": 1})

        class Klass1(Declared):
            testVarB = var(int, naming_style=NamingStyle.camelcase)

        struct = Klass(1)
        self.assertEqual(struct.to_dict(), {"testVarA": 1})

        class Klass3(Declared):
            TestVarD = var(int, naming_style=NamingStyle.camelcase)

        struct = Klass(1)
        self.assertEqual(struct.to_dict(), {"testVarA": 1})


class VarTestCase(unittest.TestCase):

    def test_post_init_case_1(self):
        class Klass(Declared):
            a = var(int)
            b = var(int)
            c = var(int, init=False)

            def __post_init__(self):
                self.c = self.a + self.b

        inst = Klass(1, 2)
        self.assertEqual(inst.a, 1)
        self.assertEqual(inst.b, 2)
        self.assertEqual(inst.c, 3)

    def test_post_init_case_2(self):
        class Klass(Declared):
            a = var(int)
            b = var(int)
            c = var(int, init=False)

            def __post_init__(self, c):
                self.c = c + 1

        inst = Klass(1, 2, 3)
        self.assertEqual(inst.a, 1)
        self.assertEqual(inst.b, 2)
        self.assertEqual(inst.c, 4)

    def test_post_init_case_3(self):
        class Klass(Declared):
            a = var(int)
            b = var(int)
            c = var(int, init=False, required=False)

            def __post_init__(self, c):
                self.c = c + 1

        inst = Klass(1, 2, 3)
        self.assertEqual(inst.a, 1)
        self.assertEqual(inst.b, 2)
        self.assertEqual(inst.c, 4)

    def test_post_init_case_4(self):
        class Klass(Declared):
            a = var(int)
            b = var(int)
            c = var(int, init=False, required=False)

            def __post_init__(self):
                self.c = self.a + self.b

        inst = Klass(1, 2)
        self.assertEqual(inst.a, 1)
        self.assertEqual(inst.b, 2)
        self.assertEqual(inst.c, 3)

    def test_default_params(self):

        class Klass(Declared):
            a = var(int)

        self.assertRaises(AttributeError, Klass)

        i1 = Klass(1)
        self.assertEqual(i1.a, 1)
        self.assertEqual(i1.to_json(), "{\"a\": 1}")
        self.assertEqual(i1.to_json(skip_none_field=True), "{\"a\": 1}")

        i1 = Klass(None)
        self.assertEqual(i1.a, None)
        self.assertEqual(i1.to_json(), "{\"a\": null}")
        self.assertEqual(i1.to_json(skip_none_field=True), "{}")

    def test_required(self):

        class Klass(Declared):
            a = var(int, required=False)

        i2 = Klass(1)
        self.assertEqual(i2.a, 1)
        self.assertEqual(i2.to_json(), "{\"a\": 1}")
        self.assertEqual(i2.to_json(skip_none_field=True), "{\"a\": 1}")

        i2 = Klass(None)
        self.assertEqual(i2.a, None)
        self.assertEqual(i2.to_json(), "{\"a\": null}")
        self.assertEqual(i2.to_json(skip_none_field=True), "{}")

    def test_ignore_serialize(self):

        class Klass(Declared):
            a = var(int, ignore_serialize=True)

        self.assertRaises(AttributeError, Klass)

        i3 = Klass(1)
        self.assertEqual(i3.a, 1)
        self.assertEqual(i3.to_json(), "{}")
        self.assertEqual(i3.to_json(skip_none_field=True), "{}")

        i3 = Klass(None)
        self.assertEqual(i3.a, None)
        self.assertEqual(i3.to_json(), "{}")
        self.assertEqual(i3.to_json(skip_none_field=True), "{}")

    def test_init(self):

        class Klass(Declared):
            a = var(int, init=False)

        i4 = Klass()
        self.assertEqual(i4.a, None)
        self.assertRaises(AttributeError, i4.to_json)
        i4.a = 1
        self.assertEqual(i4.a, 1)
        self.assertEqual(i4.to_json(), "{\"a\": 1}")
        self.assertEqual(i4.to_json(skip_none_field=True), "{\"a\": 1}")

        i4 = Klass(1)
        self.assertEqual(i4.a, None)
        self.assertRaises(AttributeError, i4.to_json)
        i4.a = 1
        self.assertEqual(i4.a, 1)
        self.assertEqual(i4.to_json(), "{\"a\": 1}")
        self.assertEqual(i4.to_json(skip_none_field=True), "{\"a\": 1}")

        i4 = Klass(None)
        self.assertEqual(i4.a, None)
        self.assertRaises(AttributeError, i4.to_json)
        self.assertRaises(AttributeError, i4.to_json, skip_none_field=True)

    def test_default(self):

        class Klass(Declared):
            a = var(int, default=10)

        i5 = Klass()
        self.assertEqual(i5.a, 10)
        self.assertEqual(i5.to_json(), "{\"a\": 10}")
        self.assertEqual(i5.to_json(skip_none_field=True), "{\"a\": 10}")

        i5 = Klass(1)
        self.assertEqual(i5.a, 1)
        self.assertEqual(i5.to_json(), "{\"a\": 1}")
        self.assertEqual(i5.to_json(skip_none_field=True), "{\"a\": 1}")

        i5 = Klass(None)
        self.assertEqual(i5.a, None)
        self.assertEqual(i5.to_json(), "{\"a\": null}")
        self.assertEqual(i5.to_json(skip_none_field=True), "{}")

    def test_default_factory(self):

        class Klass(Declared):
            a = var(int, default_factory=lambda: 10)

        i6 = Klass()
        self.assertEqual(i6.a, 10)
        self.assertEqual(i6.to_json(), "{\"a\": 10}")
        self.assertEqual(i6.to_json(skip_none_field=True), "{\"a\": 10}")

        i6 = Klass(1)
        self.assertEqual(i6.a, 1)
        self.assertEqual(i6.to_json(), "{\"a\": 1}")
        self.assertEqual(i6.to_json(skip_none_field=True), "{\"a\": 1}")

        i6 = Klass(None)
        self.assertEqual(i6.a, None)
        self.assertEqual(i6.to_json(), "{\"a\": null}")
        self.assertEqual(i6.to_json(skip_none_field=True), "{}")

    def test_field_name(self):

        class Klass(Declared):
            a = var(int, field_name="aa")

        self.assertRaises(AttributeError, Klass)

        i7 = Klass(1)
        self.assertEqual(i7.a, 1)
        self.assertEqual(i7.to_json(), "{\"aa\": 1}")
        self.assertEqual(i7.to_json(skip_none_field=True), "{\"aa\": 1}")

        i7 = Klass(None)
        self.assertEqual(i7.a, None)
        self.assertEqual(i7.to_json(), "{\"aa\": null}")
        self.assertEqual(i7.to_json(skip_none_field=True), "{}")


class ComplexVarTestCase(unittest.TestCase):

    def test_required_init(self):

        class Klass(Declared):
            a = var(int, required=False, init=False)

        i1 = Klass()
        self.assertEqual(i1.a, None)
        self.assertEqual(i1.to_json(), "{\"a\": null}")
        self.assertEqual(i1.to_json(skip_none_field=True), "{}")

        i1 = Klass(1)
        self.assertEqual(i1.a, None)
        self.assertEqual(i1.to_json(), "{\"a\": null}")
        self.assertEqual(i1.to_json(skip_none_field=True), "{}")

        i1 = Klass(1)
        i1.a = 10
        self.assertEqual(i1.a, 10)
        self.assertEqual(i1.to_json(), "{\"a\": 10}")
        self.assertEqual(i1.to_json(skip_none_field=True), "{\"a\": 10}")

        i1 = Klass(None)
        self.assertEqual(i1.a, None)
        self.assertEqual(i1.to_json(), "{\"a\": null}")
        self.assertEqual(i1.to_json(skip_none_field=True), "{}")

    def test_required_ignore_serialize(self):

        class Klass(Declared):
            a = var(int, required=False, ignore_serialize=True)

        i2 = Klass(1)
        self.assertEqual(i2.a, 1)
        self.assertEqual(i2.to_json(), "{}")
        self.assertEqual(i2.to_json(skip_none_field=True), "{}")

        i2 = Klass(None)
        self.assertEqual(i2.a, None)
        self.assertEqual(i2.to_json(), "{}")
        self.assertEqual(i2.to_json(skip_none_field=True), "{}")

    def test_required_init_ignore_serialize(self):
        """"""

        class Klass(Declared):
            a = var(int, required=False, init=False, ignore_serialize=True)

        i3 = Klass()
        self.assertEqual(i3.a, None)
        self.assertEqual(i3.to_json(), "{}")
        self.assertEqual(i3.to_json(skip_none_field=True), "{}")

        i3 = Klass()
        i3.a = 1
        self.assertEqual(i3.a, 1)
        self.assertEqual(i3.to_json(), "{}")
        self.assertEqual(i3.to_json(skip_none_field=True), "{}")

        i3 = Klass(1)
        self.assertEqual(i3.a, None)
        self.assertEqual(i3.to_json(), "{}")
        self.assertEqual(i3.to_json(skip_none_field=True), "{}")

        i3 = Klass(None)
        self.assertEqual(i3.a, None)
        self.assertEqual(i3.to_json(), "{}")
        self.assertEqual(i3.to_json(skip_none_field=True), "{}")

    def test_default_default_factory(self):
        """"""
        self.assertRaises(ValueError, var, int, default="aa", default_factory=lambda: 10)


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

    def setUp(self):
        tz = datetime.now(timezone.utc).astimezone().tzinfo
        self.timestamp = 1564758694.8669891
        self.dt = datetime.fromtimestamp(self.timestamp, tz=tz)

    def test_str(self):
        json_obj = NewVarJsonTestClass(1, 2, self.dt)
        self.assertEqual(str(json_obj), "NewVarJsonTestClass(a=1,b=2,c=2019-08-02 23:11:34.866989+08:00)")

    def test_to_dict(self):
        json_obj = NewVarJsonTestClass(1, 2, self.dt)
        self.assertEqual(json_obj.to_dict(), {"na": 1, "nb": 2, "c": self.dt})

    def test_to_json(self):
        json_obj = NewVarJsonTestClass(1, 2, self.dt)
        self.assertEqual(json_obj.to_json(), "{\"na\": 1, \"nb\": 2, \"c\": %f}" % self.timestamp)

    def test_from_dict(self):
        dct = {"na": 1, "nb": 2, "c": self.dt}
        json_obj = NewVarJsonTestClass.from_dict(dct)
        self.assertEqual(str(json_obj), "NewVarJsonTestClass(a=1,b=2,c=2019-08-02 23:11:34.866989+08:00)")

    def test_hash(self):
        dct_1 = {"na": 1, "nb": 2, "c": self.dt}
        dct_2 = {"na": 2, "nb": 1, "c": self.dt}
        json_obj_1 = NewVarJsonTestClass.from_dict(dct_1)
        json_obj_2 = NewVarJsonTestClass.from_dict(dct_1)
        json_obj_3 = NewVarJsonTestClass.from_dict(dct_2)
        self.assertEqual(hash(json_obj_1), hash(json_obj_2))
        self.assertNotEqual(hash(json_obj_1), hash(json_obj_3))

    def test_eq(self):
        dct_1 = {"na": 1, "nb": 2, "c": self.dt}
        dct_2 = {"na": 2, "nb": 1, "c": self.dt}
        json_obj_1 = NewVarJsonTestClass.from_dict(dct_1)
        json_obj_2 = NewVarJsonTestClass.from_dict(dct_1)
        json_obj_3 = NewVarJsonTestClass.from_dict(dct_2)
        self.assertNotEqual(json_obj_1, 1)
        self.assertEqual(json_obj_1, json_obj_2)
        self.assertNotEqual(json_obj_1, json_obj_3)


class CombineDeclaredTestCase(unittest.TestCase):

    def test_str(self):
        json_obj = CombineJSONTestClass(1, "123", JSONTestClass(1, 1.2, b"123", "123", True, [1, 2, 3], {"a": 1}))
        self.assertEqual(
            str(json_obj),
            "CombineJSONTestClass(a=1,b=123,json=JSONTestClass(a=1,b=1.2,c=b'123',d=123,e=True,f=[1, 2, 3],g={'a': 1}))"
        )

    def test_to_dict(self):
        json_obj = CombineJSONTestClass(1, "123", JSONTestClass(1, 1.2, b"123", "123", True, [1, 2, 3], {"a": 1}))
        self.assertEqual(
            json_obj.to_dict(), {
                "a": 1,
                "b": "123",
                "json": {
                    "a": 1,
                    "b": 1.2,
                    "c": [49, 50, 51],
                    "d": "123",
                    "e": True,
                    "f": [1, 2, 3],
                    "g": {
                        "a": 1
                    }
                }
            })

    def test_to_json(self):
        json_obj = CombineJSONTestClass(1, "123", JSONTestClass(1, 1.2, b"123", "123", True, [1, 2, 3], {"a": 1}))
        self.assertEqual(
            json_obj.to_json(),
            "{\"a\": 1, \"b\": \"123\", \"json\": {\"a\": 1, \"b\": 1.2, \"c\": [49, 50, 51], \"d\": \"123\", \"e\": true, \"f\": [1, 2, 3], \"g\": {\"a\": 1}}}"
        )

    def test_from_dict(self):
        dct = {
            "a": 1,
            "b": "123",
            "json": {
                "a": 1,
                "b": 1.2,
                "c": b'123',
                "d": "123",
                "e": True,
                "f": [1, 2, 3],
                "g": {
                    "a": 1
                }
            }
        }
        json_obj = CombineJSONTestClass.from_dict(dct)
        self.assertEqual(
            str(json_obj),
            "CombineJSONTestClass(a=1,b=123,json=JSONTestClass(a=1,b=1.2,c=b'123',d=123,e=True,f=[1, 2, 3],g={'a': 1}))"
        )

    def test_hash(self):
        dct_1 = {
            "a": 1,
            "b": "123",
            "json": {
                "a": 1,
                "b": 1.2,
                "c": b'123',
                "d": "123",
                "e": True,
                "f": [1, 2, 3],
                "g": {
                    "a": 1
                }
            }
        }
        dct_2 = {
            "a": 12,
            "b": "21123",
            "json": {
                "a": 1,
                "b": 2.2,
                "c": b'123',
                "d": "123",
                "e": True,
                "f": [1, 2, 3],
                "g": {
                    "a": 1
                }
            }
        }
        json_obj_1 = CombineJSONTestClass.from_dict(dct_1)
        json_obj_2 = CombineJSONTestClass.from_dict(dct_1)
        json_obj_3 = CombineJSONTestClass.from_dict(dct_2)
        self.assertEqual(hash(json_obj_1), hash(json_obj_2))
        self.assertNotEqual(hash(json_obj_1), hash(json_obj_3))

    def test_eq(self):
        dct_1 = {
            "a": 1,
            "b": "123",
            "json": {
                "a": 1,
                "b": 1.2,
                "c": b'123',
                "d": "123",
                "e": True,
                "f": [1, 2, 3],
                "g": {
                    "a": 1
                }
            }
        }
        dct_2 = {
            "a": 12,
            "b": "21123",
            "json": {
                "a": 1,
                "b": 2.2,
                "c": b'123',
                "d": "123",
                "e": True,
                "f": [1, 2, 3],
                "g": {
                    "a": 1
                }
            }
        }
        json_obj_1 = CombineJSONTestClass.from_dict(dct_1)
        json_obj_2 = CombineJSONTestClass.from_dict(dct_1)
        json_obj_3 = CombineJSONTestClass.from_dict(dct_2)
        self.assertNotEqual(json_obj_1, 1)
        self.assertEqual(json_obj_1, json_obj_2)
        self.assertNotEqual(json_obj_1, json_obj_3)


class InheritedDeclaredTestCase(unittest.TestCase):

    def test_str(self):
        json_obj = InheritedJSONTestClass(1, 1.2, b"123", "123", True, [1, 2, 3], {"a": 1}, 10, 11, 100)
        self.assertEqual(
            str(json_obj),
            "InheritedJSONTestClass(a=1,b=1.2,c=b'123',d=123,e=True,f=[1, 2, 3],g={'a': 1},ia=10,ib=11,iia=100)")

    def test_to_dict(self):
        json_obj = InheritedJSONTestClass(1, 1.2, b"123", "123", True, [1, 2, 3], {"a": 1}, 10, 11, 100)
        self.assertEqual(
            json_obj.to_dict(), {
                "iia": 100,
                "a": 1,
                "b": 1.2,
                "c": [49, 50, 51],
                "d": "123",
                "e": True,
                "f": [1, 2, 3],
                "g": {
                    "a": 1
                },
                "ia": 10,
                "ib": 11
            })

    def test_to_json(self):
        json_obj = InheritedJSONTestClass(1, 1.2, b"123", "123", True, [1, 2, 3], {"a": 1}, 10, 11, 100)
        self.assertEqual(
            json_obj.to_json(),
            "{\"a\": 1, \"b\": 1.2, \"c\": [49, 50, 51], \"d\": \"123\", \"e\": true, \"f\": [1, 2, 3], \"g\": {\"a\": 1}, \"ia\": 10, \"ib\": 11, \"iia\": 100}"
        )

    def test_from_dict(self):
        dct = {
            "iia": 100,
            "a": 1,
            "b": 1.2,
            "c": b'123',
            "d": "123",
            "e": True,
            "f": [1, 2, 3],
            "g": {
                "a": 1
            },
            "ia": 10,
            "ib": 11
        }
        json_obj = InheritedJSONTestClass.from_dict(dct)
        self.assertEqual(
            str(json_obj),
            "InheritedJSONTestClass(a=1,b=1.2,c=b'123',d=123,e=True,f=[1, 2, 3],g={'a': 1},ia=10,ib=11,iia=100)")

    def test_hash(self):
        dct_1 = {
            "iia": 100,
            "a": 1,
            "b": 1.2,
            "c": b'123',
            "d": "123",
            "e": True,
            "f": [1, 2, 3],
            "g": {
                "a": 1
            },
            "ia": 10,
            "ib": 11
        }
        dct_2 = {
            "iia": 11,
            "a": 12,
            "b": 1.2,
            "c": b'123',
            "d": "1123",
            "e": True,
            "f": [1, 2, 3],
            "g": {
                "a": 1
            },
            "ia": 10,
            "ib": 11
        }
        json_obj_1 = InheritedJSONTestClass.from_dict(dct_1)
        json_obj_2 = InheritedJSONTestClass.from_dict(dct_1)
        json_obj_3 = InheritedJSONTestClass.from_dict(dct_2)
        self.assertEqual(hash(json_obj_1), hash(json_obj_2))
        self.assertNotEqual(hash(json_obj_1), hash(json_obj_3))

    def test_eq(self):
        dct_1 = {
            "iia": 100,
            "a": 1,
            "b": 1.2,
            "c": b'123',
            "d": "123",
            "e": True,
            "f": [1, 2, 3],
            "g": {
                "a": 1
            },
            "ia": 10,
            "ib": 11
        }
        dct_2 = {
            "iia": 11,
            "a": 12,
            "b": 1.2,
            "c": b'123',
            "d": "1123",
            "e": True,
            "f": [1, 2, 3],
            "g": {
                "a": 1
            },
            "ia": 10,
            "ib": 11
        }
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

        class ITestJsonClass(Declared):
            a = var(int)
            b = var(int)
            c = var(int, required=False)

        json_obj = JSONTestClass(1, 1.2, b"123", "123", True, [1, 2, 3], {"a": 1})
        self.assertEqual(json_obj.to_dict(), {
            "a": 1,
            "b": 1.2,
            "c": [49, 50, 51],
            "d": "123",
            "e": True,
            "f": [1, 2, 3],
            "g": {
                "a": 1
            }
        })
        json_obj_1 = ITestJsonClass(a=1, b=1, c=2)
        self.assertRaises(AttributeError, JSONTestClass, a=1, b=1.2, f=[1, 2, 3])
        self.assertEqual(json_obj_1.to_dict(skip_none_field=True), {"a": 1, "b": 1, "c": 2})
        self.assertEqual(json_obj_1.to_dict(), {"a": 1, "b": 1, "c": 2})

    def test_to_json(self):
        json_obj = JSONTestClass(1, 1.2, b"123", "123", True, [1, 2, 3], {"a": 1})
        self.assertEqual(
            json_obj.to_json(),
            "{\"a\": 1, \"b\": 1.2, \"c\": [49, 50, 51], \"d\": \"123\", \"e\": true, \"f\": [1, 2, 3], \"g\": {\"a\": 1}}"
        )

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
