import copy
import inspect
import json
import re
import urllib.parse as urlparse
from collections import UserList
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import (Any, Callable, Collection, Dict, List, Mapping, Optional, Tuple, Type, Union)
from uuid import UUID
from xml.etree import ElementTree as ET

_REGISTER_DECLARED_CLASS: Dict[str, type] = {}


class _MISSING_TYPE:

    def __str__(self):
        return "MISSING"


MISSING = _MISSING_TYPE()
CDATA_PATTERN = re.compile(r"<!\[CDATA\[(.*?)\]\]>")
Json: Type[Any] = Union[dict, list, str, int, float, bool, None]
JsonData = Union[str, bytes, bytearray]


def custom_escape_cdata(text):
    if not _isinstance_safe(text, str):
        text = str(text)

    if CDATA_PATTERN.match(text):
        return text
    return ET_escape_cdata(text)


ET_escape_cdata = ET._escape_cdata
ET._escape_cdata = custom_escape_cdata


class _ExtendedEncoder(json.JSONEncoder):

    def default(self, o):
        result: Json
        if _isinstance_safe(o, Collection):
            if _isinstance_safe(o, Mapping):
                result = dict(o)
            else:
                result = list(o)
        elif _isinstance_safe(o, datetime):
            result = o.timestamp()
        elif _isinstance_safe(o, UUID):
            result = str(o)
        elif _isinstance_safe(o, Enum):
            result = o.value
        elif _isinstance_safe(o, Decimal):
            result = str(o)
        else:
            result = json.JSONEncoder.default(self, o)
        return result


class NamingStyle:
    """ reference to python-stringcase

    https://github.com/okunishinishi/python-stringcase
    """

    @classmethod
    def camelcase(cls, string):
        string = re.sub(r"^[\-_\.]", '', str(string))
        if not string:
            return string
        return string[0].lower() + re.sub(r"[\-_\.\s]([a-z])", lambda matched: (matched.group(1)).upper(), string[1:])

    @classmethod
    def snakecase(cls, string):
        string = re.sub(r"[\-\.\s]", '_', str(string))
        if not string:
            return string
        return string[0].lower() + re.sub(r"[A-Z]", lambda matched: '_' + (matched.group(0)).lower(), string[1:])


class Var:
    """ a represantation of declared class member varaiable
    recommend use var function to create Var object, don't use this construct directly
    """

    def __init__(self,
                 type_,
                 required=True,
                 field_name=MISSING,
                 default=MISSING,
                 default_factory=MISSING,
                 ignore_serialize=False,
                 naming_style=NamingStyle.snakecase,
                 as_xml_attr=False,
                 as_xml_text=False,
                 auto_cast=True,
                 init=True):
        self._type = type_
        self.name = ""
        self._field_name = field_name
        self.default = default
        self.default_factory = default_factory
        self.required = required
        self.init = init
        self.ignore_serialize = ignore_serialize
        self.naming_style = naming_style
        self.auto_cast = auto_cast

        self.as_xml_attr = as_xml_attr
        self.as_xml_text = as_xml_text

    @property
    def field_name(self):
        """ Cache handled field raw name """
        if self._field_name is MISSING:
            self._field_name = self.naming_style(self.name)
        return self._field_name

    @property
    def type_(self):
        if type(self._type) is str:
            self._type = _REGISTER_DECLARED_CLASS[self._type]
        return self._type

    def make_default(self):
        field_value = MISSING
        if self.default is not MISSING:
            field_value = self.default
        elif self.default_factory is not MISSING:
            field_value = self.default_factory()

        if self.check(field_value):
            return field_value
        return MISSING

    def check(self, obj):
        if obj is MISSING or obj is None:
            return True
        type_ = self.type_
        if getattr(type_, "__origin__", None):
            type_ = type_.__origin__

        if not _isinstance_safe(obj, type_):
            raise TypeError("%r is not a instance of %r" % (type(obj).__name__, self.type_.__name__))
        return True


