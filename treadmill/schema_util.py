import enum
import functools
import typing
from datetime import datetime

import marshmallow
import marshmallow_enum

_MARSHMALLOW_FIELDS = {
    str: marshmallow.fields.String,
    int: marshmallow.fields.Integer,
    float: marshmallow.fields.Float,
    bool: marshmallow.fields.Boolean,
    datetime: marshmallow.fields.DateTime,
    dict: marshmallow.fields.Dict,
    enum.Enum: marshmallow_enum.EnumField
}


def _is_primitive(type_):
    global _MARSHMALLOW_FIELDS
    return issubclass(type_, tuple(_MARSHMALLOW_FIELDS.keys()))


def _get_marshmallow_field(type_):
    global _MARSHMALLOW_FIELDS
    field = next(_MARSHMALLOW_FIELDS.get(t)
                 for t in type_.mro()
                 if t in _MARSHMALLOW_FIELDS)
    if issubclass(type_, enum.Enum):
        field = functools.partial(field, type_, by_value=True)
    return field


def _is_typing_list(type_):
    return type_.__origin__ is typing.List


def _is_typing_optional(type_):
    return (
        type_.__origin__ is typing.Union and
        len(type_.__args__) == 2 and
        type(None) in type_.__args__
    )


def _is_typing_dict(type_):
    return type_.__origin__ is typing.Dict


# DataClass registry
_DATACLASSES = {}


class DataClassMeta(type):
    def __new__(mcs, typename, bases, ns):
        fields = {}
        field_defaults = {}
        for basecls in reversed(bases):
            if type(basecls) is DataClassMeta:
                fields.update(basecls._fields)
                field_defaults.update(basecls._field_defaults)
        annots = ns.get('__annotations__', {})
        fields.update(annots)
        for field_name in annots.keys():
            if field_name in ns:
                field_defaults[field_name] = ns[field_name]
        ns['_fields'] = fields
        ns['_field_defaults'] = field_defaults
        datacls = super().__new__(mcs, typename, bases, ns)

        if 'Meta' in ns and getattr(ns['Meta'], 'abstract', False):
            pass
        else:
            ns['__slots__'] = tuple(fields.keys())
            datacls = super().__new__(mcs, typename, bases, ns)
            _DATACLASSES[typename] = datacls

        return datacls


class DataClass(object, metaclass=DataClassMeta):
    """
    DataClass automatically defines __init__ instantiation and
    marshamallow schema from field annotation definition.
    """

    __schema__ = None
    _fields = None  # filled by DataClassMeta
    _field_defaults = None  # filled by DataClassMeta
    _all_fields = None
    _all_field_defaults = None

    class Meta:
        abstract = True

    def __init__(self, **kwargs):
        for field_name, field_type in self._fields.items():
            if field_name in kwargs:
                field_val = kwargs[field_name]
                setattr(self, field_name,
                        self._compose(field_type, field_val))

    def _compose(self, field_type, data):
        if _is_primitive(field_type):
            return data
        elif hasattr(field_type, '__origin__'):
            return self._compose_container(field_type, data)
        elif issubclass(field_type, DataClass):
            return self._compose_dataclass(field_type, data)
        raise TypeError('Unsupported type ' + str(field_type))

    def _compose_container(self, field_type, data):
        if _is_typing_list(field_type):
            return [self._compose(field_type.__args__[0], v) for v in data]
        elif _is_typing_optional(field_type):
            return self._compose(field_type.__args__[0], data)
        elif _is_typing_dict(field_type):
            assert field_type.__args__[0] == str, 'Only string key is allowed'
            return {k: self._compose(field_type.__args__[1], v)
                    for k, v in data.items()}
        raise TypeError('Unsupported type ' + str(field_type))

    def _compose_dataclass(self, field_type, data):
        assert isinstance(data, dict)
        return field_type(**data)

    @classmethod
    def schema(cls):
        if cls.__schema__ is None:
            schema_fields = {}
            for field_name, field_type in cls._fields.items():
                default_val = cls._field_defaults.get(field_name)
                schema_fields[field_name] = cls._marsh_field(field_type, default=default_val)
            cls.__schema__ = type(cls.__name__ + 'Schema', (marshmallow.Schema,), schema_fields)
        return cls.__schema__()

    @classmethod
    def _marsh_field(cls, field_type, optional=False, default=None):
        if _is_primitive(field_type):
            field = _get_marshmallow_field(field_type)
            return field(
                required=not optional,
                missing=default
            )
        elif hasattr(field_type, '__origin__'):
            return cls._marsh_container_field(field_type)
        elif issubclass(field_type, DataClass):
            return cls._marsh_nested_field(field_type)
        raise TypeError('Unsupported type ' + field_type)

    @classmethod
    def _marsh_container_field(cls, field_type):
        if _is_typing_list(field_type):
            list_arg_type = field_type.__args__[0]
            return marshmallow.fields.List(cls._marsh_field(list_arg_type))
        elif _is_typing_optional(field_type):
            arg_type = field_type.__args__[0]
            return cls._marsh_field(arg_type, optional=True)
        elif _is_typing_dict(field_type):
            key_type = field_type.__args__[0]
            value_type = field_type.__args__[1]
            assert key_type == str, 'Only string key is allowed'
            return marshmallow.fields.Dict(keys=cls._marsh_field(key_type),
                                           values=cls._marsh_field(value_type))
        raise TypeError('Unsupported type ' + field_type)

    def _marsh_nested_field(self, field_type):
        return marshmallow.fields.Nested(field_type.schema())