import copy
import inspect
import json
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import (Any, Callable, Collection, Dict, Mapping, Optional, Tuple, Type, Union)
from uuid import UUID

_REGISTER_DECLARED_CLASS: Dict[str, type] = {}


class _MISSING_TYPE:

    def __str__(self):
        return "MISSING"


MISSING = _MISSING_TYPE()
Json: Type[Any] = Union[dict, list, str, int, float, bool, None]
JsonData = Union[str, bytes, bytearray]


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
                 init=True):
        self._type = type_
        self.name = ""
        self._field_name = field_name
        self.default = default
        self.default_factory = default_factory
        self.required = required
        self.init = init
        self.ignore_serialize = ignore_serialize

    @property
    def field_name(self):
        if self._field_name is MISSING:
            return self.name
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
    return Var(type_, required, field_name, default, default_factory, ignore_serialize, init)


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
            field_value = kwargs.get(field.name, MISSING)

            # set `init` to False but `required` is True, that mean is this variable must be init in later
            # otherwise seiralize will be failed.
            # `init` just tell Declared class use custom initializer instead of default initializer.
            if field_value is MISSING:
                if not field.init:
                    continue
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
                *,
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
                  infer_missing=False,
                  skip_none_field=False,
                  **kw):
        kvs = json.loads(
            s, encoding=encoding, parse_float=parse_float, parse_int=parse_int, parse_constant=parse_constant, **kw)
        return cls.from_dict(kvs, infer_missing=infer_missing, skip_none_field=skip_none_field)

    @classmethod
    def from_dict(cls: Type['Declared'], kvs: dict, *, skip_none_field=False, infer_missing=False):
        return _decode_declared_class(cls, kvs, skip_none_field, infer_missing)

    def to_dict(self, encode_json=False, skip_none_field=False):
        return _asdict(self, encode_json=encode_json, skip_none_field=skip_none_field)

    @classmethod
    def from_form_data(cls: Type['Declared'], form_data, skip_none_field=False):
        if cls.has_nest_declared_class():
            raise ValueError("can't deserialize to nested declared class.")

        return cls.from_dict(dict(d.split("=") for d in form_data.split("&")), skip_none_field=skip_none_field)

    def to_form_data(self, skip_none_field=False):
        if self.has_nest_declared_class():
            raise ValueError("can't serialize with nested declared class.")

        return "&".join([f"{k}={v}" for k, v in self.to_dict(skip_none_field=skip_none_field).items()])

    @classmethod
    def from_xml(cls: Type['Declared'], xml_data, skip_none_field=False):
        raise NotImplementedError

    def to_xml(self, skip_none_field=False):
        raise NotImplementedError

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


def _decode_declared_class(cls: Type[Declared], kvs: dict, skip_none_field: bool, infer_missing: bool):
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
            if field_value is MISSING and skip_none_field:
                field_value = None
            value = field_value
        elif _issubclass_safe(field.type_, Declared):
            value = _decode_declared_class(field.type_, field_value, skip_none_field, infer_missing)
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
        else:
            value = field_value

        init_kwargs[field.name] = value

    return cls(**init_kwargs)


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