def var(type_,
        required=True,
        field_name=MISSING,
        default=MISSING,
        default_factory=MISSING,
        ignore_serialize=False,
        naming_style=NamingStyle.snakecase,
        as_xml_attr=False,
        as_xml_text=False,
        auto_cast=True,
        init=True):
    """ check input arguments and create a Var object

    Usage:
        >>> class NewClass(Declared):
        >>>     new_field = var(int)
        >>>     another_new_field = var(str, field_name="anf")

    :param type_: a type object, or a str object that express one class of imported or declared in later,
                  if use not declared or not imported class by string, a TypeError will occur in object
                  construct or set attribute to those objects.

    :param required: a bool object, constructor, this variable can't be missing in serialize when it is True.
                     on the other hand, this variable will be set None as default if `required` is False.

    :param field_name: a str object, use to serialize or deserialize custom field name.

    :param default: a Type[A] object, raise AttributeError when this field leak user input value but
                    this value is not instance of Type.

    :param default_factory: a callable object that can return a Type[A] object, as same as default parameter
                            but it is more flexible.

    :param ignore_serialize: a bool object, if it is True then will omit in serialize.

    :param init: a bool object, the parameter determines whether this variable will be initialize by default initializer.
                 if it is False, then do not initialize with default initializer for this variable, and you must set attribute
                 in other place otherwise there are AttributeError raised in serializing.
    """
    if default is not MISSING and default_factory is not MISSING:
        raise ValueError('cannot specify both default and default_factory')
    if _isinstance_safe(naming_style, NamingStyle):
        raise TypeError(f'{type(naming_style)!r} is not instance of {NamingStyle!r}.')
    return Var(type_, required, field_name, default, default_factory, ignore_serialize, naming_style, as_xml_attr,
               as_xml_text, auto_cast, init)


class BaseDeclared(type):

    def __new__(cls, name, bases, attrs):
        if name == "Declared":
            return super(BaseDeclared, cls).__new__(cls, name, bases, attrs)

        fields = []
        meta_vars = {}
        for base in bases:
            meta = getattr(base, "meta", None)
            if meta:
                base_meta_vars = meta.get("vars", {})
                meta_vars.update(base_meta_vars)
                fields.extend(base_meta_vars.keys())

            for k, v in base.__dict__.items():
                if _isinstance_safe(v, Var):
                    fields.append(k)
                    var = v
                    var.name = k
                    meta_vars[k] = var

        for key in list(attrs.keys()):
            if isinstance(attrs[key], Var):
                if key not in fields:
                    fields.append(key)
                var = attrs.pop(key)
                var.name = key
                meta_vars[key] = var

        meta = {"vars": meta_vars}
        new_cls = super(BaseDeclared, cls).__new__(cls, name, bases, attrs)
        _REGISTER_DECLARED_CLASS[name] = new_cls
        new_cls.add_attribute("fields", tuple(fields))
        new_cls.add_attribute("meta", meta)
        new_cls.add_attribute("__annotations__", meta_vars)
        return new_cls

    def add_attribute(cls, name, attr):
        setattr(cls, name, attr)


