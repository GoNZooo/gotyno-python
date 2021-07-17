from typing import Any, Callable, Dict, List, Union, TypeVar, Generic
from dataclasses import dataclass
from json import loads


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
    if (isinstance(validation_result, Invalid)):
        return validation_result

    return Valid(validation_result.value)


def validate_string(value: Unknown) -> ValidationResult[str]:
    """
    Validates a value as a `str`.
    """
    if (isinstance(value, str)):
        return Valid(value)
    elif (isinstance(value, bytes)):
        # decode a utf8 bytestring safely
        try:
            value = value.decode('utf-8')

            return Valid(value)
        except UnicodeDecodeError:
            return Invalid('Bytes invalid as utf-8 string')

    return Invalid(f'Value is not string {value} ({type(value)})')


def validate_integer(value: Unknown) -> ValidationResult[int]:
    """
    Validates a value as an integer.
    """
    if (isinstance(value, int)):
        return Valid(value)

    return Invalid(f'Value is not integer {value} ({type(value)})')


def validate_float(value: Unknown) -> ValidationResult[float]:
    """
    Validates a value as a float.
    """
    if (isinstance(value, float)):
        return Valid(value)

    return Invalid(f'Value is not float {value} ({type(value)})')


def validate_dict(value: Unknown, validate_t: Validator[T], validate_u: Validator[U]) -> ValidationResult[Dict[T, U]]:
    """
    Validates a value as a dict with type `T` for keys and `U` for values.
    """
    if (isinstance(value, dict)):
        errors = dict()
        new_value = dict()
        for key, value in value.items():
            key_validation_result = validate_t(key)
            if (isinstance(key_validation_result, Invalid)):
                errors[key] = key_validation_result
            else:
                value_validation_result = validate_u(value)
                if (isinstance(value_validation_result, Invalid)):
                    errors[key] = value_validation_result
                else:
                    new_value[key_validation_result.value] = value_validation_result.value

        # if the error dict has values, return invalid
        if (len(errors) > 0):
            return Invalid(errors)

        return Valid(new_value)
    else:
        return Invalid(f'Value is not dict: {value} ({type(value)})')


def validate_string_map(value: Unknown, validator: Validator[T]) -> ValidationResult[StringMap[T]]:
    """
    Validates a value as a string map with value types `T`.
    """
    return validate_dict(value, validate_string, validator)


def validate_one_of_literals(value: Unknown, literals: List[T]) -> ValidationResult[T]:
    """
    Validates a value as one of the given literals.
    """
    if (value in literals):
        return Valid(value)

    return Invalid(f'Expected one of {literals}, got: {value} ({type(value)})')


def validate_one_of(value: Unknown, validators: List[Validator[T]]) -> ValidationResult[T]:
    """
    Validates a value as one of the given validators.
    """
    for validator in validators:
        validation_result = validator(value)
        if (isinstance(validation_result, Valid)):
            return validation_result

    validator_names = [f'{v.__name__}' for v in validators]

    return Invalid(f'Expected to match one of {validator_names}, got: {value} ({type(value)})')


def validate_unknown(value: Unknown) -> ValidationResult[Unknown]:
    """
    Validates a value as unknown.
    """
    return Valid(value)


def validate_interface(value: Unknown, interface: InterfaceSpecification) -> ValidationResult[T]:
    """
    Validates a value as matching a given interface specification.
    """
    value_as_string_map = validate_string_map(value, validate_unknown)
    if (isinstance(value_as_string_map, Invalid)):
        return value_as_string_map

    value_as_string_map = value_as_string_map.value
    errors = dict()
    new_value = dict()
    # iterate through the interface, validating each key exists and the value matches the validator
    for key, validator in interface.items():
        if (key not in value_as_string_map):
            errors[key] = f'Missing key: {key}'
        else:
            validation_result = validator(value_as_string_map[key])
            if (isinstance(validation_result, Invalid)):
                errors[key] = validation_result
            else:
                new_value[key] = validation_result.value

    if (len(errors) > 0):
        return Invalid(errors)

    return Valid(new_value)


if __name__ == '__main__':
    print(validate_string(b'{"a": "b"}'))
    print(validate_string('{"a": "b"}'))
    print(validate_string('{"a": "b"}'.encode('utf-8')))
    print(validate_string(b'{"a": "b"}'.decode('utf-8')))
    print(validate_string(5))
    print(validate_string_map({"a": "b"}, validate_string))
    print(validate_string_map({1: "b"}, validate_string))
    print(validate_string_map({"a": 1}, validate_string))
    print(validate_dict({1: "b"}, validate_integer, validate_string))
    print(validate_dict({"a": 1}, validate_string, validate_integer))
    print(validate_one_of_literals(1, [1, 2, 3]))
    print(validate_one_of_literals(1, ["one", "two", "three"]))
    print(validate_one_of(1, [validate_string]))
    res = validate_one_of(
        1, [validate_string, validate_float, validate_integer])
    print(res)