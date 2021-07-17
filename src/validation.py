from typing import Any, Callable, Dict, List, Tuple, Union, TypeVar, Generic
from dataclasses import dataclass
from json import loads
import unittest


T = TypeVar('T')
U = TypeVar('U')
Unknown = object
StringMap = Dict[str, T]
ErrorMap = StringMap[str]


@dataclass(frozen=True)
class Valid(Generic[T]):
    """
    Represents successfull validation of a value. Contains the valid value.
    """
    value: T


@dataclass(frozen=True)
class Invalid:
    """
    Represents unsuccessful validation of a value. Contains the reason for the value being invalid.
    """
    reason: Union[str, ErrorMap]


ValidationResult = Union[Valid[T], Invalid]
Validator = Callable[[Unknown], ValidationResult[T]]
InterfaceSpecification = StringMap[Validator[T]]
TaggedValidators = Dict[str, Validator[T]]


def validate_from_string(value: Union[str, bytes], validator: Validator[T]) -> ValidationResult[T]:
    """
    Validates a string with a validator by way of `loads`.

    :param value: The string to validate.
    :param validator: The validator to use.
    :return: The validation result.
    """
    try:
        value = loads(value)
    except ValueError:
        return Invalid('Invalid JSON')

    validation_result = validator(value)
    if isinstance(validation_result, Invalid):
        return validation_result

    return Valid(validation_result.value)


def validate_string(value: Unknown) -> ValidationResult[str]:
    """
    Validates a value as a `str`.
    """
    if isinstance(value, str):
        return Valid(value)
    elif isinstance(value, bytes):
        # decode a utf8 bytestring safely
        try:
            value = value.decode('utf-8')

            return Valid(value)
        except UnicodeDecodeError:
            return Invalid('Bytes invalid as utf-8 string')

    return Invalid(f'Value is not string: {value} ({type(value)})')


def validate_int(value: Unknown) -> ValidationResult[int]:
    """
    Validates a value as an integer. Note that boolean values are not counted as valid integers.
    """
    if isinstance(value, int) and not isinstance(value, bool):
        return Valid(value)

    return Invalid(f'Value is not int: {value} ({type(value)})')


def validate_float(value: Unknown) -> ValidationResult[float]:
    """
    Validates a value as a float.
    """
    if isinstance(value, float):
        return Valid(value)

    return Invalid(f'Value is not float: {value} ({type(value)})')


def validate_dict(value: Unknown,
                  validate_t: Validator[T],
                  validate_u: Validator[U]
                  ) -> ValidationResult[Dict[T, U]]:
    """
    Validates a value as a dict with type `T` for keys and `U` for values.
    """
    if not isinstance(value, dict):
        return Invalid(f'Expected dict, got: {value} ({type(value)})')

    errors = dict()
    new_value = dict()
    for key, value in value.items():
        key_validation_result = validate_t(key)
        if isinstance(key_validation_result, Invalid):
            errors[key] = key_validation_result
        else:
            value_validation_result = validate_u(value)
            if isinstance(value_validation_result, Invalid):
                errors[key] = value_validation_result
            else:
                new_value[key_validation_result.value] = value_validation_result.value

    # if the error dict has values, return them as part of an invalid result
    if len(errors) > 0:
        return Invalid(errors)

    return Valid(new_value)


def validate_string_map(value: Unknown, validator: Validator[T]) -> ValidationResult[StringMap[T]]:
    """
    Validates a value as a string map with value types `T`.
    """
    return validate_dict(value, validate_string, validator)


def validate_one_of_literals(value: Unknown, literals: List[T]) -> ValidationResult[T]:
    """
    Validates a value as one of the given literals.
    """
    # Loop through the literals. If the value is equal to one of them, return it as a valid result,
    # otherwise return an invalid result.
    for literal in literals:
        if value == literal:
            return Valid(value)
    return Invalid(f'Expected one of {literals}, got: {value} ({type(value)})')


def validate_one_of(value: Unknown, validators: List[Validator[T]]) -> ValidationResult[T]:
    """
    Validates a value as matching one of the given validators.
    """
    for validator in validators:
        validation_result = validator(value)
        if isinstance(validation_result, Valid):
            return validation_result

    validator_names = [v.__name__ for v in validators]

    return Invalid(f'Expected to match one of {validator_names}, got: {value} ({type(value)})')


def validate_unknown(value: Unknown) -> ValidationResult[Unknown]:
    """
    Validates a value as unknown. This is always a valid result.
    """
    return Valid(value)