class Declared(metaclass=BaseDeclared):
    """ declared a serialize object make data class more clearly and flexible, provide
    default serialize function and well behavior hash, str and eq.
    fields can use None object represent null or empty situation, otherwise those fields
    must be provided unless set it required as False.
    """

    def __init__(self, *args, **kwargs):
        kwargs.update(dict(zip(self.fields, args)))
        fs = fields(self)
        for field in fs:
            # set `init` to False but `required` is True, that mean is this variable must be init in later
            # otherwise seiralize will be failed.
            # `init` just tell Declared class use custom initializer instead of default initializer.
            if not field.init:
                continue

            field_value = kwargs.get(field.name, MISSING)

            if field_value is MISSING:
                field_value = field.make_default()
                if field_value is MISSING:
                    raise AttributeError(
                        f"field {field.name!r} is required. if you doesn't want to init this variable in initializer, "
                        f"please set `init` argument to False for this variable.")
            super().__setattr__(field.name, field_value)

        self.__post_init__()

    def __post_init__(self):
        """"""

    def __setattr__(self, name, value):
        if name in self.fields:
            self.meta["vars"][name].check(value)
        super().__setattr__(name, value)

    def __getattr__(self, name):
        try:
            result = self.__getattribute__(name)
            if result is MISSING:
                return None
            return result
        except AttributeError as why:
            try:
                meta_var = self.meta["vars"][name]
            except KeyError:
                raise why
            else:
                value = meta_var.make_default()
                if value is MISSING:
                    return None
                else:
                    super().__setattr__(name, value)
                    return value

    @classmethod
    def has_nest_declared_class(cls):
        _has_nest_declared_class = getattr(cls, "_has_nest_declared_class", None)
        if _has_nest_declared_class is None:
            result = False
            for field in fields(cls):
                if _is_declared_instance(field.type_):
                    result = True
                    break
            setattr(cls, "_has_nest_declared_class", result)
        else:
            return _has_nest_declared_class

    def to_json(self,
                skipkeys: bool = False,
                ensure_ascii: bool = True,
                check_circular: bool = True,
                allow_nan: bool = True,
                indent: Optional[Union[int, str]] = None,
                separators: Tuple[str, str] = None,
                default: Callable = None,
                sort_keys: bool = False,
                skip_none_field=False,
                **kw):
        return json.dumps(
            self.to_dict(encode_json=False, skip_none_field=skip_none_field),
            cls=_ExtendedEncoder,
            skipkeys=skipkeys,
            ensure_ascii=ensure_ascii,
            check_circular=check_circular,
            allow_nan=allow_nan,
            indent=indent,
            separators=separators,
            default=default,
            sort_keys=sort_keys,
            **kw)

    @classmethod
    def from_json(cls: Type['Declared'],
                  s: JsonData,
                  *,
                  encoding=None,
                  parse_float=None,
                  parse_int=None,
                  parse_constant=None,
                  **kw):
        kvs = json.loads(
            s, encoding=encoding, parse_float=parse_float, parse_int=parse_int, parse_constant=parse_constant, **kw)
        return cls.from_dict(kvs)

    @classmethod
    def from_dict(cls: Type['Declared'], kvs: dict):
        return _decode_dict_to_declared_class(cls, kvs)

    def to_dict(self, encode_json=False, skip_none_field=False):
        return _asdict(self, encode_json=encode_json, skip_none_field=skip_none_field)

    @classmethod
    def from_form_data(cls: Type['Declared'], form_data):
        if cls.has_nest_declared_class():
            raise ValueError("can't deserialize to nested declared class.")

        return cls.from_dict(dict(d.split("=") for d in form_data.split("&")))

    def to_form_data(self, skip_none_field=False):
        if self.has_nest_declared_class():
            raise ValueError("can't serialize with nested declared class.")

        return "&".join([f"{k}={v}" for k, v in self.to_dict(skip_none_field=skip_none_field).items()])

    @classmethod
    def from_query_string(cls: Type['Declared'], query_string: str):
        if cls.has_nest_declared_class():
            raise ValueError("can't deserialize to nested declared class.")

        return cls.from_dict(dict(d.split("=") for d in urlparse.unquote(query_string).split("&")))

    def to_query_string(self,
                        skip_none_field=False,
                        doseq=False,
                        safe='',
                        encoding=None,
                        errors=None,
                        quote_via=urlparse.quote_plus):
        if self.has_nest_declared_class():
            raise ValueError("can't deserialize to nested declared class.")

        return urlparse.urlencode(
            self.to_dict(skip_none_field=skip_none_field),
            doseq=doseq,
            safe=safe,
            encoding=encoding,
            errors=errors,
            quote_via=quote_via)

    @classmethod
    def from_xml(cls: Type['Declared'], element: ET.Element) -> ET.Element:
        """
        >>> class Struct(Declared):
        >>>     tag = var(str)
        >>>     text = var(str)
        >>>     children = var(str)

        >>>     # attrs
        >>>     id = var(str)
        >>>     style = var(str)
        >>>     ......
        """
        return _decode_xml_to_declared_class(cls, element)

    @classmethod
    def from_xml_string(cls: Type['Declared'], xml_string) -> ET.Element:
        return cls.from_xml(ET.XML(xml_string))

    def to_xml(self, skip_none_field: bool = False) -> ET.Element:
        """
        <?xml version="1.0"?>
        <tag id="`id`" style="`style`">
            `text`
        </tag>
        """
        # TODO
        attr = {}
        text = ""
        children = []
        for field in fields(self):
            if field.as_xml_attr:
                new_attr = getattr(self, field.name, None)
                if new_attr:
                    attr[field.field_name] = new_attr
            elif field.as_xml_text:
                text = getattr(self, field.name, "")
            elif _issubclass_safe(field.type_, GenericList):
                children.extend((sub.to_xml(skip_none_field) for sub in getattr(self, field.name, ())))
            else:
                elem = getattr(self, field.name, MISSING)
                if elem is not MISSING:
                    children.append(elem.to_xml(skip_none_field))

        new_element = ET.Element(field.field_name, attr)
        new_element.text = text
        for c in children:
            new_element.append(c)
        return new_element

    def to_xml_string(self, skip_none_field: bool = False) -> str:
        return ET.tostring(self.to_xml(skip_none_field))

    def _extract_attrs(self, skip_none_field: bool) -> Tuple[Dict, Dict]:
        dct = self.to_dict(skip_none_field=skip_none_field)
        attrs = {}
        others = {}
        attr_field_names = tuple(f.field_name for f in fields(self) if f.as_xml_attr)
        for k, v in dct.items():
            if k in attr_field_names:
                attrs[k] = v
            else:
                others[k] = v
        return attrs, others

    def __str__(self):
        args = [f"{var.name}={str(getattr(self, var.name, 'missing'))}" for _, var in self.meta["vars"].items()]
        return f"{self.__class__.__name__}({','.join(args)})"

    def __eq__(self, other):
        if other.__class__ != self.__class__:
            return False

        for field_name in self.fields:
            field_value_self = getattr(self, field_name, MISSING)
            field_value_other = getattr(other, field_name, MISSING)
            if field_value_self != field_value_other:
                return False
        return True

    def __hash__(self):
        return hash(tuple(str(getattr(self, f.name)) for f in fields(self)))


