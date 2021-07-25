from typing import Callable, Dict, List, Optional, Union, TypeVar, Generic
from dataclasses import dataclass
import json
from enum import Enum


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
        value = json.loads(value)
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


def validate_bigint(value: Unknown) -> ValidationResult[int]:
    """
    Validates a value as a big integer. This means it may come in the form of an integer or a string.
    """
    if isinstance(value, int) and not isinstance(value, bool):
        return Valid(value)
    if isinstance(value, str):
        # If we can parse it as an integer it's valid
        try:
            value = int(value)
            return Valid(value)
        except ValueError:
            return Invalid(f'String value for bigint is not parsable as integer: {value}')
    return Invalid(f'Value is not valid big integer or parsable as one: {value} ({type(value)})')


def validate_float(value: Unknown) -> ValidationResult[float]:
    """
    Validates a value as a float.
    """
    if isinstance(value, float):
        return Valid(value)

    return Invalid(f'Value is not float: {value} ({type(value)})')


def validate_bool(value: Unknown) -> ValidationResult[bool]:
    """
    Validates a value as a boolean.
    """
    if isinstance(value, bool):
        return Valid(value)

    return Invalid(f'Value is not bool: {value} ({type(value)})')


def validate_literal(literal: T) -> Validator[T]:
    """
    Takes a literal value and creates a validator for it.
    """
    def validator(value: Unknown) -> Validator[T]:
        if value == literal:
            return Valid(literal)
        return Invalid(f'Value is not {literal}: {value} ({type(value)})')

    return validator


def validate_optional(validator: Validator[T]) -> Validator[Optional[T]]:
    """
    Takes a validator and creates a validator that will return `None` if the value is `None`.
    """
    def validate_OptionalT(value: Optional[T]) -> Validator[Optional[T]]:
        if value is None:
            return Valid(None)
        return validator(value)

    return validate_OptionalT


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
            errors[key] = key_validation_result.reason
        else:
            value_validation_result = validate_u(value)
            if isinstance(value_validation_result, Invalid):
                errors[key] = value_validation_result.reason
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


def validate_dict_of(validate_t: Validator[T],
                     validate_u: Validator[U]
                     ) -> Validator[Dict[T, U]]:
    """
    Takes a key validator and a value validator and creates a validator for a dict using them.
    """
    def validator(value: Unknown) -> Validator[Dict[T, U]]:
        if not isinstance(value, dict):
            return Invalid('Expected dict')
        new_value = dict()
        errors = dict()
        for key, value_u in value.items():
            key_validation_result = validate_t(key)
            value_validation_result = validate_u(value_u)
            if isinstance(key_validation_result, Invalid):
                errors[key] = key_validation_result.reason
                continue

            if isinstance(value_validation_result, Invalid):
                errors[key] = value_validation_result.reason
                continue

            new_value[key_validation_result.value] = value_validation_result.value

        if len(errors) > 0:
            return Invalid(errors)

        return Valid(new_value)

    return validator


def validate_string_map_of(validate_t: Validator[T]) -> Validator[StringMap[T]]:
    """
    Takes a value validator for `T` and creates a validator for a `StringMap[T]`.
    """
    return validate_dict_of(validate_string, validate_t)


def validate_list(validate_T: Validator[T]) -> Validator[List[T]]:
    """
    Takes a validator and creates a validator for a list of that type.
    """
    def validate_list_T(value: Unknown) -> Validator[List[T]]:
        if not isinstance(value, list):
            return Invalid(f'Expected list, got: {value} ({type(value)})')
        errors = dict()
        new_value = list()
        for i, item in enumerate(value):
            item_validation_result = validate_T(item)
            if isinstance(item_validation_result, Invalid):
                errors[str(i)] = item_validation_result.reason
            else:
                new_value.append(item_validation_result.value)

        if len(errors) > 0:
            return Invalid(errors)

        return Valid(new_value)

    return validate_list_T


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


def validate_interface(value: Unknown,
                       interface: InterfaceSpecification,
                       constructor: Callable[[Dict[str, Unknown]], T] = None
                       ) -> ValidationResult[T]:
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
            validation_result = validator(None)
            if isinstance(validation_result, Invalid):
                errors[key] = validation_result.reason
            else:
                new_value[key] = validation_result.value
        else:
            validation_result = validator(value_as_string_map[key])
            if isinstance(validation_result, Invalid):
                errors[key] = validation_result
            else:
                new_value[key] = validation_result.value

    if len(errors) > 0:
        return Invalid(errors)

    if constructor is not None:
        return Valid(constructor(**new_value))

    return Valid(new_value)


def validate_has_type_tag(value: Unknown,
                          tag_field: str,
                          type_tag: str) -> ValidationResult[StringMap[Unknown]]:
    """
    Validates a value as being a string map with a specific type tag.
    """
    as_string_map = validate_string_map(value, validate_unknown)
    if isinstance(as_string_map, Invalid):
        return as_string_map

    string_map = as_string_map.value
    if tag_field not in string_map:
        return Invalid(f'Missing tag field "{tag_field}"')
    tag = string_map[tag_field]
    if tag != type_tag:
        return Invalid(f'Expected tag "{type_tag}", got "{tag}"')
    return Valid(string_map)


def validate_with_type_tag_and_validator(value: Unknown,
                                         tag_field: str,
                                         type_tag: str,
                                         validator: Validator[U],
                                         constructor: Callable[[
                                             Dict[str, Unknown]], T]
                                         ) -> ValidationResult[T]:
    """
    Validates a value as being a string map with a specific type tag and validates the value with
    a given validator.
    """
    has_type_tag_result = validate_has_type_tag(value, tag_field, type_tag)
    if isinstance(has_type_tag_result, Invalid):
        return has_type_tag_result
    string_map = has_type_tag_result.value

    result = validator(string_map)
    if isinstance(result, Invalid):
        return result

    return Valid(constructor(**result.value))


def validate_with_type_tag(value: Unknown,
                           tag_field: str,
                           type_tag: str,
                           interface: InterfaceSpecification,
                           constructor: Callable[[Dict[str, Unknown]], T]
                           ) -> ValidationResult[T]:
    """
    Validates a value as matching a given interface specification and having a type tag. The type
    tag is removed from the result after validation.
    """
    # Check first for a valid type tag
    validation_result = validate_has_type_tag(value, tag_field, type_tag)
    if isinstance(validation_result, Invalid):
        return validation_result

    result = validate_interface(value, interface)
    if isinstance(result, Invalid):
        return result

    return Valid(constructor(**result.value))


def validate_with_type_tags(value: Unknown,
                            tag_field: str,
                            tagged_validators: TaggedValidators[T]
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
    validator = tagged_validators[tag]

    return validator(string_map)


def validate_enumeration_member(value: Unknown, enumeration: Enum) -> ValidationResult[Enum]:
    """
    Validates that a value is a member of an enumeration.
    """
    for member in enumeration:
        if value == member:
            return Valid(value)

    enumeration_values = [str(v) for v in enumeration]

    return Invalid(f'Expected one of {", ".join(enumeration_values)}, got: {value} ({type(value)})')