def validate_interface(value: Unknown, interface: InterfaceSpecification) -> ValidationResult[T]:
    """
    Validates a value as matching a given interface specification.
    """
    value_as_string_map = validate_string_map(value, validate_unknown)
    if isinstance(value_as_string_map, Invalid):
        return value_as_string_map

    value_as_string_map = value_as_string_map.value
    errors = dict()
    new_value = dict()
    # iterate through the interface, validating each key exists and the value matches the validator
    for key, validator in interface.items():
        if key not in value_as_string_map:
            errors[key] = f'Missing key: {key}'
        else:
            validation_result = validator(value_as_string_map[key])
            if isinstance(validation_result, Invalid):
                errors[key] = validation_result
            else:
                new_value[key] = validation_result.value

    if len(errors) > 0:
        return Invalid(errors)

    return Valid(new_value)


def validate_with_type_tags(value: Unknown,
                            tag_field: str,
                            tagged_validators: TaggedValidators[T],
                            is_embedded=False
                            ) -> ValidationResult[T]:
    """
    Validates that a value has a tag field matching one of several tagged validators. If the tag
    field matches, the corresponding validator is also run either on the value itself or a 'data'
    field inside of it.
    """
    # Make sure that we have a `StringMap`
    as_string_map = validate_string_map(value, validate_unknown)
    if not isinstance(as_string_map, Valid):
        return as_string_map
    string_map = as_string_map.value

    # Make sure that the tag field exists
    if tag_field not in string_map:
        return Invalid(f'Missing tag field: {tag_field}')
    tag = string_map[tag_field]
    # If the tag doesn't match any of our tagged validators, we have an error
    if tag not in tagged_validators:
        valid_type_tags = [tag for tag in tagged_validators.keys()]

        return Invalid(f'Invalid tag: {tag}, expecting one of {valid_type_tags}')

    # Since our tag exists and matches one of our tagged validators, we can run the validator
    # on the value itself or on the data field inside of it
    validator = tagged_validators[tag]
    if not is_embedded:
        # If the data field doesn't exist, we have an invalid structure
        if 'data' not in string_map:
            return Invalid(f'Missing data field for non-embedded structure')

        return validator(string_map['data'])

    # Otherwise, we can run the validator on the entire string map
    return validator(string_map)


@dataclass(frozen=True)
class SomeType:
    some_field: str
    some_other_field: int


def validate_SomeType(value: Unknown) -> ValidationResult[SomeType]:
    """
    Validates a value as being of type `SomeType`
    """
    return validate_interface(value,
                              {'some_field': validate_string,
                                  'some_other_field': validate_int}
                              )


if __name__ == '__main__':
    print(validate_string(b'{"a": "b"}'))
    print(validate_string('{"a": "b"}'))
    print(validate_string('{"a": "b"}'.encode('utf-8')))
    print(validate_string(b'{"a": "b"}'.decode('utf-8')))
    print(validate_string(5))
    print(validate_string_map({"a": "b"}, validate_string))
    print(validate_string_map({1: "b"}, validate_string))
    print(validate_string_map({"a": 1}, validate_string))
    print(validate_dict({1: "b"}, validate_int, validate_string))
    print(validate_dict({"a": 1}, validate_string, validate_int))
    print(validate_one_of_literals(1, [1, 2, 3]))
    print(validate_one_of_literals(1, ["one", "two", "three"]))
    print(validate_one_of(1, [validate_string]))
    res = validate_one_of(
        1, [validate_string, validate_float, validate_int])
    print(res)
    print(validate_interface(1, {'a': validate_string}))
    print(validate_interface({'a': 'hullaballoo'}, {'a': validate_string}))
    print(validate_interface({'a': 'hullaballoo'}, {
          'ab': validate_string, 'bb': validate_string}))

    print(validate_with_type_tags(
        {'type': 'SomeType', 'some_field': 'hullaballoo', 'some_other_field': 1},
        'type',
        {'SomeType': validate_SomeType},
        is_embedded=True
    ))

    print(validate_with_type_tags(
        {'type': 'SomeTyp', 'some_field': 'hullaballoo', 'some_other_field': 1},
        'type',
        {'SomeType': validate_SomeType},
        is_embedded=True
    ))

    print(validate_with_type_tags(
        {'type': 'SomeType', 'some_field': 'hullaballoo'},
        'type',
        {'SomeType': validate_SomeType},
        is_embedded=True
    ))

    print(validate_with_type_tags(
        {'type': 'SomeType', 'data': {
            'some_field': 'hullaballoo', 'some_other_field': 1}},
        'type',
        {'SomeType': validate_SomeType},
        is_embedded=False
    ))

    print(validate_int(True))