class GenericList(UserList):
    """ represant a series of vars

    >>> class NewType(Declared):
    >>>     items = var(new_list_type(str))

    >>> result = NewType.from_json("{\"items\": [\"1\", \"2\"]}")
    >>> result.to_json() #  {\"items\": [\"1\", \"2\"]}

    or used directly

    >>> strings = new_list_type(str)
    >>> result = strings.from_json("[\"1\", \"2\"]")
    >>> result.to_json() #  "[\"1\", \"2\"]"
    """

    __type__ = None

    def __init__(self, initlist: List = None, tag: str = None):
        if self.__type__ is None:
            raise TypeError(
                f"Type {self.__class__.__name__} cannot be intialize directly; please use new_list_type instead")

        super().__init__(initlist)
        # type checked
        for item in self.data:
            if type(item) is not self.__type__:
                raise TypeError(f"Type of instance {str(item)} is {type(item)}, but not {self.__type__}.")
        self.tag = tag

    @classmethod
    def from_json(cls: Type['GenericList'],
                  s: JsonData,
                  *,
                  encoding=None,
                  parse_float=None,
                  parse_int=None,
                  parse_constant=None,
                  **kw) -> 'GenericList':
        kvs = json.loads(
            s, encoding=encoding, parse_float=parse_float, parse_int=parse_int, parse_constant=parse_constant, **kw)
        return cls(kvs)

    def to_json(self,
                skipkeys: bool = False,
                ensure_ascii: bool = True,
                check_circular: bool = True,
                allow_nan: bool = True,
                indent: Optional[Union[int, str]] = None,
                separators: Tuple[str, str] = None,
                default: Callable = None,
                sort_keys: bool = False,
                skip_none_field=False,
                **kw) -> JsonData:
        return json.dumps([inst.to_dict(encode_json=False, skip_none_field=skip_none_field) for inst in self.data],
                          cls=_ExtendedEncoder,
                          skipkeys=skipkeys,
                          ensure_ascii=ensure_ascii,
                          check_circular=check_circular,
                          allow_nan=allow_nan,
                          indent=indent,
                          separators=separators,
                          default=default,
                          sort_keys=sort_keys,
                          **kw)

    @classmethod
    def from_xml(cls: Type['GenericList'], element: ET.Element) -> 'GenericList':
        return cls((cls.__type__.from_xml(sub) for sub in element), tag=element.tag)

    @classmethod
    def from_xml_string(cls: Type['GenericList'], xml_string) -> 'GenericList':
        return cls.from_xml(ET.XML(xml_string))

    def to_xml(self, tag: str = None, skip_none_field: bool = False) -> ET.Element:
        if tag is None:
            tag = self.tag
        root = ET.Element(tag)
        for item in self:
            root.append(item.to_xml(skip_none_field=skip_none_field))
        return root

    def to_xml_string(self, tag: str = None, skip_none_field: bool = False) -> str:
        return ET.tostring(self.to_xml(tag, skip_none_field))

    def __str__(self):
        return f"{self.__class__.__name__}({', '.join(str(i) for i in self)})"


__created_list_types: Dict[Type, GenericList] = {}


def new_list_type(type_: Type) -> GenericList:
    if type_ in __created_list_types:
        return __created_list_types[type_]
    cls = type(f"GenericList<{type_.__name__}>", (GenericList,), {"__type__": type_})
    __created_list_types[type_] = cls
    return cls


def _tuple_str(obj_name, fields):
    # Return a string representing each field of obj_name as a tuple
    # member.  So, if fields is ['x', 'y'] and obj_name is "self",
    # return "(self.x,self.y)".

    # Special case for the 0-tuple.
    if not fields:
        return '()'
    # Note the trailing comma, needed if this turns out to be a 1-tuple.
    return f'({",".join([f"{obj_name}.{f.name}" for f in fields])},)'


def _isinstance_safe(o, t):
    try:
        result = isinstance(o, t)
    except Exception:
        return False
    else:
        return result


def _issubclass_safe(cls, classinfo):
    try:
        return issubclass(cls, classinfo)
    except Exception:
        return (_is_new_type_subclass_safe(cls, classinfo) if _is_new_type(cls) else False)


def _is_new_type_subclass_safe(cls, classinfo):
    super_type = getattr(cls, "__supertype__", None)

    if super_type:
        return _is_new_type_subclass_safe(super_type, classinfo)

    try:
        return issubclass(cls, classinfo)
    except Exception:
        return False


def _is_new_type(type_):
    return inspect.isfunction(type_) and hasattr(type_, "__supertype__")


def _decode_xml_to_declared_class(cls: Type[Declared], element: ET.Element) -> Declared:
    init_kwargs: Dict[str, Any] = {}
    for field in fields(cls):
        if field.as_xml_attr:
            field_value = element.get(field.field_name, MISSING)
        elif field.as_xml_text:
            field_value = element.text
        elif _issubclass_safe(field.type_, GenericList):
            field_value = (field.type_.__type__.from_xml(sub) for sub in element)
        else:
            field_value = _decode_xml_to_declared_class(field.type_, element.find(field.field_name))
        init_kwargs[field.name] = _cast_field_value(field, field_value)
    return cls(**init_kwargs)


def _decode_dict_to_declared_class(cls: Type[Declared], kvs: Union['List', 'Dict']):
    if _isinstance_safe(kvs, cls):
        return kvs

    if not kvs:
        if _issubclass_safe(cls, Declared):
            return cls.__new__(cls)
        return cls()

    init_kwargs: Dict[str, Any] = {}
    for field in fields(cls):
        field_value = kvs.get(field.field_name, MISSING)
        if field_value is MISSING:
            field_value = field.make_default()

        init_kwargs[field.name] = _cast_field_value(field, field_value)

    return cls(**init_kwargs)


def _cast_field_value(field: Var, field_value: Any):
    if field_value is MISSING:
        return field_value

    if _issubclass_safe(field.type_, Declared):
        value = _decode_dict_to_declared_class(field.type_, field_value)
    elif _issubclass_safe(field.type_, Decimal):
        value = field_value if isinstance(field_value, Decimal) else Decimal(field_value)
    elif _issubclass_safe(field.type_, UUID):
        value = field_value if isinstance(field_value, UUID) else UUID(field_value)
    elif _issubclass_safe(field.type_, datetime):
        if _isinstance_safe(field_value, datetime):
            dt = field_value
        else:
            tz = datetime.now(timezone.utc).astimezone().tzinfo
            dt = datetime.fromtimestamp(field_value, tz=tz)
        value = dt
    elif type(field_value) != field.type_ and field.auto_cast and field:
        value = field.type_(field_value)
    else:
        value = field_value
    return value


def _is_declared_instance(obj):
    return isinstance(obj, Declared)


def fields(class_or_instance):
    """Return a tuple describing the fields of this declared class.
    Accepts a declared class or an instance of one. Tuple elements are of
    type Field.
    """
    # Might it be worth caching this, per class?
    try:
        fields = getattr(class_or_instance, "fields")
        meta = getattr(class_or_instance, "meta")
        meta_vars = meta["vars"]
    except AttributeError or KeyError:
        raise TypeError('must be called with a declared type or instance')

    # Exclude pseudo-fields.  Note that fields is sorted by insertion
    # order, so the order of the tuple is as the fields were defined.
    out = []
    for f in fields:
        var: Var = meta_vars.get(f, None)
        if var:
            out.append(var)
    return tuple(out)


def _encode_json_type(value, default=_ExtendedEncoder().default):
    if isinstance(value, Json.__args__):
        return value
    return default(value)


def _encode_overrides(kvs, overrides, encode_json=False):
    override_kvs = {}
    for k, v in kvs.items():
        # if k in overrides:
        #     letter_case = overrides[k].letter_case
        #     original_key = k
        #     k = letter_case(k) if letter_case is not None else k

        #     encoder = overrides[original_key].encoder
        #     v = encoder(v) if encoder is not None else v

        if encode_json:
            v = _encode_json_type(v)
        override_kvs[k] = v
    return override_kvs


def _user_overrides(cls):
    overrides = {}
    return overrides


def _asdict(obj, encode_json=False, skip_none_field=False):
    if _is_declared_instance(obj):
        result = []
        field: Var
        for field in fields(obj):
            if field.ignore_serialize:
                continue

            field_value = obj.__dict__.get(field.name, MISSING)
            if field_value is MISSING:
                field_value = field.make_default()
                if field_value is MISSING:
                    if not field.required:
                        field_value = None
                    else:
                        raise AttributeError(f"field {field.name} is required.")

            if skip_none_field and field_value is None:
                continue

            value = _asdict(field_value, encode_json=encode_json, skip_none_field=skip_none_field)
            result.append((field.field_name, value))
        return _encode_overrides(dict(result), None, encode_json=encode_json)
    elif isinstance(obj, Mapping):
        return dict((_asdict(k, encode_json=encode_json), _asdict(v, encode_json=encode_json)) for k, v in obj.items())
    elif isinstance(obj, Collection) and not isinstance(obj, str):
        return list(_asdict(v, encode_json=encode_json) for v in obj)
    else:
        return copy.deepcopy(obj)


def _asxml(obj: dict, tag: str, attrib: Dict = {}) -> ET.Element:
    """
    :param obj: a dictionary object, root element children
    :tag str: root element tag name
    :param attrs: a dictionary object, root element attributes
    :return: ET.Element
    """
    root = ET.Element(tag, attrib)
    for k, v in obj.items():
        if isinstance(v, Dict):
            elem = _convert(k, v)
        else:
            elem = ET.Element(k)
            elem.text = v
        root.append(elem)
    return root


def _convert(key: str, obj: Dict) -> ET.ElementPath:
    if not isinstance(obj, Dict):
        raise TypeError('Only support dict type as element\'s attribute: %s (%s)' % (obj, type(obj).__name__))

    elem = ET.Element(key)
    for k, v in obj.items():
        # update attributes
        if v is None:
            pass
        elif not isinstance(v, Dict):
            elem.set(k, str(v))
        else:
            sub_elem = _convert(k, v)
            elem.append(sub_elem)
    return elem
